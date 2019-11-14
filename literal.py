

class Literal(object):
    """A literal is a basic logical unit, that is made of composites of itself"""
    def __init__(self, inpString : str):
        """ The inpstring is parsed to get the output"""

        # Check if first letter implies negation
        self.negated = inpString[0] == '~'
        if self.negated:
            inpString = inpString[1:]
            
        # Check if first letter is small. If so, then this is a variable
        if ord(inpString[0]) > ord('a') and ord(inpString[0]) < ord('z'):
            self.litType = 'V'
            self.identifier = inpString
        elif inpString.index('(') != -1:
            # There is a bracket in this, this is a predicate
            self.litType = 'P'
            openBrackets = inpString.index('(')
            self.identifier = inpString[:openBrackets]
            closeBrackets = inpString.index(')')
            args = inpString[openBrackets+1:closeBrackets].split(',')
            self.args = processArgs(args)
        else:
            self.litType = 'C'
            self.identifer = inpString

    
    def negate():
        self.negated ^= True;


def processArgs(args : List[str]):
    """ Converts args into literals"""
    returnable = []
    for a in args:
        a = a.strip()
        literal = Literal(a)
        returnable.append(literal)

    return returnable