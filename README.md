### Description

This is a mini-Prolog Interpreter written in a few lines of Python 3. It runs a limited subset of Prolog and uses backtracking and generators in order to perform its magic.  The inspiration for creating this, with full info and detailed writeup on implementation, can be found through [this link](https://curiosity-driven.org/prolog-interpreter).

In addition to the interpreter, there’s also an interface for testing the functionality which allows a user to enter Prolog rules and perform queries for the solutions: 

![](images/Prolog-Editor-Snip.PNG?raw=true)

### Prolog

Prolog stands for ‘Programming in Logic’. It’s a declarative programming language. This means that the programmer specifies a goal to be achieved, and Prolog works out how to achieve it. 

Prolog has been enormously influential in the domains of theorem proving, expert systems, natural language processing and in the field of artificial intelligence. It also significantly influenced the development of Erlang programming language. 

### Prolog Programming

Prolog code consists of two main types of clauses: facts and rules. 

Facts are assertions about a domain. They always start with a lowercase letter and end with a period. We use them to build our database / logical rules. As an example, we could say that Mary and Jack and siblings using the simple statement provided below:

```prolog
sibling( mary, jack).
```

We don’t only have to include relations though. We could state that the day is sunny and that logic programming is amazing using these facts:

```prolog
sunny.
logic_programming_is_amazing.
```

Rules are inferences about facts. As an example, we could state that 2 children are siblings if they share at least one parent: 

```prolog
sibling(X, Y) :- parent_child(Z, X), parent_child(Z, Y).
```

Using the above rule, we can assert that mary and jack are siblings by specifying facts which show that they share the same parent:

```prolog
parent_child( tom_smith, mary ).
parent_child( tom_smith, jack ).
```

We can combine facts and rules to specify more complex statements – our choice is almost unlimited. As an example, we can represent the statement 'Something is fun if it’s a blue car or ice cream' as follows:

```prolog
fun(X) :- blue(X), car(X).
fun(ice_cream).
```

As a note, we use capital letters in Prolog to denote variables, which are placeholders for terms we can use to express our rules and query our data.  

Variable name scoping is per-individual rule. The same variable name may appear in different clauses of a rule, or rules with different names, and each time it is treated as something specific to its context. As an example, we re-used variable X a few times above, and in each instance, the interpreter treats it as a different variable with different possible bindings, since its scope only extends within the rule it’s defined in.  

### Queries

The real power of Prolog comes from the ability to query our facts and rules. Queries are used to either check if an expression is true, or we can use them to try to find possible solutions that satisfy the query criteria by using Variables.

The example below shows how we can perform a very simple query checking if it is sunny:

```prolog
?- sunny.
Yes.
```

Of course, Prolog assumes that anything NOT contained within its database of facts and rules is False, so if we queried for any facts that we haven’t defined, it would return ‘No.’:

```prolog
?- rainy.
No.
?- wonderful.
No.
?- bright.
No.
```

We can also use Variables to query for items which satisfy our rules. Let’s say that we know that Fred eats oranges, so we define:

```prolog
eats(fred, oranges).
```

How could we ask what Fred eats? We simply use a variable and our interpreter will take care of the rest:

```prolog
?- eats(fred, Food).
Food = oranges
```

The above gives a very small sample of Prolog. I’ve included a few test cases which demo how to solve the [Zebra / Einstein puzzle](https://en.wikipedia.org/wiki/Zebra_Puzzle) using the interpreter, and you can play around and create your own rules / programs using the editor. The original language includes a lot more functionality, so I urge you to explore further. 

