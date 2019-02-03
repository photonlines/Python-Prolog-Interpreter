import re
from src.Interpreter import Conjunction, Variable, Term, TRUE, Rule

# The following class implements a parser we use to parse our Prolog programs / queries.
class Parser:

    def __init__(self, input_text):

        self.token_regex = '[A-Za-z0-9_]+|:\-|[()\.,]'
        self.atom_name_regex = '^[A-Za-z0-9_]+$'
        self.variable_regex = '^[A-Z_][A-Za-z0-9_]*$'

        # Regex to parse comment strings. The first group captures quoted strings (double and single).
        # The second group captures regular comments ('%' for single-line or '/* */' for multi-line)
        self.comment_regex = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|%[^\r\n]*$)"

        tokens = self.get_token_list( input_text )

        self.tokens = tokens
        self.token_iterator = iter(self.tokens)

        self.current = None
        self.finished = False
        self.scope = None

        self.parse_next()

    # Return the input text string with all of the comments removed from it
    def remove_comments(self, input_text):

        # Create a regular expression Pattern object we can use to find and strip out comments.
        # The MULTILINE flag tells Python to treat each line in the string separately, while the DOTALL flag
        # indicates that we can match patterns which span multiple lines (so our multi-line comments '/* */'
        # can  be processed)
        regex = re.compile(self.comment_regex, re.MULTILINE | re.DOTALL)

        def remove_comment(match):
            # If we found a match for our 2nd group, it is a comment, so we remove it
            if match.group(2) is not None:
                return ''
            # Otherwise, we found a quoted string containing a comment, so we leave it in
            else:
                return match.group(1)

        return regex.sub(remove_comment, input_text)

    # Convert the input text into a list of tokens we can iterate over / process
    def get_token_list(self, input_text):
        iterator = re.finditer(self.token_regex, self.remove_comments( input_text ) )
        return [token.group() for token in iterator];

    def parse_rules(self):
        rules = []

        while not self.finished:
            self.scope = {}
            rules.append(self.parse_rule())

        return rules

    def parse_query(self):
        self.scope = {}
        return self.parse_term()

    def parse_next(self):
        try:
            self.current = next(self.token_iterator)
            # If there are no more tokens to iterate over, we mark the parser as being finished
            self.finished = self.token_iterator.__length_hint__() <= 0
        except StopIteration:
            self.finished = True

    def parse_atom(self):
        name = self.current

        if re.match(self.atom_name_regex, name) is None:
            raise Exception("Invalid Atom Name: " + str(name))

        self.parse_next()

        return name

    def parse_term(self):

        # If we encounter an opening parenthesis, we know we're dealing with a conjunction, so we process the
        # list of arguments until we hit a closing parenthesis and return the conjunction object.
        if (self.current == '('):

            self.parse_next()
            arguments = []

            while (self.current != ')'):
                arguments.append(self.parse_term())

                if self.current not in (',', ')'):
                    raise Exception('Expected , or ) in term but got ' + str(self.current))

                if (self.current == ','):
                    self.parse_next()

            self.parse_next()

            return Conjunction(arguments)

        functor = self.parse_atom()

        # If we have a matching variable, we make sure that variables with the same name within a rule always
        # use one variable object (with the exception of the anonymous '_' variable object).
        if re.match(self.variable_regex, functor) is not None:

            if functor == '_':
                return Variable('_')

            variable = self.scope.get(functor)

            if variable is None:
                self.scope[functor] = Variable(functor)
                variable = self.scope[functor]

            return variable

        # If there are no arguments to process, return an atom. Atoms are processed as terms without arguments.
        if self.current != '(':
            return Term(functor)

        self.parse_next()

        # We now process our term arguments:
        arguments = []

        # Keep adding the arguments to our list until we encounter an ending parenthesis ')'
        while self.current != ')':
            arguments.append(self.parse_term())
            if self.current not in (',', ')'):
                raise Exception('Expected , or ) in term but got ' + str(self.current))
            if (self.current == ','):
                self.parse_next()

        self.parse_next()

        return Term(functor, arguments)

    def parse_rule(self):

        head = self.parse_term()

        if self.current == '.':
            self.parse_next()
            # We process facts as rules with the tail set to true:
            return Rule(head, TRUE())

        if self.current != ':-':
            raise Exception('Expected :- in rule but got ' + str(self.current))

        self.parse_next()

        # Process the rule arguments
        arguments = []

        while (self.current != '.'):
            arguments.append(self.parse_term())

            if (self.current not in (',', '.')):
                raise Exception('Expected , or . in term but got ' + str(self.current))

            if self.current == ',':
                self.parse_next()

        self.parse_next()

        # If we have more than one argument, we return a conjunction, otherwise, we process the item as a regular
        # rule containing a head and a tail
        tail = arguments[0] if arguments == 1 else Conjunction(arguments)
        return Rule(head, tail)

