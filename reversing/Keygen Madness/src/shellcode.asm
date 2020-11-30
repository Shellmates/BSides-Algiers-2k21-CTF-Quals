; getmodulehandle
; getprocaddress
; dllname
; start
call +5;
pop r13;
sub r13, 29;
mov rbp, rsp
and rsp, -16
mov qword[r13+0x10], 0
mov r14, rcx; r14 = argument
; get the handle to the injected DLL
mov rax, 0x6c6c642e;
push rax;
mov rax, 0x78637a4d7a457a4d;
push rax;
mov rcx, rsp;
sub rsp, 32
call [r13];
add rsp, 48
mov r12, rax ; r12 = GetModuleHandle(mydll)
; Separate the serial and the username
xor rcx, rcx
dec rcx
xor al, al
mov rdi, r14
repne scasb
lea r15, [r14+17]
cmp rcx, -48
jne wrong_serial
push 4
pop rcx
mov byte[r15-1], 0
push 5
pop rdi
xor al, al
check_dashes:
mov bl, 0x2d
xor bl, byte[r15+rdi]
or al, bl
add rdi, 6
loop check_dashes
test al, al
jnz wrong_serial
; get the address of the md5 function
mov rcx, r12
mov rax, 0x544365426b724b
push rax
mov rdx, rsp
sub rsp, 40
call [r13+8]
add rsp, 48
test rax, rax
jz error_occured
sub rsp, 16
mov rcx, rsp
mov rdx, r14
xor r8, r8
inc r8
shl r8, 4
sub rsp, 32
call rax
add rsp, 32
test rax, rax
jz error_occured
mov rsi, rsp
; rsi = digest
; r14 = username
; r15 = serial
; r13 = base
; r12 = GetModuleHandle(mydll)
while1:
    ; check if exiting loop
	mov rdi, [rsi]
	xor rcx, rcx ; j
	while2:
		cmp cl, 40
		jge outofloop2
		cmp byte [r15], 0
		jz outofloop1
		cmp byte[r15], 0x2d
		lea rax, [r15+1]
		cmove r15, rax
		mov rax, rdi
		shr rax, cl
		and rax, 0x1f
		mov r8, 22
		mov r9, 65
		cmp rax, 26
		cmovl r8, r9
		add rax, r8
		push rcx
		push rax
		mov rax, 0x4d395a72664c6d
		push rax
		mov rcx, r12
		mov rdx, rsp
		sub rsp, 40
		call [r13+8]
		add rsp, 48
		pop rcx
		sub rsp, 40
		call rax
		add rsp, 40
		; now, al = sbox1[c]
		push rax
		mov rax, 0x4a414632366c4b
		push rax
		mov rcx, r12
		mov rdx, rsp
		sub rsp,40
		call [r13+8]
		add rsp, 40
		xor rcx,rcx
		mov cl,[r15]
		sub rsp, 40
		call rax
		add rsp, 48
		pop rcx
		cmp al,cl
		jne wrong_serial
		pop rcx
		add cl, 5
		inc r15
		jmp while2
	outofloop2:
	add rsi, 5
	jmp while1
outofloop1:
mov qword[r13+0x10],1
jmp clean_ret
wrong_serial:
mov qword[r13+0x10],2
jmp clean_ret
error_occured:
mov qword[r13+0x10],3
clean_ret:
mov rsp, rbp
ret
