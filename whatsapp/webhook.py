from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import date
from config import VERIFY_TOKEN
from whatsapp.client import WhatsAppClient
from core.questions import QUESTOES
from logger import logger
from data import carregar_progresso, salvar_progresso, criar_usuario

router = APIRouter()

# Dicionário em memória para armazenar progresso
USUARIOS_PROGRESSO = {}
carregar_progresso(USUARIOS_PROGRESSO)


# ----------------------------
# Funções auxiliares
# ----------------------------
def extrair_texto(msg: dict) -> str:
    """Extrai texto de mensagens comuns e interativas do WhatsApp."""
    if msg["type"] == "text":
        return msg.get("text", {}).get("body", "")
    elif msg["type"] == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "list_reply":
            return interactive["list_reply"]["title"]
        elif interactive["type"] == "button_reply":
            return interactive["button_reply"]["title"]
    return "[Tipo de mensagem não tratado]"


def gerar_id_usuario(usuario: str, progresso_usuarios: dict) -> str:
    """Gera um novo ID no formato <usuario>_<data>_<número_tentativa>"""
    data_atual = str(date.today())
    tentativas_existentes = [
        uid for uid in progresso_usuarios.keys()
        if uid.startswith(f"{usuario}_{data_atual}")
    ]
    if tentativas_existentes:
        ultima_tentativa = max(int(uid.split("_")[-1]) for uid in tentativas_existentes)
        nova_tentativa = ultima_tentativa + 1
    else:
        nova_tentativa = 0
    return f"{usuario}_{data_atual}_{nova_tentativa}"


# ----------------------------
# Rotas Webhook
# ----------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)))
    return JSONResponse(content="Erro: token inválido", status_code=403)


@router.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        if "messages" not in value:
            logger.log_error("Evento sem campo 'messages'", contexto="receive_message")
            return JSONResponse(content={"status": "ok"})

        msg = value["messages"][0]
        usuario = msg["from"]
        texto = extrair_texto(msg).lower().strip()
        logger.log_message(usuario, texto, "recebida")

        # --- Buscar ou criar usuário ---
        id_usuario = gerar_id_usuario(usuario, USUARIOS_PROGRESSO)  # pega o último ou cria novo
        ids_atuais = [uid for uid in USUARIOS_PROGRESSO if uid.startswith(f"{usuario}_{date.today()}")]

        if ids_atuais:
            # Mantém o último id do dia (tentativa mais recente)
            id_usuario = sorted(ids_atuais, key=lambda uid: int(uid.split("_")[-1]))[-1]

        else:
            id_usuario = f"{usuario}_{date.today()}_0"

        user_data = USUARIOS_PROGRESSO.get(id_usuario)

        if not user_data:
            user_data = criar_usuario(id_usuario=id_usuario, progresso_usuarios=USUARIOS_PROGRESSO)

        tentativa = int(id_usuario.split("_")[-1])
        user_data["tentativa"] = tentativa

        # ---------------------------------
        # Reiniciar quiz (apenas se a atual estiver finalizada)
        # ---------------------------------
        if texto == "sim, reiniciar" and user_data.get("finalizado"):
            novo_id = gerar_id_usuario(usuario, USUARIOS_PROGRESSO)
            novo_user_data = criar_usuario(id_usuario=novo_id, progresso_usuarios=USUARIOS_PROGRESSO)
            tentativa = int(novo_id.split("_")[-1])

            novo_user_data["apresentado"] = True
            # Atualiza o dicionário principal com o novo progresso
            USUARIOS_PROGRESSO[novo_id] = novo_user_data

            WhatsAppClient.send_message(
                to=usuario,
                text=f"🔄 Iniciando nova tentativa ({tentativa}) do quiz!",
                is_questao=False
            )

            # Envia imediatamente a introdução novamente
            WhatsAppClient.send_message(
                to=usuario,
                text="Olá novamente! 👋\nBem-vindo à sua nova tentativa do *Quiz de Conhecimentos Gerais!* 🧠",
                is_questao=False
            )
            WhatsAppClient.send_button_message(
                usuario,
                "Aperte em iniciar para começar",
                [{"id": "iniciar", "title": "iniciar"}]
            )

            salvar_progresso(USUARIOS_PROGRESSO)
            return JSONResponse(content={"status": "ok"})

        # ---------------------------------
        # Caso o usuário já tenha finalizado
        # ---------------------------------
        if user_data.get("finalizado"):
            WhatsAppClient.send_button_message(
                to=usuario,
                body_text=f"Você já completou o quiz de hoje na tentativa {tentativa}. Deseja tentar novamente?",
                buttons=[{"id": "Sim, reiniciar", "title": "Sim, reiniciar"}]
            )
            return JSONResponse(content={"status": "ok"})

        # ---------------------------------
        # Mensagem inicial
        # ---------------------------------
        if not user_data["apresentado"]:
            WhatsAppClient.send_message(
                to=usuario,
                text="Olá! 👋 Bem-vindo ao *Quiz de Conhecimentos Gerais!* 🧠\n\n"
                     "Você receberá perguntas de múltipla escolha.",
                is_questao=False
            )
            user_data["apresentado"] = True
            WhatsAppClient.send_button_message(
                usuario,
                "Aperte em iniciar para começar",
                [{"id": "iniciar", "title": "iniciar"}]
            )
            salvar_progresso(USUARIOS_PROGRESSO)
            return JSONResponse(content={"status": "ok"})

        # ---------------------------------
        # Iniciar / continuar quiz
        # ---------------------------------
        if texto in ["iniciar", "continuar"]:
            for q in QUESTOES:
                if q.text not in user_data["perguntas_respondidas"]:
                    questao = q
                    break
            else:
                # Todas respondidas
                user_data["finalizado"] = True
                WhatsAppClient.send_message(
                    to=usuario,
                    text=f"🎉 Você completou todas as questões!\n"
                         f"Pontuação final: {user_data['pontuacao']}/{len(QUESTOES)}",
                    is_questao=False
                )
                WhatsAppClient.send_button_message(
                    usuario,
                    "Deseja tentar novamente?",
                    [{"id": "Sim, reiniciar", "title": "Sim, reiniciar"}]
                )
                salvar_progresso(USUARIOS_PROGRESSO)
                return JSONResponse(content={"status": "ok"})

            # Enviar próxima questão
            payload = questao.to_payload(usuario)
            WhatsAppClient.send_message(payload=payload, is_questao=True)
            user_data["ultima_questao"] = questao
            salvar_progresso(USUARIOS_PROGRESSO)
            return JSONResponse(content={"status": "ok"})

        # ---------------------------------
        # Avaliar resposta
        # ---------------------------------
        if user_data.get("ultima_questao"):
            ultima = user_data["ultima_questao"]
            acertou = (
                hasattr(ultima, "options")
                and texto == ultima.options[ultima.correct].lower()
            )

            msg_feedback = "✅ Correto!" if acertou else f"❌ Errado! A resposta correta era: {ultima.options[ultima.correct]}"
            if acertou:
                user_data["pontuacao"] += 1

            user_data["perguntas_respondidas"].append(ultima.text)
            user_data["ultima_questao"] = None

            WhatsAppClient.send_message(to=usuario, text=msg_feedback, is_questao=False)
            WhatsAppClient.send_button_message(
                usuario,
                "Aperte em continuar para seguir",
                [{"id": "continuar", "title": "continuar"}]
            )

            salvar_progresso(USUARIOS_PROGRESSO)

    except Exception as e:
        logger.log_error(str(e), contexto="receive_message")

    return JSONResponse(content={"status": "ok"})
