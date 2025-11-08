import pandas as pd
from pathlib import Path
from logger import logger

# Caminho para armazenar o progresso dos usuários
PATH_DADOS = Path('../conectaMais/logs') / "dados.csv"


def criar_usuario(progresso_usuarios: dict, id_usuario: str) -> dict:
    """Cria um novo usuário com base no ID gerado (<usuario>_<data>_<tentativa>)."""
    tentativa = int(id_usuario.split("_")[-1])

    progresso_usuarios[id_usuario] = {
        "id": id_usuario,
        "tentativa": tentativa,
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
        try:
            df = pd.read_csv(PATH_DADOS, sep=';')
            for _, row in df.iterrows():
                progresso_usuarios[row["id"]] = {
                    "id": row["id"],
                    "tentativa": int(row.get("tentativa", 0)),
                    "perguntas_respondidas": eval(row["perguntas_respondidas"]),
                    "pontuacao": int(row["pontuacao"]),
                    "ultima_questao": None,  # Não persiste o objeto questão
                    "apresentado": bool(row["apresentado"]),
                    "finalizado": bool(row["finalizado"]),
                }
            logger.log_message("sistema", f"{len(df)} registros carregados de {PATH_DADOS}", "sistema")
        except Exception as e:
            logger.log_error(f"Erro ao carregar progresso: {e}", contexto="carregar_progresso")


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
                "tentativa": dados.get("tentativa", 0),
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
