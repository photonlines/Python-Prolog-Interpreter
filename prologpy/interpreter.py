from functools import reduce


class Term(object):
    """Prolog has only one data type — the term.

    The simplest term is an atom. Atoms can be combined to form compound terms.
    Example: are_friends(mark, michael) is a compound term where are_friends is
    called a functor and mark and michael are arguments.
    """

    def __init__(self, functor, arguments=None):
        if not arguments:
            arguments = []
        self.functor = functor
        self.arguments = arguments

    def match_variable_bindings(self, other_term):
        """Return a map of matching variable bindings"""

        # If the passed in term is a variable, we bind the variable to our current
        # term and return the result.
        if isinstance(other_term, Variable):
            return other_term.match_variable_bindings(self)

        # If we have a term, we check if the terms are identical and if so,
        # we extract the combined variable bindings.
        if isinstance(other_term, Term):

            # Verify that the functor and argument lengths match.
            if self.functor != other_term.functor or len(
                self.arguments
            ) != len(other_term.arguments):
                return None

            # Zip the current term and the other term arguments and combine the
            # results into one list. Zip creates a new list filled with tuples
            # containing the matching elements from the 2 argument lists. i.e. zip ([
            # 1, 2, 3],[4, 5, 6]) returns [(1, 4), (2, 5), (3, 6)]
            zipped_argument_list = list(
                zip(self.arguments, other_term.arguments)
            )

            # Get the matched variable bindings list for the matching arguments in
            # our 2 terms and merge them.
            matched_argument_var_bindings = [
                arguments[0].match_variable_bindings(arguments[1])
                for arguments in zipped_argument_list
            ]

            # Merge the combined argument variable bindings and return the result.
            # The reduce function applies a rolling computation to sequential pairs
            # of values in a list. i.e. reduce((lambda x, y: x + y), [1, 2, 3,
            # 4]) returns 10
            return reduce(
                Database.merge_bindings, [{}] + matched_argument_var_bindings
            )

    def substitute_variable_bindings(self, variable_bindings):
        """Take the variable bindings map and return a term with all occurrences of
        the term variables replaced with the corresponding variable values from our
        variable bindings map.
        """
        return Term(
            self.functor,
            [
                argument.substitute_variable_bindings(variable_bindings)
                for argument in self.arguments
            ],
        )

    def query(self, database):
        """Query the database for terms matching this one"""
        yield from database.query(self)

    def __str__(self):
        return (
            str(self.functor)
            if len(self.arguments) == 0
            else str(self.functor)
            + " ( "
            + ", ".join(str(argument) for argument in self.arguments)
            + " ) "
        )

    def __repr__(self):
        return str(self)


class TRUE(Term):
    """A predefined term used to represent facts as rules. i.e. functor(argument1,
    argument2) for example gets translated to functor(argument1, argument2) :- TRUE """

    # TODO should take no arguments?
    def __init__(self, functor="TRUE", arguments=None):
        if not arguments:
            arguments = []
        super().__init__(functor, arguments)

    def substitute_variable_bindings(self, variable_bindings):
        # Simply return our truth term since there is nothing to bind
        return self

    def query(self, database):
        yield self


class Variable(object):
    """A variable is a type of term. Variables start with an uppercase letter and
    represent placeholders for actual terms. """

    def __init__(self, name):
        self.name = name

    def match_variable_bindings(self, other_term):
        """ If the passed in term doesn't represent the same variable, we bind our
        current variable to the outer term and return the mapped binding. """
        bindings = {}

        if self != other_term:
            bindings[self] = other_term

        return bindings

    def substitute_variable_bindings(self, variable_bindings):
        """Fetch the currently bound variable value for our variable and return the
        substituted bindings if our variable is mapped. If our variable isn't mapped,
        we simply return the variable as the substitute. """
        bound_variable_value = variable_bindings.get(self)

        if bound_variable_value:
            return bound_variable_value.substitute_variable_bindings(
                variable_bindings
            )

        return self

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)


class Rule(object):
    """Rules are used to define relationships between facts and other rules.They
    allow us to make conditional statements about our world. Let's say we want to say
    that all humans are mortal. We can do so using the rule below: mortal(X) :-
    human(X) """

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __str__(self):
        return str(self.head) + " :- " + str(self.tail)

    def __repr__(self):
        return str(self)


class Conjunction(Term):
    """# A conjunction is a logical operator that connects two terms. A conjunction
    between the two terms will result in the expression evaluating to true only if
    both terms evaluate to true. As an example, we could state that a teacher
    teaches another student if the student lectures a course and the student
    studies the course using the rule below:

    teaches(Teacher, Student) :- lectures(Teacher, Course), studies(Student, Course).

    """

    def __init__(self, arguments):
        super().__init__("", arguments)

    def query(self, database):
        """Return a generator that iterates over all of the conjunction terms which
        match the database rules. """

        def find_solutions(argument_index, variable_bindings):
            """Return a generator which iterates over all of the database solutions
            matching our rules """

            # If there are no more arguments to match, we return the substituted
            # variable bindings for our entire conjunction
            if argument_index >= len(self.arguments):
                yield self.substitute_variable_bindings(variable_bindings)
            else:
                # There are more arguments to process, so we process the argument at
                # our current index
                current_term = self.arguments[argument_index]

                # Find all of the database items matching our current variable
                # bindings, and if we have matching items, keep searching the
                # database by iterating over our next conjunction arguments
                for item in database.query(
                    current_term.substitute_variable_bindings(
                        variable_bindings
                    )
                ):

                    combined_variable_bindings = Database.merge_bindings(
                        current_term.match_variable_bindings(item),
                        variable_bindings,
                    )

                    if combined_variable_bindings is not None:
                        yield from find_solutions(
                            argument_index + 1, combined_variable_bindings
                        )

        # Find all of the conjunction solutions matching our database rules. As a
        # note, the yield from expression is a form of generator delegation used to
        # recursively process all of the items matching our rules.
        yield from find_solutions(0, {})

    def substitute_variable_bindings(self, variable_bindings):
        """ Take the variable bindings map and return a conjunction with all
        occurrences of the variables present in our current conjunction terms
        replaced with a list of terms containing the substituted variable bindings
        from our variable bindings map.

        """
        return Conjunction(
            [
                argument.substitute_variable_bindings(variable_bindings)
                for argument in self.arguments
            ]
        )

    def __str__(self):
        return ", ".join(str(argument) for argument in self.arguments)

    def __repr__(self):
        return str(self)


class Database(object):
    """The database object is an object which contains a list of our declared rules.

    It's used to query our data for items matching a goal. It also contains the
    helper function used to merge variable bindings.

    """

    def __init__(self, rules):
        self.rules = rules

    def query(self, goal):
        """Return a generator that iterates over all of the terms matching the given
        goal.

        """

        for index, rule in enumerate(self.rules):

            # We obtain the map containing our shared rule head and goal variable
            # bindings, and process the matching results if there are any to process.
            matching_head_var_bindings = rule.head.match_variable_bindings(
                goal
            )

            if matching_head_var_bindings is not None:

                matched_head_item = rule.head.substitute_variable_bindings(
                    matching_head_var_bindings
                )
                matched_tail_item = rule.tail.substitute_variable_bindings(
                    matching_head_var_bindings
                )

                # Query the database for the substituted tail items matching our rules
                for matching_item in matched_tail_item.query(self):

                    # Fetch the map containing our variable bindings matching the
                    # tail of our rule.
                    matcng_tail_var_bndngs = matched_tail_item.match_variable_bindings(
                        matching_item
                    )

                    # We return a generator yielding head terms with the substituted
                    # variable bindings replaced with the bindings found by querying
                    # our tail.
                    yield matched_head_item.substitute_variable_bindings(
                        matcng_tail_var_bndngs
                    )

    @staticmethod
    def merge_bindings(first_bindings_map, second_bindings_map):
        """Takes two variable binding maps and returns a combined bindings map if
        there are no conflicts. If any of the bound variables are present in both
        bindings maps but the terms they are bound to do not match, merge_bindings
        returns None. """

        if first_bindings_map is None or second_bindings_map is None:
            return None

        merged_bindings = {}

        # Process our first bindings map and add the variable bindings to our merged map
        for variable, value in first_bindings_map.items():
            merged_bindings[variable] = value

        # Process our second bindings map and verify that the bindings contain in
        # this map align with the bindings from our first binding map. If any
        # variable bindings do not align, we return None. Otherwise, we process any
        # matching items and continue iterating through our binding map adding each
        # binding to our merged map.
        for variable, value in second_bindings_map.items():

            if variable in merged_bindings:

                existing_variable_binding = merged_bindings[variable]
                shared_bindings = existing_variable_binding.match_variable_bindings(
                    value
                )

                # If we have shared bindings, we add them to our existing map
                if shared_bindings is not None:
                    for variable_, value_ in shared_bindings.items():
                        merged_bindings[variable_] = value_

                # If the shared bindings don't match, we have a conflict and we
                # return None
                else:
                    return None

            else:
                merged_bindings[variable] = value

        return merged_bindings

    def __str__(self):
        return ".\n".join(str(rule) for rule in self.rules)

    def __repr__(self):
        return str(self)
