from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from config import VERIFY_TOKEN
from whatsapp.client import WhatsAppClient
from core.questions import QUESTOES
from logger import logger

router = APIRouter()

# Dicionário em memória para controlar usuários e progresso
USUARIOS_PROGRESSO = {}


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

        if "messages" in value:
            msg = value["messages"][0]
            usuario = msg["from"]

            # Identifica texto do usuário, seja text ou resposta interativa
            if msg["type"] == "text":
                texto = msg.get("text", {}).get("body", "")
            elif msg["type"] == "interactive":
                interactive = msg["interactive"]
                if interactive["type"] == "list_reply":
                    texto = interactive["list_reply"]["title"]
                elif interactive["type"] == "button_reply":
                    texto = interactive["button_reply"]["title"]
                else:
                    texto = "[Resposta interativa desconhecida]"
            else:
                texto = "[Tipo de mensagem não tratado]"

            logger.log_message(usuario, texto, "recebida")

            # Inicializa usuário se não existir
            if usuario not in USUARIOS_PROGRESSO:
                USUARIOS_PROGRESSO[usuario] = {
                    "perguntas_respondidas": [],
                    "pontuacao": 0,
                    "ultima_questao": None,
                    "apresentado": False
                }

            user_data = USUARIOS_PROGRESSO[usuario]

            # Primeira interação: apresenta o quiz
            if not user_data["apresentado"]:
                msg_intro = (
                    "Olá! Bem-vindo ao Quiz de Conhecimentos Gerais!\n\n"
                    "Você receberá perguntas de múltipla escolha.\n\n"
                    "Para receber a primeira pergunta, digite: 'quiz'"
                )
                WhatsAppClient.send_message({
                    "messaging_product": "whatsapp",
                    "to": usuario,
                    "type": "text",
                    "text": {"body": msg_intro}
                })
                logger.log_message(usuario, msg_intro, "enviada")
                user_data["apresentado"] = True
                return JSONResponse(content={"status": "ok"})

            # Inicia quiz ou envia próxima questão
            if texto.lower() == "quiz":
                # Envia a primeira questão que ainda não respondeu
                for q in QUESTOES:
                    if q.text not in user_data["perguntas_respondidas"]:
                        questao = q
                        break
                else:
                    msg_final = (
                        f"Você completou todas as questões! "
                        f"Pontuação: {user_data['pontuacao']}/{len(QUESTOES)}"
                    )
                    WhatsAppClient.send_message({
                        "messaging_product": "whatsapp",
                        "to": usuario,
                        "type": "text",
                        "text": {"body": msg_final}
                    })
                    logger.log_message(usuario, msg_final, "enviada")
                    questao = None

                if questao:
                    payload = questao.to_payload(usuario)
                    WhatsAppClient.send_message(payload)
                    logger.log_message(usuario, questao.text, "enviada")
                    user_data["ultima_questao"] = questao

            # Se houver uma última questão, verifica resposta do usuário
            elif user_data.get("ultima_questao"):
                ultima = user_data["ultima_questao"]
                resposta_usuario = texto.strip()
                acertou = False

                # Compara o texto enviado com a opção correta
                if hasattr(ultima, "options"):
                    if resposta_usuario.lower() == ultima.options[ultima.correct].lower():
                        acertou = True

                # Feedback
                if acertou:
                    user_data["pontuacao"] += 1
                    msg_feedback = "Correto!"
                else:
                    msg_feedback = (
                        f"Errado! A resposta correta era: {ultima.options[ultima.correct]}"
                    )

                # Mensagem de orientação para próxima questão
                msg_feedback += "\nPara receber a próxima pergunta, digite: 'quiz'"

                WhatsAppClient.send_message({
                    "messaging_product": "whatsapp",
                    "to": usuario,
                    "type": "text",
                    "text": {"body": msg_feedback}
                })
                logger.log_message(usuario, msg_feedback, "enviada")

                # Marca questão como respondida
                user_data["perguntas_respondidas"].append(ultima.text)
                user_data["ultima_questao"] = None

        else:
            logger.log_error("Evento sem campo 'messages'", contexto="receive_message")

    except Exception as e:
        logger.log_error(str(e), contexto="receive_message")

    return JSONResponse(content={"status": "ok"})
