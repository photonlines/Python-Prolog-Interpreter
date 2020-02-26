from prologpy.interpreter import Database, Variable
from prologpy.parser import Parser
from collections import defaultdict


class Solver(object):
    def __init__(self, rules_text):
        """Parse the rules text and initialize the database we plan to use to query
        our rules."""
        rules = Parser(rules_text).parse_rules()
        self.database = Database(rules)

    def find_solutions(self, query_text):
        """Parse the query text and use our database rules to search for matching
        query solutions. """

        query = Parser(query_text).parse_query()

        query_variable_map = {}
        variables_in_query = False

        # Find any variables within the query and return a map containing the
        # variable name to actual Prolog variable mapping we can later use to query
        # our database.
        for argument in query.arguments:
            if isinstance(argument, Variable):
                variables_in_query = True
                query_variable_map[argument.name] = argument

        # Return a generator which iterates over the terms matching our query
        matching_query_terms = [item for item in self.database.query(query)]

        if matching_query_terms:
            if query_variable_map:

                # If our query has variables and we have matching query terms/items,
                # we iterate over the query items and our list of query variables and
                # construct a map containing the matching variable names and their
                # values
                solutions_map = defaultdict(list)
                for matching_query_term in matching_query_terms:
                    matching_variable_bindings = query.match_variable_bindings(
                        matching_query_term
                    )

                    # Itarate over the query variables and bind them to the matched
                    # database bindings
                    for variable_name, variable in query_variable_map.items():
                        solutions_map[variable_name].append(
                            matching_variable_bindings.get(variable)
                        )

                return solutions_map

            else:
                # If we have matching query items / terms but no variables in our
                # query, we simply return true to indicate that our query did match
                # our goal. Otherwise, we return None
                return True if not variables_in_query else None
        else:
            # If we have no variables in our query, it means our goal had no matches,
            # so we return False. Otherwise simply return None to show no variable
            # bindings were found.
            return False if not variables_in_query else None
