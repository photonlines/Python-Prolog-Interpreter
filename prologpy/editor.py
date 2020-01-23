from tkinter import Tk, Text, Menu, filedialog, Label, Button, END, W, E, FALSE
from tkinter.scrolledtext import ScrolledText
from prologpy.solver import Solver


class Editor(object):

    def __init__(self, root_):

        self.root = root_
        self.file_path = None
        self.root.title("Prolog Interpreter")

        # Create a rule label

        self.rule_editor_label = Label(
            root, text="Prolog Rules: ", padx=10, pady=1
        )

        self.rule_editor_label.grid(
            sticky="W", row=0, column=0, columnspan=2, pady=3
        )

        # Create rule editor where we can edit the rules we want to enter:

        self.rule_editor = ScrolledText(
            root, width=100, height=30, padx=10, pady=10
        )

        self.rule_editor.grid(
            sticky=W + E, row=1, column=0, columnspan=2, padx=10
        )

        self.rule_editor.config(wrap="word", undo=True)

        self.rule_editor.focus()

        # Create a query label:

        self.query_label = Label(root, text="Prolog Query:", padx=10, pady=1)

        self.query_label.grid(sticky=W, row=2, column=0, columnspan=2, pady=3)

        # Create the Prolog query editor we'll use to query our rules:

        self.query_editor = Text(root, width=77, height=2, padx=10, pady=10)

        self.query_editor.grid(sticky=W, row=3, column=0, pady=3, padx=10)

        self.query_editor.config(wrap="word", undo=True)

        # Create a run button which runs the query against our rules and outputs the
        # results in our solutions text box / editor.

        self.run_button = Button(
            root,
            text="Find Query Solutions",
            height=2,
            width=20,
            command=self.run_query,
        )

        self.run_button.grid(sticky=E, row=3, column=1, pady=3, padx=10)

        # Create a solutions label

        self.solutions_label = Label(
            root, text="Query Solutions:", padx=10, pady=1
        )

        self.solutions_label.grid(
            sticky="W", row=4, column=0, columnspan=2, padx=10, pady=3
        )

        # Create a text box which we'll use to display our Prolog query solutions:

        self.solutions_display = ScrolledText(
            root, width=100, height=5, padx=10, pady=10
        )

        self.solutions_display.grid(
            row=5, column=0, columnspan=2, padx=10, pady=7
        )

        # Finally, let's create the file menu
        self.menu_bar = self.create_file_menu()

    def create_file_menu(self):
        """Create a menu which will allow us to open / save our Prolog rules, run our
        query, and exit our editor interface """

        menu_bar = Menu(root)

        file_menu = Menu(menu_bar, tearoff=0)

        file_menu.add_command(
            label="Open...", underline=1, command=self.open_file
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save", underline=1, command=self.save_file
        )
        file_menu.add_command(
            label="Save As...", underline=5, command=self.save_file_as
        )
        file_menu.add_separator()
        file_menu.add_command(label="Run", underline=1, command=self.run_query)
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit", underline=2, command=self.root.destroy
        )

        menu_bar.add_cascade(label="File", underline=0, menu=file_menu)

        self.root.config(menu=menu_bar)
        return menu_bar

    def set_busy(self):
        # Show a busy cursor and update the UI
        self.root.config(cursor="watch")
        self.root.update()

    def set_not_busy(self):
        # Show a regular cursor
        self.root.config(cursor="")

    def run_query(self):
        """Interpret the entered rules and query and display the results in the
        solutions text box """

        # Delete all of the text in our solutions display text box
        self.solutions_display.delete("1.0", END)

        self.set_busy()

        # Fetch the raw rule / query text entered by the user
        rules_text = self.rule_editor.get(1.0, "end-1c")
        query_text = self.query_editor.get(1.0, "end-1c")

        # Create a new solver so we can try to query for solutions.
        try:
            solver = Solver(rules_text)
        except Exception as exception:
            self.handle_exception("Error processing prolog rules.", exception)
            return

        # Attempt to find the solutions and handle any exceptions gracefully
        try:
            solutions = solver.find_solutions(query_text)
        except Exception as exception:
            self.handle_exception("Error processing prolog query.", exception)
            return

        # If our query returns a boolean, we simply display a 'Yes' or a 'No'
        # depending on its value
        if isinstance(solutions, bool):
            self.solutions_display.insert(END, "Yes." if solutions else "No.")

        # Our solver returned a map, so we display the variable name to value mappings
        elif isinstance(solutions, dict):
            self.solutions_display.insert(
                END,
                "\n".join(
                    "{} = {}"
                    # If our solution is a list contining one item, we show that
                    # item, otherwise we display the entire list
                    .format(variable, value[0] if len(value) == 1 else value)
                    for variable, value in solutions.items()
                ),
            )
        else:

            # We know we have no matching solutions in this instance so we provide
            # relevant feedback
            self.solutions_display.insert(END, "No solutions found.")

        self.set_not_busy()

    def handle_exception(self, error_message, exception=""):
        """Handle the exception by printing an error message as well as exception in
        our solution text editor / display """
        self.solutions_display.insert(END, error_message + "\n")
        self.solutions_display.insert(END, str(exception) + "\n")
        self.set_not_busy()

    def is_file_path_selected(self, file_path):
        return file_path != None and file_path != ""

    def get_file_contents(self, file_path):
        """Return a string containing the file contents of the file located at the
        specified file path """
        with open(file_path, encoding="utf-8") as f:
            file_contents = f.read()

        return file_contents

    def set_rule_editor_text(self, text):
        self.rule_editor.delete(1.0, "end")
        self.rule_editor.insert(1.0, text)
        self.rule_editor.edit_modified(False)

    def open_file(self, file_path=None):

        # Open a a new file dialog which allows the user to select a file to open
        if file_path == None:
            file_path = filedialog.askopenfilename()

        if self.is_file_path_selected(file_path):
            file_contents = self.get_file_contents(file_path)

            # Set the rule editor text to contain the selected file contents
            self.set_rule_editor_text(file_contents)
            self.file_path = file_path

    def save_file(self):
        """If we have specified a file path, save the file - otherwise, prompt the
        user to specify the file location prior to saving the file """
        if self.file_path == None:
            result = self.save_file_as()
        else:
            result = self.save_file_as(file_path=self.file_path)

        return result

    def write_editor_text_to_file(self, file):
        editor_text = self.rule_editor.get(1.0, "end-1c")
        file.write(bytes(editor_text, "UTF-8"))
        self.rule_editor.edit_modified(False)

    def save_file_as(self, file_path=None):
        # If there is no file path specified, prompt the user with a dialog which
        # allows him/her to select where they want to save the file
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                filetypes=(
                    ("Text files", "*.txt"),
                    ("Prolog files", "*.pl *.pro"),
                    ("All files", "*.*"),
                )
            )

        try:

            # Write the Prolog rule editor contents to the file location
            with open(file_path, "wb") as file:
                self.write_editor_text_to_file(file)
                self.file_path = file_path
                return "saved"

        except FileNotFoundError:
            return "cancelled"

    def undo(self, event=None):
        self.rule_editor.edit_undo()

    def redo(self, event=None):
        self.rule_editor.edit_redo()


if __name__ == "__main__":

    root = Tk()
    editor = Editor(root)

    # Don't allow users to re-size the editor
    root.resizable(width=FALSE, height=FALSE)

    root.mainloop()
