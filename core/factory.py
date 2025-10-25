from questions.multiple_choice import MultiplaEscolha
from questions.true_false import VerdadeiroFalso
from questions.image_choice import ImageChoice


class QuestaoFactory:
    @staticmethod
    def criar(tipo: str, **kwargs):
        if tipo == "multiple":
            return MultiplaEscolha(**kwargs)
        elif tipo == "truefalse":
            return VerdadeiroFalso(**kwargs)
        elif tipo == 'image':
            return ImageChoice(**kwargs)
        else:
            raise ValueError(f"Tipo de pergunta desconhecido: {tipo}")
