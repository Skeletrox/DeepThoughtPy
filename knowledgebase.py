from sentence import Sentence
from literal import Literal
from copy import deepcopy

class KnowledgeBase(object):
    """KnowledgeBase is a collection of sentences, the known truths"""
    def __init__(self, inputs):
        self.literalMap = {}
        self.sentences = []
        for i in range(len(inputs)):
            s = Sentence(inputs[i])
            for lit in s.literals:
                self.literalMap[(lit.identifier, lit.litType)] = self.literalMap.get((lit.identifier, lit.litType), []) + [i]

            self.sentences.append(s)


    def __str__(self):
        return "\n".join([str(s) for s in self.sentences])


    def getProofByResolution(self, l : Literal):
        l.negate() # Negate the literal!
        inputLiterals = [l]
        literalCopy = deepcopy(self.literalMap)
        sentenceCopy = deepcopy(self.sentences)
        alreadySelected = {}
        while True:            
            # Iterate though all input literals to get the best matching sentence in KB
            sentenceCountMap = {}
            bestSentence = -1
            for inlit in inputLiterals:
                key = (inlit.identifier, inlit.litType)
                locations = literalCopy.get(key, [])
                for loc in locations:
                    sentence = sentenceCopy[loc]
                    literals = sentence.literals
                    for lit in literals:
                        if (lit.identifier, lit.litType) == key and lit.canBeResolvedBy(inlit) and lit.negated != inlit.negated:
                            # These can be resolved
                            sentenceCountMap[loc] = sentenceCountMap.get(loc, 0) + 1
                            if sentenceCountMap[loc] > sentenceCountMap.get(bestSentence, -1) and alreadySelected.get(loc, None) is None:
                                bestSentence = loc
                            break

            # There is no sentence with at least one of the appropriate literals
            if bestSentence == -1:
                return False

            # Convert literal to key
            neededSentence = sentenceCopy[bestSentence]
            inputLiterals = getResolution(neededSentence, inputLiterals)
            if len(inputLiterals) == 0:
                return True
            # print([str(i) for i in inputLiterals])

def getResolution(sentence : Sentence, lits : list):
    literals = sentence.literals
    unification = {}
    removableLits = []
    for l in lits:
        # For each literal, find the corresponding location and unify
        key = (l.identifier, l.litType)
        # This is a conjunction of iterals
        position = -1
        for i in range(len(literals)):
            if (literals[i].identifier, literals[i].litType) == key:
                position = i
                break

        if position != -1:
            unification.update(getUnification(literals[position], l))
            literals.pop(position)
            removableLits.append(l)
        if len(literals) == 0:
            break
        

    lits = [l for l in lits if l not in removableLits]
    for i in range(len(literals)):
        literals[i] = substitute(literals[i], unification)

    for i in range(len(lits)):
        lits[i] = substitute(lits[i], unification)
    literals.extend(lits)
    return literals


def getUnification(original : Literal, new : Literal):
    if original.litType != 'P' and new.litType != 'P':
        return {(original.identifier, original.litType): (new.identifier, new.litType)}
    returnable = {}
    for i in range(len(original.args)):
        returnable.update(getUnification(original.args[i], new.args[i]))

    return returnable


def substitute(lit : Literal, unification : dict):
    if lit.litType != 'P':
        # If the unification does not contain this identifier, then just return this
        lit.identifier, lit.litType = unification.get((lit.identifier, lit.litType), (lit.identifier, lit.litType))
        return lit

    for i in range(len(lit.args)):
        lit.args[i] = substitute(lit.args[i], unification)

    return lit