"""Implemention of the Maze ADT using a 2-D array."""
from arrays import Array2D
from lliststack import Stack


class Maze:
    """Define constants to represent contents of the maze cells."""
    MAZE_WALL = "*"
    PATH_TOKEN = "x"
    TRIED_TOKEN = "o"

    def __init__(self, num_rows, num_cols):
        """Creates a maze object with all cells marked as open."""
        self._maze_cells = Array2D(num_rows, num_cols)
        self._start_cell = None
        self._exit_cell = None

    def num_rows(self):
        """Returns the number of rows in the maze."""
        return self._maze_cells.num_rows()

    def num_cols(self):
        """Returns the number of columns in the maze."""
        return self._maze_cells.num_cols()

    def set_wall(self, row, col):
        """Fills the indicated cell with a "wall" marker."""
        assert row >= 0 and row < self.num_rows() and \
               col >= 0 and col < self.num_cols(), "Cell index out of range."
        self._maze_cells[row, col] = self.MAZE_WALL

    def set_start(self, row, col):
        """Sets the starting cell position."""
        assert row >= 0 and row < self.num_rows() and \
               col >= 0 and col < self.num_cols(), "Cell index out of range."
        self._start_cell = _CellPosition(row, col)

    def set_exit(self, row, col):
        """Sets the exit cell position."""
        assert row >= 0 and row < self.num_rows() and \
               col >= 0 and col < self.num_cols(), "Cell index out of range."
        self._exit_cell = _CellPosition(row, col)

    def __smart_push_to_stack(self, move: tuple[int], stc: "Stack") -> bool:
        """
        if the move is already in stack, deletes itself and adds to the begining
        """
        head = stc._top

        if head is None:
            stc.push(move)
            return
        if head.item == move:
            return
        while head.next:
            if head.next.item == move:
                head.next = head.next.next
                stc.push(move)
                return
            head = head.next
        stc.push(move)
        return

    def find_path(self):
        """
        Attempts to solve the maze by finding a path from the starting cell
        to the exit. Returns True if a path is found and False otherwise.
        """
        # start is wall
        if self._maze_cells[self._start_cell.row, self._start_cell.col] == '*':
            return False

        # strat is finish
        if self._exit_found(self._start_cell.row, self._start_cell.col):
            self._mark_path(self._start_cell.row, self._start_cell.col)
            return True

        path = Stack()
        moves = Stack()

        # start always belongs to path
        path.push((self._start_cell.row, self._start_cell.col))
        self._mark_tried(self._start_cell.row, self._start_cell.col)

        for move in self.__get_moves(path.peek()[0], path.peek()[1]):
            self.__smart_push_to_stack(move, moves)

        # if it is possible to make a move
        while moves:
            # makes move and pushes it to path
            mv_row, mv_col = moves.pop()
            if self._maze_cells[mv_row, mv_col] == self.TRIED_TOKEN:
                mv_row, mv_col = moves.pop()

            path.push((mv_row, mv_col))
            self._mark_tried(mv_row, mv_col)

            if self._exit_found(mv_row, mv_col):
                # marks path cells with PATH_TOKEN
                while path:
                    pth_row, pth_col = path.pop()
                    self._mark_path(pth_row, pth_col)
                return True

            # updates move
            pos_moves = self.__get_moves(mv_row, mv_col)

            if pos_moves:
                for move in pos_moves:
                    self.__smart_push_to_stack(move, moves)

            # if it is impossible to make a move deletes cells from path
            # till reaches the cell of last crossroad
            else:
                tr_row, tr_col = path.peek()

                # if moves empty, all cells are hecked
                if not moves:
                    return False

                while moves.peek() not in self.__get_moves(tr_row, tr_col):
                    path.pop()
                    if not path:
                        return False
                    tr_row, tr_col = path.peek()

        return False

    def __get_moves(self, row: int, col: int) -> tuple[tuple[int, int]]:
        """
        Gets information about all cells arround
        """
        moves = []
        for row_d, col_d in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            move = (row + row_d, col + col_d)
            if self._valid_move(move[0], move[1]):
                moves.append(move)

        return tuple(moves[::-1])


    def reset(self):
        """Resets the maze by removing all "path" and "tried" tokens."""
        for row in range(self.num_rows()):
            for col in range(self.num_rows()):
                if self._maze_cells[row, col] in (self.PATH_TOKEN, self.TRIED_TOKEN):
                    self._maze_cells[row, col] = None

    def __str__(self):
        """Returns a text-based representation of the maze."""
        maze_str = ''
        for row in range(self.num_rows()):
            line = ''
            for col in range(self.num_cols()):
                cell = self._maze_cells[row, col]
                if cell:
                    line += cell + ' '
                else:
                    line += '_ '

            maze_str += line + '\n'

        return maze_str[:-1]

    def _valid_move(self, row, col):
        """Returns True if the given cell position is a valid move."""
        return row >= 0 and row < self.num_rows() \
               and col >= 0 and col < self.num_cols() \
               and self._maze_cells[row, col] is None

    def _exit_found(self, row, col):
        """Helper method to determine if the exit was found."""
        return row == self._exit_cell.row and col == self._exit_cell.col

    def _mark_tried(self, row, col):
        """Drops a "tried" token at the given cell."""
        self._maze_cells[row, col] = self.TRIED_TOKEN

    def _mark_path(self, row, col):
        """Drops a "path" token at the given cell."""
        self._maze_cells[row, col] = self.PATH_TOKEN


class _CellPosition(object):
    """Private storage class for holding a cell position."""
    def __init__(self, row, col):
        self.row = row
        self.col = col
