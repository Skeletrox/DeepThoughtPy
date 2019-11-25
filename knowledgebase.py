from sentence import Sentence
from literal import Literal
from copy import deepcopy
from typing import List

class KnowledgeBase(object):
    """KnowledgeBase is a collection of sentences, the known truths"""
    def __init__(self, inputs):
        self.literalMap = {}
        self.sentences = []
        for i in range(len(inputs)):
            s = Sentence(inputs[i], i)
            for lit in s.literals:
                self.literalMap[lit] = self.literalMap.get(lit, []) + [i]
                # self.literalMap[(lit.identifier, lit.litType)].update({i : True})

            self.sentences.append(s)


    def __str__(self):
        return "\n".join([str(s) for s in self.sentences])


    def proveByResolution2(self, inputs : List[Literal], ignore=0):
        if len(inputs) == 0:
            return True
        sentenceLocs = []
        sentenceLocBitMap = 0 # Maximum 100 bits
        for i in inputs:
            # print("Current Input in pBR2: ", i)
            # key = (i.identifier, i.litType)
            locations = self.literalMap.get(i, [])
            chosen = []
            for l in locations:
                # print("Looking at:", l)
                # Ensure this is not already in chosen locations, or being ignored
                # The ith bit is set, then the ith sentence was already chosen
                # If the ith bit of ignore was set, then the ith sentence is being ignored 
                if sentenceLocBitMap >> l & 1 == 0 and ignore >> l & 1 == 0:
                    sentenceLocs.append(l)
                    sentenceLocBitMap |= 1 << l
                    chosen.append(l)
            # print("Chosen sentences: ", chosen)
            for l in chosen:
                if sentenceLocBitMap >> l & 1 == 0 and ignore >> l & 1 == 0:
                    sentenceLocs.append(l)
                    sentenceLocBitMap |= 1 << l

        for l in sentenceLocs:
            # print("Now trying sentence", self.sentences[l], "for literal", str(i))
            currSentence = deepcopy(self.sentences[l])
            newIgnore = ignore | 1 << l
            result = self.getResolution2(currSentence, deepcopy(inputs), newIgnore)
            if result:
                return True

        return False


    def getResolution2(self, sentence : Sentence, inputs : List[int], ignore : int):
        if len(inputs) == 0:
            return True
        literals = sentence.literals
        # print("GR2 Literals:", [str(l) for l in literals])
        # print("GR2 Inputs:", [str(i) for i in inputs])
        unification = {}
        unifiables = {}
        for i in inputs:
            for l in literals:
                if i.canBeResolvedBy(l) or l.canBeResolvedBy(i):
                    # print("{} and {} can resolve.".format(i, l))
                    unifiables[(i.identifier, i.litType, i.negated)] = unifiables.get((i.identifier, i.litType, i.negated), []) + [l]
        for i in inputs:
            # print("GR2 input before res:", i)
            # print("Unifiables: ", unifiables)
            currLitUnifi = unifiables.get((i.identifier, i.litType, i.negated), None)
            if not currLitUnifi:
                # No literal can unify with this one
                continue
            l = currLitUnifi.pop()
            # print(i, l)
            result = getUnification(l, i)
            # If l already resolves to another variable that can resolve to i, then generalize
            for (key, val) in result.items():
                res = unification.get(key, None)
                # print("Res:", res)
                # print(unification)
                if res is not None:
                    # Another unification exists for this variable, see if the other unifier can also do this
                    if val.canBeResolvedBy(res):
                        # The older unification is a better choice than the new one
                        # Set the result for the new one to the old one
                        unification[val] = res
                    elif res.canBeResolvedBy(val):
                        # The newer unification is a better choice than the old one
                        # Set the result for the old one to the new one
                        unification[res] = val
                        unification[key] = val;
                    else:
                        return False
                else:
                    # Result is none anyway, so just add this
                    unification[key] = val

            # Substitute all literals in appropriate locations
            for i in range(len(literals)):
                literals[i] = substitute(literals[i], unification)
            for i in range(len(inputs)):
                inputs[i] = substitute(inputs[i], unification)

            # Purge negating, common literals
            newSentence = purgeCommon(literals, inputs)
            # print("New sentence:", [str(i) for i in newSentence])
            # Try to prove this by resolution next
            result = self.proveByResolution2(newSentence, ignore)
            if result:
                return True
        return False


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
                        if (lit.identifier, lit.litType) == key and (lit.canBeResolvedBy(inlit) or inlit.canBeResolvedBy(lit)) and lit.negated != inlit.negated:
                            # These can be resolved
                            sentenceCountMap[loc] = sentenceCountMap.get(loc, 0) + 1
                            if sentenceCountMap[loc] > sentenceCountMap.get(bestSentence, -1):
                                bestSentence = loc
                            break

            # There is no sentence with at least one of the appropriate literals
            if bestSentence == -1:
                return False

            neededSentence = sentenceCopy[bestSentence]
            inputLiterals = getResolution(neededSentence, inputLiterals)
            if len(inputLiterals) == 0:
                self.sentences.append(Sentence(str(l)))
                self.literalMap[(l.identifier, l.litType)] = self.literalMap.get((l.identifier, l.litType), []) + [len(self.sentences) - 1]
                return True
            # print([str(i) for i in inputLiterals]) # For debug purposes

def getResolution(sentence : Sentence, lits : list):
    literals = sentence.literals
    unification = {}
    removableLits = []
    for l in lits:
        # For each literal, find the corresponding location and unify
        key = (l.identifier, l.litType)
        # This is a conjunction of iterals
        positions = []
        for i in range(len(literals)):
            # Only select the appropriate, negatable literal(s)
            if (literals[i].identifier, literals[i].litType) == key and l.negated != literals[i].negated:
                positions.append(i)
                break

        if len(positions) == 0:
            return False

        for p in positions:
            unification.update(getUnification(literals[position], l))
            literals.pop(position)
            removableLits.append(l)
        if position != -1:
            pass    
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
        if (original.litType == 'C' or new.litType == 'V') and new.litType == 'V' and original.identifier != new.identifier:
            # print("Variable from {} to constant from {}".format(str(new), str(original)))
            return {new : original}
        elif original.litType == 'V' and new.litType == 'C':
            # print("Variable from {} to constant from {}".format(str(original), str(new)))
            return {original : new}
        else:
            # print("No unification between {} and {}".format(str(new), str(original)))
            return {}
    returnable = {}
    for i in range(len(original.args)):
        returnable.update(getUnification(original.args[i], new.args[i]))

    return returnable


def substitute(lit : Literal, unification : dict):
    # print("Trying to unify {} with {}".format(str(lit), unification)) # For debug purposes
    if lit.litType != 'P':
        # If the unification does not contain this identifier, then just return this
        lit = unification.get(lit, lit)
        return lit

    for i in range(len(lit.args)):
        lit.args[i] = substitute(lit.args[i], unification)

    return lit


def purgeCommon(lits1 : List[Literal], lits2 : List[Literal]):
    returnable = []
    for i in range(len(lits1)):
        loc1,loc2 = i,-1
        for j in range(len(lits2)):
            if lits1[i].deepEquals(lits2[j]) and lits1[i].negated != lits2[j].negated:
                # print("{} and {} cancel out".format(l1, lits2[i]))
                loc1,loc2 = i,j
                break
        if loc2 != -1:
            lits1.pop(loc1)
            lits2.pop(loc2)
            break
    returnable.extend(lits1)
    returnable.extend(lits2)
    return returnable