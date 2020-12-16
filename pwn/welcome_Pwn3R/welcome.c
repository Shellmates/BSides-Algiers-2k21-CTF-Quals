#include <stdio.h>

void setup(void);
void secret(void);

int main(int argc, char *argv[]) {
  long v1 = 0;
  int v2 = 0;
  char *v3 = NULL;
  int v4 = 0;
  char buf[0x20];

  setup();

  printf("Welcome Pwn3R!!\n");
  printf("I suppose you have something for me : ");
  gets(buf);

  return 0;
}

void setup(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

void secret(void) {
  asm(
    ".intel_syntax noprefix\n"
    "mov rax, 0x88f1d994a2b48cd0\n"
    "mov rdi, 0x8899aabbccddeeff\n"
    "xor rax, rdi\n"
    "push rax\n"
    "mov rdi, rsp\n"
    "xor rsi, rsi\n"
    "xor rdx, rdx\n"
    "mov rax, 0x1337\n"
    "xor rax, 0x130c\n"
    "syscall"
  );
}
