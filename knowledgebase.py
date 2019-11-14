from .sentence import Sentence

class KnowledgeBase(object):
    """KnowledgeBase is a collection of sentences"""
    def __init__(self, inputs : List[str]):
        self.literalMap = {}
        self.sentences = []
        for i in range(len(inputs)):
            s = Sentence(inputs[i])
            for lit in s.literals:
                self.literalMap[(lit.identifer, lit.litType)] = self.literalMap.get((lit.identifer, lit.litType), []) + i

            self.sentences.append(s)

