import ast

from pwn import *

from consts import BOARD_LENGTH
from solver import SudokuSolver


class PwnSudoku:
    NUM_STAGES = 100

    def __init__(self):
        self.shell = remote("pwnable.kr", 9016)
        self.solver = None
        self.current_stage = 1

    def get_board(self):
        self.shell.recvuntil(f"Stage {self.current_stage}\n")
        self.shell.recvline()
        board = [ast.literal_eval(self.shell.recvline().decode()) for _ in range(BOARD_LENGTH)]
        print("Received board: ")
        pprint(board)
        return board

    def get_rule(self):
        self.shell.recvuntil("rule -\n")
        rule_header = self.shell.recvline().decode()
        rule_sum = int(re.search(r"\d+", rule_header).group())
        is_rule_bigger = True if "bigger" in rule_header else False
        rule_cells = []
        while True:
            rule_cell = tuple(map(int, re.findall(r"\d+", self.shell.recvline().decode())))
            if rule_cell:
                rule_cells.append(rule_cell)
            else:
                break

        print(f"Rule sum: Should be {'bigger' if is_rule_bigger else 'smaller'} than {rule_sum}")
        print(f"Rule cells: {rule_cells}")

        rule_cells = [(i - 1, j - 1) for i, j in rule_cells]
        return rule_cells, rule_sum, is_rule_bigger

    def prepare_game(self):
        board = self.get_board()
        rule_cells, rule_sum, is_rule_bigger = self.get_rule()
        self.solver = SudokuSolver(board, rule_cells, rule_sum, is_rule_bigger)

    def solve_board(self):
        self.solver.solve_board()
        print("Solved board:")
        self.solver.board.print_board()
        self.shell.sendline(str(self.solver.board))

    def solve_single_level(self):
        print(f"Solving stage {self.current_stage}")
        self.prepare_game()
        self.solve_board()
        self.current_stage += 1

    def run(self):
        self.shell.sendline("\n")
        for _ in range(self.NUM_STAGES):
            self.solve_single_level()
        self.shell.interactive()


if __name__ == '__main__':
    PwnSudoku().run()
