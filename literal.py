

class Literal(object):
    """A literal is a basic logical unit, that is made of composites of itself"""
    def __init__(self, inpString : str, sNum : int):
        """ The inpstring is parsed to get the output"""

        # Check if first letter implies negation
        self.negated = inpString[0] == '~'
        if self.negated:
            inpString = inpString[1:]
        self.args = None
        # Check if first letter is small. If so, then this is a variable
        if ord(inpString[0]) >= ord('a') and ord(inpString[0]) <= ord('z'):
            self.litType = 'V'
            self.identifier = "{}_{}".format(inpString, sNum)
        elif inpString.find('(') != -1:
            # There is a bracket in this, this is a predicate
            self.litType = 'P'
            openBrackets = inpString.find('(')
            self.identifier = inpString[:openBrackets]
            closeBrackets = inpString.find(')')
            args = inpString[openBrackets+1:closeBrackets].split(',')
            self.args = processArgs(args, sNum)
        else:
            self.litType = 'C'
            self.identifier = inpString

    def canBeResolvedBy(self, other):
        """Returns if self, while in KB, can be resolved with incoming other"""
        # Variables can be resolved with other variables and constants
        if self.litType == 'V':
            return other.litType != 'P'

        # Constants can resolve with similar constants
        elif self.litType == 'C':
            return self.identifier == other.identifier and other.litType == 'C'

        # Predicates only resolve with similar predicates and resolvable args
        else:
            if other.litType != 'P' or other.identifier != self.identifier or len(self.args) != len(other.args):
                # print("Cannot resolve {} and {}".format(str(self), str(other))) # For debug purposes
                return False
            for i in range(len(self.args)):
                if not self.args[i].canBeResolvedBy(other.args[i]):
                    # print("Cannot resolve {} and {} because of {} and {}".format(str(self), str(other), str(self.args[i]), str(other.args[i]))) # For debug purposes
                    return False

        return True

    def negate(self):
        self.negated ^= True;


    def __hash__(self):
        return hash((self.identifier, self.litType))

    def __eq__(self, other):
        return (self.identifier, self.litType) == (other.identifier, other.litType)

    def __str__(self):
        return "{}{}{}".format("~" if self.negated else "", self.identifier, "({})".format(",".join([str(a) for a in self.args])) if self.litType == 'P' else "")

    def deepEquals(self, other):
        if self.litType != other.litType:
            return False
        elif self.litType == 'P':
            if len(other.args) !=len(self.args) or self.identifier != other.identifier:
                return False
            else:
                for i in range(len(self.args)):
                    res = self.args[i] == other.args[i]
                    if not res:
                        return False
                return True
        else:
            return self.identifier == other.identifier


    def __neq__(self, other):
        return not self.__eq__(other)

def processArgs(args, sNum):
    """ Converts args into literals"""
    returnable = []
    for a in args:
        a = a.strip()
        literal = Literal(a, sNum)
        returnable.append(literal)

    return returnable