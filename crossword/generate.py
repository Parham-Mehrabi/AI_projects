import sys

from crossword import Variable, Crossword


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for key, value in self.domains.items():
            self.domains[key] = {domain for
                                 domain in value
                                 if len(domain) == key.length
                                 }

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[(x, y)]
        if overlap is not None:
            x_overlap_index, y_overlap_index = overlap
            for x_variable in list(self.domains[x]):
                found = False
                for y_variables in self.domains[y]:
                    if x_variable[x_overlap_index] == y_variables[y_overlap_index]:
                        found = True
                if not found:
                    self.domains[x].remove(x_variable)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for x in self.domains.keys():
                for n in self.crossword.neighbors(x):
                    if self.crossword.overlaps[x, n] is not None:
                        arcs.append((x, n))

        while len(arcs) != 0:
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = self.crossword.neighbors(x)
                for n in neighbors - {y}:
                    arcs.append((n, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for value in self.crossword.variables:
            if value in assignment.keys():
                if assignment[value] is None:
                    return False
            else:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable, word in assignment.items():
            if word and len(word) != variable.length:
                return False

            neighbors = self.crossword.neighbors(variable).copy()

            for n in neighbors:
                # check if the neighbor filled or not
                if n in assignment.keys():
                    neighbor = assignment[n]
                    overlap = self.crossword.overlaps[(variable, n)]
                    if overlap is not None:
                        variable_overlap_index, neighbor_overlap_index = overlap

                        # check for conflict
                        if word[variable_overlap_index] != neighbor[neighbor_overlap_index]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        unassigned_variable_neighbors = [
            n for n in self.crossword.neighbors(var) if n not in assignment.keys()]

        def sort_domain(value):
            eliminated = 0
            for n in unassigned_variable_neighbors:

                xoverlap, yoverlap = self.crossword.overlaps[var, n]

                for neighbor_word in self.domains[n]:
                    if value[xoverlap] != neighbor_word[yoverlap]:
                        eliminated += 1

            return eliminated

        raw_domain = list(self.domains[var])
        ordered_domain = sorted(raw_domain, key=sort_domain)
        return ordered_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = []
        for variable in self.domains.keys():
            self.order_domain_values(variable, assignment=assignment)
            if variable not in assignment.keys():
                variables.append(variable)

        variables = sorted(variables, key=lambda x: len(self.domains[x]))
        return variables[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        try:
            if self.assignment_complete(assignment=assignment):
                return assignment
            var = self.select_unassigned_variable(assignment=assignment)
            for value in self.domains[var]:
                assignment[var] = value
                if self.consistent(assignment=assignment):
                    assignment[var] = value
                    result = self.backtrack(assignment=assignment)
                    if result is not None:
                        return assignment
                del assignment[var]
            return None
        except Exception as e:
            print(e)
            return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
