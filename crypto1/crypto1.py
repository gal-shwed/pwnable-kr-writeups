from pwn import *


class CryptoExploit(object):

    POSSIBLE_CHARS = "1234567890abcdefghijklmnopqrstuvwxyz_"
    BLOCK_SIZE = 16

    def __init__(self) -> None:
        self.cookie = ""

    @staticmethod
    def get_encrypted_data(filler_id, filler_pw=""):
        shell = remote('pwnable.kr', 9006)
        shell.recv()
        shell.sendline(filler_id)
        shell.recv()
        shell.sendline(filler_pw)
        encrypted_data_response = str(shell.recv())
        shell.close()
        return encrypted_data_response[encrypted_data_response.find("(") + 1:encrypted_data_response.find(")")]

    def find_next_cookie_char(self):
        required_id_length = (self.BLOCK_SIZE - len(self.cookie) - 3) % self.BLOCK_SIZE
        num_interesting_blocks = math.ceil((len(self.cookie) + 3) / self.BLOCK_SIZE)
        interesting_encrypted_data_offset = self.BLOCK_SIZE * 2 * num_interesting_blocks
        filler_id = "a" * required_id_length
        desired_encrypted_data = self.get_encrypted_data(filler_id)
        for c in self.POSSIBLE_CHARS:
            filler_pw = "-" + self.cookie + c
            bruteforce_encrypted_data = self.get_encrypted_data(filler_id, filler_pw)
            if desired_encrypted_data[:interesting_encrypted_data_offset] == \
                    bruteforce_encrypted_data[:interesting_encrypted_data_offset]:
                return c

    def run(self):
        while True:
            next_cookie_char = self.find_next_cookie_char()
            if next_cookie_char:
                self.cookie += next_cookie_char
                print("Cookie so far:", self.cookie)
            else:
                print("Found cookie:", self.cookie)
                return


if __name__ == '__main__':
    CryptoExploit().run()
