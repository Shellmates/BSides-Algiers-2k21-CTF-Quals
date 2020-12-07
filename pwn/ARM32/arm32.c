#include <stdio.h>

void setup(void);
void vuln(void);
void _gadgets(void);

int main(int argc, char *argv[]) {
  setup();

  vuln();

  return 0;
}

void setup(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

void vuln(void) {
  char buf[0x20];

  printf("plz no bof :'(\n");
  gets(buf);
}

void _gadgets(void) {
  asm(
    "bx sp\n"
    "blx sp\n"
  );
}
