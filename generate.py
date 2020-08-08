import sys

from crossword import *


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
                        w, h = draw.textsize(letters[i][j], font=font)
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

        # Loop through variables
        for variable, domain in self.domains.items():
            variable_length = variable.length

            delete_list = []

            # Loop through domain
            for x in domain:
                if len(x) != variable_length:
                    delete_list.append(x)
            
            for x in delete_list:
                self.domains[variable].remove(x)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        revised = False

        # Check for overlaping
        overlaping = self.crossword.overlaps[x, y]
        if not overlaping: return revised

        x_overlap = overlaping[0]
        y_overlap = overlaping[1]
        consistent_values = set()
        non_consistent_values = set()

        # Loop through x values looking for arc consistency with y
        for x_value in self.domains[x]:
            for y_value in self.domains[y]:
                if x_value[x_overlap] == y_value[y_overlap]:
                    consistent_values.add(x_value)

        # Remove non arc consistent values
        for value in self.domains[x]:
            if value not in consistent_values:
                non_consistent_values.add(value)

        if non_consistent_values:
            revised = True

        for value in non_consistent_values:
            self.domains[x].remove(value)

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # If arcs given, use it, otherwise use all the arcs in problem
        if arcs:
            queue = arcs

        else: 
            queue = []
            for pair, overlap in self.crossword.overlaps.items():
                if overlap:
                    queue.append(tuple(pair))

        # Loop until queue no longer has arcs
        while queue:

            # Remove arc from queue
            popped_element = queue.pop(0)
            
            # Revise pair
            x = popped_element[0]
            y = popped_element[1]

            if self.revise(x, y):

                # Break if problem is not solvable
                if len(self.domains[x]) == 0:
                    return False

                # Add x's neighbors to queue (except y)
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        queue.append((neighbor, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for value in assignment.values():
            if not value:
                return False
            
        return True
            

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        current_values = []

        # Check for correct length
        for var, value in assignment.items():
            current_values.append(value)
            if var.length != len(value):
                return False

        # Check that all values are distinct
        if len(current_values) != len(set(current_values)): return False

        # Check conflicts between neighbors
        for var, value in assignment.items():

            for neighbor in self.crossword.neighbors(var):

                # Make sure neighbor is part of assigment
                if neighbor in assignment:

                    # Ensure onverlapped letters are equal 
                    overlaping = self.crossword.overlaps[var, neighbor]
                    var_overlap = overlaping[0]
                    neighbor_overlap = overlaping[1]

                    if value[var_overlap] != assignment[neighbor][neighbor_overlap]:
                        return False
                   
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        least_constraining = dict()

        # Var domain
        var_domain = self.domains[var]

        # Define each variable's heuristic
        for value in var_domain:
    
            heuristic = 0

            for neighbor in self.crossword.neighbors(var):

                if neighbor not in assignment.keys():

                    # Overlap
                    overlaping = self.crossword.overlaps[var, neighbor]
                    var_overlap = overlaping[0]
                    neighbor_overlap = overlaping[1]

                    # Loop neighbor values
                    for neighbor_value in self.domains[neighbor]:

                        if value[var_overlap] == neighbor_value[neighbor_overlap]:

                            heuristic = heuristic + 1

            # Add value's heuristic to dict
            least_constraining[value] = heuristic

        # Sorted list
        least_constraining_list = sorted(least_constraining, key=least_constraining.get)

        return least_constraining_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Key: variables, value: length of domain
        unassigned_vars = dict()

        # Populate the dic of unassigned variables
        for variable, domain in self.domains.items():
            if variable not in assignment:
                unassigned_vars[variable] = len(domain)

        # Get the variable with the smallest domain (or one of the) and length of domain
        smallest_variable = min(unassigned_vars, key=unassigned_vars.get)
        smallest_domain_length = unassigned_vars[smallest_variable]

        # Create a list with tied variables for smallest domain (heuristic 1)
        smallest_group = []

        for variable, length in unassigned_vars.items():
            if length == smallest_domain_length:
                smallest_group.append(variable)

        # Select variable with largest degree
        if len(smallest_group) > 1:

            best_var = None
            largest_degree = 0
            
            # Loop through tied variables a find the one with the most neighbors (heuristic 2)
            for tied_var in smallest_group:
                var_neighbors = self.crossword.neighbors(tied_var)
                if len(var_neighbors) > largest_degree:
                    best_var = tied_var

            # Return var with the most neighbors or just the first one in the smallest_group
            if best_var: 
                return best_var
            else:
                return smallest_group[0]

        # Only one variable in smallest group
        else:
            return smallest_variable


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Assigment is complete
        if len(self.domains) == len(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Try diffenrent values for variable
        for value in self.order_domain_values(var, assignment):

            assignment[var] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)

                if result != None: return result

            del assignment[var]

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
