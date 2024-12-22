from consts import BOARD_LENGTH


class CannotProposeCell(Exception):
    pass


class SudokuCell:
    def __init__(self, cell_value, is_cell_in_rules, is_rule_bigger):
        self.cell_value = cell_value
        self.is_cell_in_rules = is_cell_in_rules
        self.is_rule_bigger = is_rule_bigger
        self.is_cell_editable = True if cell_value == 0 else False
        self.is_cell_assigned = False

    def propose_cell_value(self):
        assert self.is_cell_editable, "You cannot edit a non-editable cell"

        # Reserve large values for cells in rules
        if self.is_cell_in_rules and self.is_rule_bigger:
            proposed_value = self.cell_value = (self.cell_value - 1) % (BOARD_LENGTH + 1)
        else:
            proposed_value = self.cell_value = (self.cell_value + 1) % (BOARD_LENGTH + 1)

        if proposed_value > 0:
            self.cell_value = proposed_value
        else:
            raise CannotProposeCell()
