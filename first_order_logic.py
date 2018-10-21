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
    def copy(self):
        new_var_const = []
        for var_const in self.var_const:
            new_var_const.append(var_const.copy())

        return Statement(self.is_positive, self.relation, new_var_const)

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
    def copy(self):
        return Constant(self.name)

class Variable:
    # necessary properties: identifiable
    def __init__(self, name):
        self.name = name
    def copy(self):
        return Variable(self.name)

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

    def get_var_dict(self):
        # make a dictionary of variables (name -> [var1, var2, ...])
        var_dict = {}
        statements = self.premise + [self.conclusion]
        for statement in statements:
            for var_const in statement.var_const:
                if isinstance(var_const, Variable):
                    if var_const.name in var_dict:
                        var_dict[var_const.name].append(var_const)
                    else:
                        var_dict[var_const.name] = [var_const]
        return var_dict

    def copy(self):
        new_premise = []
        for statement in self.premise:
            new_premise.append(statement.copy())
        new_conclusion = self.conclusion.copy()
        return Implication(new_premise, new_conclusion)

    def substitute(self, name_const_dict):
        # name_const_dict: "x" -> Constant("Charlie")
        # "x" is the name of the variable
        copy = self.copy()
        statements = copy.premise + [copy.conclusion]
        for statement in statements:
            for i in range(len(statement.var_const)):
                var_const = statement.var_const[i]
                if isinstance(var_const, Variable) and var_const.name in name_const_dict:
                    statement.var_const[i] = name_const_dict[var_const.name]

        copy.sort_premise()
        copy.reform_premise()
        return copy


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
        self.facts = [] # implication of the form [] -> Parent(Harry, Kate)
        self.constants = {}

    def tell(self, implication):
        # add the implication to KB, if it's not the same as another implication
        for added_im in self.implications:
            if added_im.is_equal(implication): return
        self.implications.append(implication)
        if len(implication.premise) == 0:
            self.facts.append(implication)
        statements = implication.premise + [implication.conclusion]
        for statement in statements:
            for var_const in statement.var_const:
                if isinstance(var_const, Constant) and var_const.name not in self.constants:
                    self.constants[var_const.name] = var_const

    def statement_is_satisfied(self, statement):
        for var_const in statement.var_const:
            if isinstance(var_const, Variable):
                return False
        for im in self.facts:
            if statement.is_equal_reformed(im.conclusion): return True

        return False


    def premise_is_satisfied(self, implication):
        for statement in implication.premise:
            if not self.statement_is_satisfied(statement):
                return False
        return True

    def expand_by_substitution(self):
        for im in self.implications:
            var_dict = im.get_var_dict()
            var_names = list(var_dict.keys())
            all_const_selection = self.get_all_selections(len(var_names), self.constants)
            for selection in all_const_selection:
                name_const_dict = {var_names[i]:Constant(selection[i]) for i in range(len(var_names))}
                self.tell(im.substitute(name_const_dict))


    def expand_by_inference(self):
        to_add = []
        for im in self.implications:
            size = len(self.implications)
            if self.premise_is_satisfied(im):
                new_im = Implication([], im.conclusion)
                self.tell(new_im)
                if size < len(self.implications):
                    to_add.append(new_im)
        if len(to_add) > 0:
            self.expand_by_inference()

    def expand(self):
        self.expand_by_substitution()
        self.expand_by_inference()

    def get_all_selections(self, k, list2):
        # return a list of all possible selections when selecting k elements from list2 (with replacement)
        # a selection is a list of elements

        if k== 0:
            return []
        if k==1:
            return [[element] for element in list2 ]

        all_selections = []
        sub_selections = self.get_all_selections(k-1, list2)
        for element in list2:
            for selection in sub_selections:
                all_selections.append([element] + selection)
        return all_selections


    def ask(self, query):
        pass

    def to_string(self):
        str = ''
        for i in range(len(self.implications)):
            str += self.implications[i].to_string() + '\n'
        return str

    def forward_chaining(self, query):

        return

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

def test_inference():
    KB = KnowledgeBase()
    A = Relation("A")
    B = Relation("B")
    C = Relation("C")


    KB.tell(Implication([Statement(True, A, [Variable("x")])], Statement(True, B, [Variable("x")])))
    KB.tell(Implication([Statement(True, B, [Variable("x")])], Statement(True, C, [Variable("x")])))
    KB.tell(Implication([], Statement(True, A, [Constant("Quang")])))

    print(KB.to_string())
    KB.expand()
    print(KB.to_string())

def test_parent_sibling():
    KB = KnowledgeBase()
    Parent = Relation("Parent")
    Sibling = Relation("Sibling")

    KB.tell(Implication([Statement(True, Parent, [Variable("x"), Variable("y")]), Statement(True, Parent, [Variable("x"), Variable("z")])], Statement(True, Sibling, [Variable("y"), Variable("z")])))
    KB.tell(Implication([], Statement(True, Parent, [Constant("Hoang"), Constant("Quang")])))
    KB.tell(Implication([], Statement(True, Parent, [Constant("Hoang"), Constant("Tung")])))

    print(KB.to_string())
    KB.expand()
    print(KB.to_string())

def main():
    test_parent_sibling()


main()