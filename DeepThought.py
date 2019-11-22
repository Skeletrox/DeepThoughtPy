from knowledgebase import KnowledgeBase
from literal import Literal

def main():
    numQueries = 0
    queries = []
    numTruths = 0
    truths = []
    with open("./input.txt") as inp:
        line = inp.readline()
        # First line is always the number of queries
        numQueries = int(line)
        # n queries
        for i in range(numQueries):
            line = inp.readline()
            queries.append(line.strip())
        line = inp.readline()
        # This is followed by the number of truths
        numTruths = int(line)
        for i in range(numTruths):
            line = inp.readline()
            truths.append(line.strip())

    kb = KnowledgeBase(truths)

    for q in queries:
        lit = Literal(q, len(truths)+1)
        lit.negate()
        result = kb.proveByResolution2([lit], 0)
        print("{}: {}".format(q, result))

if __name__ == "__main__":
    main()