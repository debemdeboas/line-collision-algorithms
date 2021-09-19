from dataclasses import dataclass
from math import floor
from typing import List, Set, Tuple

from Linha import Linha


class Matrix:
    """
    Matrix class

    Divides the canvas into a `size_x` by `size_y` matrix and
    registers the objetcs that pass through each cell on the grid.
    """

    @dataclass
    class CellHelper:
        """
        Named tuple for x and y sizes for the matrix
        """
        x: float
        y: float


    @dataclass
    class Cell:
        """
        Cell class

        Contains a set of lines that pass through this
        cell on the matrix.
        """
        contained_lines: Set[int]

    def __init__(self, universe_size: Tuple[int, int], cell_amount: Tuple[int, int]) -> None:
        """
        Creates an instance of the Matrix class

        Args:
            universe_size (Tuple[int, int]): Maximum universe size. (x, y) tuple.
            cell_amount (Tuple[int, int]): Amount of entries per axis. (x, y) tuple.
        """

        self.matrix: List[List[Matrix.Cell]] = []
        self.cell_size = Matrix.CellHelper(universe_size[0] / cell_amount[0],
                                    universe_size[1] / cell_amount[1])
        self.size_x = floor(universe_size[0] / self.cell_size.x)
        self.size_y = floor(universe_size[1] / self.cell_size.y)

        for _ in range(self.size_x):
            y_list = []
            for _ in range(self.size_y):
                y_list.append(Matrix.Cell(set()))
            self.matrix.append(y_list)

    def register_line_on_cells(self, line: Linha, line_index: int):
        """
        Registers a line on its corresponding cells

        Args:
            line (Linha): Line whose coordinates are accessed
            line_index (int): Line index to be added to the corresponding cells
        """

        starting_cell_x = max(floor(line.minx / self.cell_size.x), 0)
        starting_cell_y = max(floor(line.miny / self.cell_size.y), 0)
        ending_cell_x = max(floor(line.maxx / self.cell_size.x), 0)
        ending_cell_y = max(floor(line.maxy / self.cell_size.y), 0)

        for x in range(starting_cell_x, ending_cell_x + 1):
            for y in range(starting_cell_y, ending_cell_y + 1):
                matrix_line = self.matrix[min(x, self.size_x - 1)]
                matrix_line[min(y, self.size_y - 1)].contained_lines.add(line_index)

    def generate_candidates(self, line_index: int, lines: List[Linha]) -> Set[int]:
        """
        Generates a set of possible intersection candidates for a given line

        Args:
            line_index (int): Line index to be accesed via the `lines` parameter
            lines (List[Linha]): Array of lines. Used to get a line object for the given index.

        Returns:
            Set[int]: 
                Set of possible intersection candidates for the given line.
                Does not contain itself.
        """

        line = lines[line_index]

        starting_cell_x = floor(line.minx / self.cell_size.x)
        starting_cell_y = floor(line.miny / self.cell_size.y)
        ending_cell_x = floor(line.maxx / self.cell_size.x)
        ending_cell_y = floor(line.maxy / self.cell_size.y)

        result_set: Set[int] = set()
        index_set: Set[int] = set()
        index_set.add(line_index)

        for x in range(starting_cell_x, ending_cell_x + 1):
            for y in range(starting_cell_y, ending_cell_y + 1):
                line = self.matrix[min(x, self.size_x - 1)]
                cell = line[min(y, self.size_y - 1)]
                for index in cell.contained_lines - index_set:
                    result_set.add(index)

        return result_set
