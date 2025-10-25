from core.factory import QuestaoFactory

# Lista de questões múltipla escolha
QUESTOES = [

    QuestaoFactory.criar(
        tipo='image',
        text="🖼️ Qual desses é um gato?",
        image_url="https://http.cat/images/102.jpg",
        options=["🐶", "🐱"],
        correct=1
    ),

    QuestaoFactory.criar(
        "multiple",
        text="Qual a capital do Brasil?",
        options=["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
        correct=2
    ),

    QuestaoFactory.criar(
        'multiple',
        text='☀️ O sol aparece de dia.',
        options=["Verdadeiro", "Falso"],
        correct=0
    ),
    QuestaoFactory.criar(
        "multiple",
        text="Qual é o maior planeta do Sistema Solar?",
        options=["Terra", "Júpiter", "Saturno", "Marte"],
        correct=1
    ),

    QuestaoFactory.criar(
        tipo='image',
        text="🖼️ Quantos gatos existem na foto?",
        image_url="https://http.cat/images/409.jpg",
        options=["1️⃣", "2️⃣", "3️⃣"],
        correct=1
    ),

    QuestaoFactory.criar(
        "multiple",
        text="🚦 Qual cor significa 'Pare'?",
        options=["🟢 Verde", "🟡 Amarelo", "🔴 Vermelho"],
        correct=2
    ),
    QuestaoFactory.criar(
        "multiple",
        text="🐾 Qual desses é um animal?",
        options=["🚲 Bicicleta", "🐶 Cachorro", "🍯 Mel"],
        correct=1
    ),
    QuestaoFactory.criar(
        "multiple",
        text="🍎 Qual dessas é uma fruta?",
        options=["🍞 Pão", "🍎 Maçã", "🐟 Peixe"],
        correct=1
    )

]
