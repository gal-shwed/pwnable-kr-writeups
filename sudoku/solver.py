from board import SudokuBoard
from cell import CannotProposeCell


class SudokuSolver:
    def __init__(self, raw_board, rule_cells, rule_sum, is_rule_bigger):
        self.board = SudokuBoard(raw_board, rule_cells, rule_sum, is_rule_bigger)

    def solve_board(self):
        cell_location = self.board.find_unassigned_location()
        if not cell_location:  # Board is full
            return self.board.are_rules_satisfied()

        self.board.mark_location_assignment(cell_location[0], cell_location[1], is_assigned=True)
        try:
            while True:
                self.board.try_new_value_in_cell(cell_location[0], cell_location[1])
                if self.solve_board():
                    return True
        except CannotProposeCell:
            pass

        self.board.mark_location_assignment(cell_location[0], cell_location[1], is_assigned=False)
        return False
