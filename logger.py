import logging
from pathlib import Path

LOG_DIR = Path("../conectaMais/logs")
LOG_DIR.mkdir(exist_ok=True)


class Logger:
    def __init__(self):
        # Log geral (mensagens)
        self.message_logger = logging.getLogger("messages")
        self.message_logger.setLevel(logging.INFO)
        fh_messages = logging.FileHandler(LOG_DIR / "messages.log")
        fh_messages.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.message_logger.addHandler(fh_messages)

        # Log de erros
        self.error_logger = logging.getLogger("errors")
        self.error_logger.setLevel(logging.ERROR)
        fh_errors = logging.FileHandler(LOG_DIR / "errors.log")
        fh_errors.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.error_logger.addHandler(fh_errors)

    def log_message(self, usuario: str, mensagem: str, direcao: str):
        """
        usuario: número ou identificador do usuário
        mensagem: texto trocado
        direcao: 'enviada' ou 'recebida'
        """

        log_entry = f"[{direcao.upper()}] Usuário: {usuario} | Mensagem: {mensagem}"

        self.message_logger.info(log_entry)

    def log_error(self, erro: str, contexto: str = ""):
        """
        erro: mensagem de erro
        contexto: parte do código onde aconteceu
        """
        log_entry = f"{erro} | Contexto: {contexto}"
        self.error_logger.error(log_entry)


# Instância global (para reuso em todo projeto)
logger = Logger()
