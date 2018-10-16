# First knowledge based agent
class Statement:
    def __init__(self, function, object):
        self.function = function
        self.object = object

class Function:
    def __init__(self, name):
        self.name = name

class Object:
    def __init__(self, name):
        self.name = name

class Variable:
    def __init__(self, name):
        self.name = name

class Implication:
    def __init__(self, statement1, statement2):
        self.statement1 = statement1
        self.statement2 = statement2

class KnowledgeBase:
    def __init__(self):
        self.statements = []
        self.implications = []

    def tell(self, statement_or_implication):
        if isinstance(statement_or_implication, Statement):
            self.statements.append(statement_or_implication)
        elif isinstance(statement_or_implication, Implication):
            self.implications.append(statement_or_implication)


    def is_equal(self, statement1, statement2):
        return statement1.function == statement2.function and statement1.object == statement2.object

    def ask(self, query):
        new = []
        for statement in self.statements:
            if self.is_equal(query, statement):
                return True
        for implication in self.implications:
            for statement in self.statements:
                if implication.statement1.function == statement.function:
                    new_statement = Statement(implication.statement2.function, statement.object)
                    self.tell(new_statement)
                    new.append(new_statement)
                    if self.is_equal(query, new_statement):
                        return True

        if len(new) == 0:
            return False
        else:
            self.ask(query)

def main():
    KB = KnowledgeBase()
    Jay = Object("jay")
    Male = Function("male")
    NotFemale = Function("not_female")
    ShortHair = Function("short_hair")
    x = Variable("x")
    s1 = Statement(Male, [Jay])
    s2 = Statement(Male, [x])
    s3 = Statement(NotFemale, [x])
    s4 = Statement(ShortHair, [x])

    im1 = Implication(s2, s3)
    im2 = Implication(s3, s4)

    KB.tell(s1)
    KB.tell(im1)
    KB.tell(im2)
    query = Statement(ShortHair, [Jay])
    print(KB.ask(query))


main()