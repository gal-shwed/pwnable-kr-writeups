from pprint import pprint

from consts import BOARD_LENGTH, BLOCK_LENGTH
from cell import SudokuCell


class SudokuBoard:
    def __init__(self, raw_board, rule_cells, rule_sum, is_rule_bigger):
        self.board = raw_board
        self.rule_cells = rule_cells
        self.rule_sum = rule_sum
        self.is_rule_bigger = is_rule_bigger
        self.process_board()

    def process_board(self):
        for i in range(BOARD_LENGTH):
            for j in range(BOARD_LENGTH):
                is_cell_in_rules = True if (i, j) in self.rule_cells else False
                self.board[i][j] = SudokuCell(self.board[i][j], is_cell_in_rules=is_cell_in_rules,
                                              is_rule_bigger=self.is_rule_bigger)

    def find_unassigned_location(self):
        for i in range(BOARD_LENGTH):
            for j in range(BOARD_LENGTH):
                cell = self.board[i][j]
                if cell.is_cell_editable and not cell.is_cell_assigned:
                    return i, j

    def is_cell_assignment_safe(self, cell_row, cell_col):
        # Validate row and column
        assigned_value = self.board[cell_row][cell_col].cell_value
        for i in range(BOARD_LENGTH):
            if (i != cell_col and self.board[cell_row][i].cell_value == assigned_value) or \
                    (i != cell_row and self.board[i][cell_col].cell_value == assigned_value):
                return False

        # Validate block
        block_row, block_col = cell_row // BLOCK_LENGTH * 3, cell_col // BLOCK_LENGTH * 3
        for i in range(BLOCK_LENGTH):
            for j in range(BLOCK_LENGTH):
                if (cell_row != block_row + i or cell_col != block_col + j) and \
                        self.board[block_row + i][block_col + j].cell_value == assigned_value:
                    return False

        return True

    def try_new_value_in_cell(self, cell_row, cell_col):
        cell = self.board[cell_row][cell_col]
        while True:
            cell.propose_cell_value()
            if self.is_cell_assignment_safe(cell_row, cell_col):
                return

    def mark_location_assignment(self, cell_row, cell_col, is_assigned):
        self.board[cell_row][cell_col].is_cell_assigned = is_assigned

    def are_rules_satisfied(self):
        sum_rule_cells = sum(self.board[i][j].cell_value for i, j in self.rule_cells)
        if self.is_rule_bigger:
            return sum_rule_cells > self.rule_sum
        return sum_rule_cells < self.rule_sum

    def print_board(self):
        pprint([[self.board[i][j].cell_value for j in range(BOARD_LENGTH)] for i in range(BOARD_LENGTH)])

    def __str__(self):
        return str([[self.board[i][j].cell_value for j in range(BOARD_LENGTH)] for i in range(BOARD_LENGTH)])
