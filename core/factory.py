from questions.multiple_choice import MultiplaEscolha
from questions.true_false import VerdadeiroFalso


class QuestaoFactory:
    @staticmethod
    def criar(tipo: str, **kwargs):
        if tipo == "multiple":
            return MultiplaEscolha(**kwargs)
        elif tipo == "truefalse":
            return VerdadeiroFalso(**kwargs)
        else:
            raise ValueError(f"Tipo de pergunta desconhecido: {tipo}")
