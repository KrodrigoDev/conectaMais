## ConectaMais – Quiz via WhatsApp

### Estrutura do Projeto
````
conectaMais/
│── main.py                # Ponto de entrada da aplicação FastAPI
│── config.py              # Configurações (dotenv, constantes, tokens)
│── logger.py              # Logs de mensagens e erros
│
├── core/
│   ├── interfaces.py      # Interfaces/ABCs (ex: Questao)
│   └── factory.py         # Factory para criação de questões
│
├── questions/
│   ├── __init__.py
│   ├── multiple_choice.py # Questão de múltipla escolha
│   ├── true_false.py      # Questão verdadeiro/falso
│   └── ...                # Outras futuras (texto aberto, escala, etc.)
│
├── whatsapp/
│   ├── client.py          # Cliente para envio/recebimento via API WhatsApp
│   └── webhook.py         # Webhook FastAPI para receber mensagens
│
└── logs/
    ├── errors.log        # Registra os erros durante as conversas
    └── messages.log      # Registra todas as mensagens enviadas e recebidas

````


### Fluxo do Usuário – Quiz via WhatsApp
```` mermaid
flowchart TD
    A[Usuário envia qualquer mensagem] --> B[Mensagem de boas-vindas]
    B --> C["Digite 'quiz' para começar"]
    C --> D[Usuário digita 'quiz']
    D --> E[Bot envia primeira questão interativa]
    E --> F[Usuário seleciona resposta]
    F --> G[Bot verifica resposta e envia feedback]
    G --> H[Atualiza pontuação e marca questão respondida]
    H --> I{Mais questões?}
    I -- Sim --> D
    I -- Não --> J[Mensagem final com pontuação]


````

### Observações

- Todas as questões são criadas via Factory (`QuestaoFactory`) seguindo o padrão de projeto **Factory Method**.
- O progresso do usuário é inicialmente mantido em memória (`USUARIOS_PROGRESSO`), podendo futuramente ser salvo em banco de dados.
- Mensagens interativas usam a **API oficial do WhatsApp**, garantindo que o usuário clique nas opções em vez de digitar números.
- O projeto segue princípios **SOLID**, facilitando a adição de novos tipos de questões no futuro.
