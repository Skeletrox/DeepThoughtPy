from literal import Literal

class Sentence(object):
    """Sentence contains literals and connectors"""
    def __init__(self, inp : str, sNum : int):
        # Replace implication with #
        sent = inp.replace("=>", "#").strip()
        isImplication = sent.rfind("#") != -1
        sent = sent.split(" ")
        # Alternate to get literals
        self.literals = [Literal(l, sNum) for l in sent[::2]]
        # Alternate with one offset to get connectors
        self.connectors = [l for l in sent[1::2]]
        # If implication, convert to disjunction
        if isImplication:
            self.connectors[-1] = "|"
            for i in range(len(self.connectors) - 1):
                self.connectors[i] = "&" if self.connectors[i] == "|" else "|"
            for i in range(len(self.literals) - 1):
                self.literals[i].negate()

    def __str__(self):
        return "Literals: {}, connectors: {}".format([str(l) for l in self.literals], [c for c in self.connectors])