import re
from prologpy.interpreter import Conjunction, Variable, Term, TRUE, Rule


TOKEN_REGEX = r"[A-Za-z0-9_]+|:\-|[()\.,]"
ATOM_NAME_REGEX = r"^[A-Za-z0-9_]+$"
VARIABLE_REGEX = r"^[A-Z_][A-Za-z0-9_]*$"

# Regex to parse comment strings. The first group captures quoted strings (
# double and single). The second group captures regular comments ('%' for
# single-line or '/* */' for multi-line)
COMMENT_REGEX = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|%[^\r\n]*$)"


def remove_comments(input_text):
    """Return the input text string with all of the comments removed from it"""

    # Create a regular expression Pattern object we can use to find and strip out
    # comments. The MULTILINE flag tells Python to treat each line in the string
    # separately, while the DOTALL flag indicates that we can match patterns
    # which span multiple lines (so our multi-line comments '/* */' can  be
    # processed)
    regex = re.compile(COMMENT_REGEX, re.MULTILINE | re.DOTALL)

    def remove_comment(match):
        """If we found a match for our 2nd group, it is a comment, so we remove"""
        if match.group(2) is not None:
            return ""
        # Otherwise, we found a quoted string containing a comment, so we leave
        # it in
        else:
            return match.group(1)

    return regex.sub(remove_comment, input_text)


def parse_tokens_from_string(input_text):
    """Convert the input text into a list of tokens we can iterate over / process"""
    iterator = re.finditer(TOKEN_REGEX, remove_comments(input_text))
    return [token.group() for token in iterator]


class Parser(object):
    """
    NOTE: Instance can only be used once!
    """

    def __init__(self, input_text):
        self._tokens = parse_tokens_from_string(input_text)
        self._scope = None

    def parse_rules(self):
        rules = []
        while self._tokens:
            self._scope = {}
            rules.append(self._parse_rule())
        return rules

    def parse_query(self):
        self._scope = {}
        return self._parse_term()

    @property
    def _current(self):
        return self._tokens[0]

    def _pop_current(self):
        return self._tokens.pop(0)

    def _parse_atom(self):
        name = self._pop_current()
        if re.match(ATOM_NAME_REGEX, name) is None:
            raise Exception("Invalid Atom Name: " + str(name))
        return name

    def _parse_term(self):
        # If we encounter an opening parenthesis, we know we're dealing with a
        # conjunction, so we process the list of arguments until we hit a closing
        # parenthesis and return the conjunction object.
        if self._current == "(":
            self._pop_current()
            arguments = self._parse_arguments()
            return Conjunction(arguments)

        functor = self._parse_atom()

        # If we have a matching variable, we make sure that variables with the same
        # name within a rule always use one variable object (with the exception of
        # the anonymous '_' variable object).
        if re.match(VARIABLE_REGEX, functor) is not None:

            if functor == "_":
                return Variable("_")

            variable = self._scope.get(functor)

            if variable is None:
                self._scope[functor] = Variable(functor)
                variable = self._scope[functor]

            return variable

        # If there are no arguments to process, return an atom. Atoms are processed
        # as terms without arguments.
        if self._current != "(":
            return Term(functor)
        self._pop_current()
        arguments = self._parse_arguments()
        return Term(functor, arguments)

    def _parse_arguments(self):
        arguments = []
        # Keep adding the arguments to our list until we encounter an ending
        # parenthesis ')'
        while self._current != ")":
            arguments.append(self._parse_term())
            if self._current not in (",", ")"):
                raise Exception(
                    "Expected , or ) in term but got " + str(self._current)
                )
            if self._current == ",":
                self._pop_current()
        self._pop_current()
        return arguments

    def _parse_rule(self):

        head = self._parse_term()

        if self._current == ".":
            self._pop_current()
            # We process facts as rules with the tail set to true:
            return Rule(head, TRUE())

        if self._current != ":-":
            raise Exception(
                "Expected :- in rule but got " + str(self._current)
            )

        self._pop_current()

        # Process the rule arguments
        arguments = []

        while self._current != ".":
            arguments.append(self._parse_term())

            if self._current not in (",", "."):
                raise Exception(
                    "Expected , or . in term but got " + str(self._current)
                )

            if self._current == ",":
                self._pop_current()

        self._pop_current()

        # If we have more than one argument, we return a conjunction, otherwise,
        # we process the item as a regular rule containing a head and a tail
        tail = arguments[0] if arguments == 1 else Conjunction(arguments)
        return Rule(head, tail)
