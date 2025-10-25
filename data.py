import pandas as pd
from pathlib import Path

from logger import logger

# Caminho para armazenar o progresso dos usuários
PATH_DADOS = Path('../conectaMais/logs') / "dados.csv"


def criar_usuario(progresso_usuarios: dict, id_usuario: str) -> dict:
    progresso_usuarios[id_usuario] = {
        "id": id_usuario,
        "perguntas_respondidas": [],
        "pontuacao": 0,
        "ultima_questao": None,
        "apresentado": False,
        "finalizado": False
    }
    salvar_progresso(progresso_usuarios)
    return progresso_usuarios[id_usuario]


def carregar_progresso(progresso_usuarios: dict):
    """Carrega o progresso salvo no CSV para a memória."""
    if PATH_DADOS.exists():
        df = pd.read_csv(PATH_DADOS, sep=';')
        for _, row in df.iterrows():
            progresso_usuarios[row["id"]] = {
                "id": row["id"],
                "perguntas_respondidas": eval(row["perguntas_respondidas"]),
                "pontuacao": row["pontuacao"],
                "ultima_questao": None,  # Não persiste o objeto questão
                "apresentado": row["apresentado"],
                "finalizado": row["finalizado"],
            }


def salvar_progresso(progresso_usuarios: dict):
    """Salva o progresso atual de todos os usuários no CSV."""
    try:
        PATH_DADOS.parent.mkdir(parents=True, exist_ok=True)

        if not progresso_usuarios:
            logger.log_error("Nenhum dado para salvar — dicionário vazio.", contexto="salvar_progresso")
            return

        registros = []
        for usuario, dados in progresso_usuarios.items():
            registros.append({
                "id": dados["id"],
                "perguntas_respondidas": str(dados["perguntas_respondidas"]),
                "pontuacao": dados["pontuacao"],
                "apresentado": dados["apresentado"],
                "finalizado": dados["finalizado"]
            })

        df = pd.DataFrame(registros)
        df.to_csv(PATH_DADOS, index=False, sep=';')

        logger.log_message("sistema", f"Progresso salvo em {PATH_DADOS} ({len(df)} registros).", "sistema")

    except Exception as e:
        logger.log_error(f"Erro ao salvar progresso: {e}", contexto="salvar_progresso")
