from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import date

from config import VERIFY_TOKEN
from whatsapp.client import WhatsAppClient
from core.questions import QUESTOES
from logger import logger
from data import carregar_progresso, salvar_progresso, criar_usuario

router = APIRouter()

# Dicionário em memória para controlar progresso
USUARIOS_PROGRESSO = {}

# Carrega dados existentes ao iniciar o servidor
carregar_progresso(USUARIOS_PROGRESSO)


# ----------------------------
# Funções auxiliares
# ----------------------------
def extrair_texto(msg: dict) -> str:
    if msg["type"] == "text":
        return msg.get("text", {}).get("body", "")
    elif msg["type"] == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "list_reply":
            return interactive["list_reply"]["title"]
        elif interactive["type"] == "button_reply":
            return interactive["button_reply"]["title"]
        else:
            return "[Resposta interativa desconhecida]"
    else:
        return "[Tipo de mensagem não tratado]"


# ----------------------------
# Webhook
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
        id_usuario = f"{usuario}_{date.today()}"

        texto = extrair_texto(msg).lower()
        logger.log_message(usuario, texto, "recebida")

        user_data = USUARIOS_PROGRESSO.get(id_usuario) or criar_usuario(id_usuario=id_usuario,
                                                                        progresso_usuarios=USUARIOS_PROGRESSO)

        # ----------------------------
        # Bloqueio se o usuário já finalizou hoje
        # ----------------------------
        if user_data.get("finalizado"):
            WhatsAppClient.send_message(
                to=usuario,
                text="Você já respondeu todas as questões do dia de hoje. "
                     "Para responder novas questões, volte amanhã!",
                is_questao=False
            )
            return JSONResponse(content={"status": "ok"})

        # ----------------------------
        # Boas-vindas
        # ----------------------------
        if not user_data["apresentado"]:
            WhatsAppClient.send_message(
                to=usuario,
                text="Olá! Bem-vindo ao Quiz de Conhecimentos Gerais!\n\n"
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

        # ----------------------------
        # Iniciar / continuar quiz
        # ----------------------------
        if texto in ["iniciar", "continuar"]:
            for q in QUESTOES:
                if q.text not in user_data["perguntas_respondidas"]:
                    questao = q
                    break
            else:
                # Todas as questões respondidas
                user_data["finalizado"] = True
                WhatsAppClient.send_message(
                    to=usuario,
                    text=f"Você completou todas as questões! Pontuação final: {user_data['pontuacao']}/{len(QUESTOES)}",
                    is_questao=False
                )
                salvar_progresso(USUARIOS_PROGRESSO)
                return JSONResponse(content={"status": "ok"})

            payload = questao.to_payload(usuario)
            WhatsAppClient.send_message(payload=payload, is_questao=True)

            user_data["ultima_questao"] = questao
            salvar_progresso(USUARIOS_PROGRESSO)
            return JSONResponse(content={"status": "ok"})

        # ----------------------------
        # Avaliar resposta à última questão
        # ----------------------------
        if user_data.get("ultima_questao"):
            ultima = user_data["ultima_questao"]
            acertou = hasattr(ultima, "options") and texto == ultima.options[ultima.correct].lower()

            msg_feedback = "Correto!" if acertou else f"Errado! A resposta correta era: {ultima.options[ultima.correct]}"
            if acertou:
                user_data["pontuacao"] += 1

            user_data["perguntas_respondidas"].append(ultima.text)
            user_data["ultima_questao"] = None
            WhatsAppClient.send_message(to=usuario, text=msg_feedback, is_questao=False)

            WhatsAppClient.send_button_message(usuario, "Aperte em continuar para receber uma nova questão",
                                               [{"id": "continuar", "title": "continuar"}])

            salvar_progresso(USUARIOS_PROGRESSO)

    except Exception as e:
        logger.log_error(str(e), contexto="receive_message")

    return JSONResponse(content={"status": "ok"})
