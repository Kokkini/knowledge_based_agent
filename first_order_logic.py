# First knowledge based agent
class Statement:
    # necessary properties: syntax being similar to a usual statement
    def __init__(self, is_positive, relation, var_const):
        self.is_positive = is_positive
        self.relation = relation
        self.var_const = var_const

    def compare(self, other):
        # order: relation, is_positive, var_const
        if (self.relation.name < other.relation.name):
            return -1
        if (self.relation.name > other.relation.name):
            return 1

        if (self.is_positive==True and other.is_positive==False):
            return -1
        if (self.is_positive==False and other.is_positive==True):
            return 1

        assert len(self.var_const) == len(other.var_const)
        for i in range(len(self.var_const)):
            this = self.var_const[i]
            that = other.var_const[i]
            if isinstance(this, Constant) and isinstance(that, Variable):
                return -1
            if isinstance(this, Variable) and isinstance(that, Constant):
                return 1
            if isinstance(this, Constant) and isinstance(that, Constant):
                if this.name < that.name: return -1
                if this.name > that.name: return 1

        return 0

    def is_equal_reformed(self, other):
        if len(self.var_const) != len(other.var_const):
            return False
        if (self.relation.name != other.relation.name):
            return False

        if (self.is_positive != other.is_positive):
            return False

        assert len(self.var_const) == len(other.var_const)
        for i in range(len(self.var_const)):
            this = self.var_const[i]
            that = other.var_const[i]
            if isinstance(this, Constant) != isinstance(that, Constant):
                return False

            if this.name != that.name:
                return False
        return True

    def to_string(self):
        str = ''
        if self.is_positive: str += '+'
        else: str += '-'
        str += self.relation.name
        str += '('
        for i in range(len(self.var_const)):
            str += self.var_const[i].name
            if i!=len(self.var_const) - 1:
                str += ' '
        str = str + ')'
        return str

class Relation:
    def __init__(self, name):
        self.name = name

class Constant:
    # necessary properties: identifiable
    def __init__(self, name):
        self.name = name

class Variable:
    # necessary properties: identifiable
    def __init__(self, name):
        self.name = name

class Implication:
    # necessary properties:
    # identifiable: P(x,z), Q(y,z) -> T(x,y) is the same as Q(x,y), P(z,y) -> T(z,x). To decide whether or not to add it to the KB
    # we need this because all the KB has is implications
    # solution: sort relation and implication and before adding to KB
    def __init__(self, premise, conclusion):
        # premise: set of statements
        # conclusion: one statement
        self.premise = premise
        self.conclusion = conclusion
        self.sort_premise()
        self.reform_premise()

    def is_equal(self, other):
        if len(self.premise) != len(other.premise): return False
        for i in range(len(self.premise)):
            if not self.premise[i].is_equal_reformed(other.premise[i]): return False

        if not self.conclusion.is_equal_reformed(other.conclusion): return False
        return True


    def arg_min(self, statements):
        assert len(statements) > 0
        min_ix = 0
        for i in range(1, len(statements)):
            if statements[i].compare(statements[min_ix]) == -1:
                min_ix = i
        return min_ix

    def sort_premise(self):
        if len(self.premise) < 2:
            return
        for i in range(len(self.premise)):
            min_ix = self.arg_min(self.premise[i:])
            min_statement = self.premise[min_ix]
            self.premise[min_ix] = self.premise[i]
            self.premise[i] = min_statement

    def reform_premise(self):
        if len(self.premise) == 0:
            return
        var_names = {} # map 'x' to [2, [var1, var2, var3]]
        order = 0
        for i in range(len(self.premise)):
            for var_const in self.premise[i].var_const:
                if isinstance(var_const, Constant): continue
                if var_const.name not in var_names:
                    var_names[var_const.name] = [order, [var_const]]
                    order += 1
                else:
                    var_names[var_const.name][1].append(var_const)
        for var_const in self.conclusion.var_const:
            if isinstance(var_const, Constant): continue
            assert var_const.name in var_names
            var_names[var_const.name][1].append(var_const)
        for key in var_names:
            new_name = chr(ord('a')+var_names[key][0])
            for var in var_names[key][1]:
                var.name = new_name

    def to_string(self):
        str = ''
        for i in range(len(self.premise)):
            str += ' ' + self.premise[i].to_string() + ' '
            if i != len(self.premise) - 1:
                str += '&'
        str += '-> '
        str += self.conclusion.to_string()
        return str


class KnowledgeBase:
    def __init__(self):
        self.implications = []

    def tell(self, implication):
        # add the implication to KB, if it's not the same as another implication
        for added_im in self.implications:
            if added_im.is_equal(implication): return

        self.implications.append(implication)

    def ask(self, query):
        pass

    def to_string(self):
        str = ''
        for i in range(len(self.implications)):
            str += self.implications[i].to_string() + '\n'
        return str

def test_print():
    KB = KnowledgeBase()
    male = Relation('Male')
    likes = Relation('Likes')
    jack = Constant('Jack')
    true = Relation('True')


    s1 = Statement(True, male, [jack])
    s2 = Statement(True, true, [])


    im1 = Implication([s1], s2)
    im2 = Implication([Statement(False, male, [Variable('x')]), Statement(True, male, [jack])], Statement(True, likes, [jack, Variable('x')]))
    im3 = Implication([Statement(True, likes, [Variable('x'),Variable('y')]), Statement(True, likes, [Variable('y'),Variable('z')])], Statement(True, likes, [Variable('x'),Variable('z')]))
    im4 = Implication([Statement(True, likes, [Variable('x'),Variable('y')])], s2)
    im5 = Implication([Statement(True, likes, [Variable('z'),Variable('t')])], s2)


    KB.tell(im1)
    KB.tell(im2)
    KB.tell(im3)
    KB.tell(im4)
    KB.tell(im5)
    print(KB.to_string())

def main():
    test_print()


main()