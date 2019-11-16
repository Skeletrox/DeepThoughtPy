

class Literal(object):
    """A literal is a basic logical unit, that is made of composites of itself"""
    def __init__(self, inpString : str):
        """ The inpstring is parsed to get the output"""

        # Check if first letter implies negation
        self.negated = inpString[0] == '~'
        if self.negated:
            inpString = inpString[1:]
        self.args = None
        # Check if first letter is small. If so, then this is a variable
        if ord(inpString[0]) > ord('a') and ord(inpString[0]) < ord('z'):
            self.litType = 'V'
            self.identifier = inpString
        elif inpString.find('(') != -1:
            # There is a bracket in this, this is a predicate
            self.litType = 'P'
            openBrackets = inpString.find('(')
            self.identifier = inpString[:openBrackets]
            closeBrackets = inpString.find(')')
            args = inpString[openBrackets+1:closeBrackets].split(',')
            self.args = processArgs(args)
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
                return False
            for i in range(len(self.args)):
                if not self.args[i].canBeResolvedBy(other.args[i]):
                    return False

        return True

    def negate(self):
        self.negated ^= True;


    def __str__(self):
        return "{}{}{}".format("~" if self.negated else "", self.identifier, "({})".format(",".join([str(a) for a in self.args])) if self.litType == 'P' else "")

def processArgs(args):
    """ Converts args into literals"""
    returnable = []
    for a in args:
        a = a.strip()
        literal = Literal(a)
        returnable.append(literal)

    return returnable