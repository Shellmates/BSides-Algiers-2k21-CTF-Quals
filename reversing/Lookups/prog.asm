
.global f

f:
	push %rbp
	mov %rbp, %rsp
	sub %rsp, 16
	mov dword ptr[%rbp-12],%edi
	fild dword ptr[%rbp-12]
	fld %st(0)
	fsqrt
	fmulp
	fstp dword ptr[%rbp-12]
	mov %eax, [%rbp-12]
	mov %rsp, %rbp
	pop %rbp
	ret
