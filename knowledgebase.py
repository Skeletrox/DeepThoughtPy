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
        literalCopy = deepcopy(self.literalMap)
        sentenceCopy = deepcopy(self.sentences)
        while True:
            
            # Convert literal to key
            key = (l.identifier, l.litType)
            locations = literalCopy.get(key, [])
            
            neededSentence = None
            for loc in locations:
                sentence = sentenceCopy[loc]
                literals = sentence.literals
                for lit in literals:
                    if (lit.identifier, lit.litType) == key and lit.canBeResolvedBy(l) and lit.negated != l.negated:
                        # These can be resolved
                        
                        neededSentence = sentence                
                        break
                if neededSentence is not None:
                    literalCopy[key].remove(loc) # We shall ignore this line now, because it has already been chosen
                    break

            if neededSentence is None: # This literal does not exist in the knowledge base | No further substitutions are possible
                return False
            result = getResolution(neededSentence, l)

            if result is None: # We ended up with a contradiction, so this is true
                return True
            l = result[0]
            



def getResolution(sentence : Sentence, l : Literal):
    literals = sentence.literals
    key = (l.identifier, l.litType)
    # This is a conjunction of iterals
    position = -1
    for i in range(len(literals)):
        if (literals[i].identifier, literals[i].litType) == key:
            position = i
            break

    if position == -1:
        return None
    
    unification = getUnification(literals[position], l)
    literals.pop(position)
    if len(literals) == 0:
        return None
    for i in range(len(literals)):
        literals[i] = substitute(literals[i], unification)

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