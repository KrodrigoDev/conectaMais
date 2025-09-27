from core.factory import QuestaoFactory

# Lista de questões múltipla escolha
QUESTOES = [
    QuestaoFactory.criar(
        "multiple",
        text="Qual a capital do Brasil?",
        options=["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
        correct=2
    ),
    QuestaoFactory.criar(
        "multiple",
        text="Qual é o maior planeta do Sistema Solar?",
        options=["Terra", "Júpiter", "Saturno", "Marte"],
        correct=1
    ),
    QuestaoFactory.criar(
        "multiple",
        text="Qual animal é conhecido como o rei da selva?",
        options=["Leão", "Tigre", "Elefante", "Guepardo"],
        correct=0
    ),
    QuestaoFactory.criar(
        "multiple",
        text="Qual é a cor resultante da mistura de azul e amarelo?",
        options=["Verde", "Roxo", "Laranja", "Marrom"],
        correct=0
    )
]
