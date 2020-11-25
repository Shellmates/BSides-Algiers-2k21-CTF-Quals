#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#define MAX_SIZE 0x30

void setup(void);
void l33t_banner(void);
int read_num(char *msg);
void read_str(char *msg, char *buf, unsigned int max_size);
unsigned int random_num(unsigned int min, unsigned int max);
void l33t(void);

int main(int argc, char *argv[]) {
  unsigned int min, max, num;

  setup();

  srand(time(NULL));

  printf("so u w4nna j0in the l33t club huh.. pr0ve yours3lf f1rst!\n");
  printf("th1nking ab0ut som3 5tuff.. c4n u h4ck 1nto my m1nd?\n\n");

  for (int i = 0; i < 5; i++) {
    min = random_num(0x0, 0x1337);
    max = min + random_num(0x0, 0x1337);
    num = random_num(min, max);

    if (read_num("> ") != num) {
      printf("nahh..");
      exit(1);
    }
  }

  l33t();
  
  return EXIT_SUCCESS;
}

void setup(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

void l33t_banner(void) {
  printf("\n\
  $$\\   $$$$$$\\   $$$$$$\\  $$$$$$$$\\ \n\
$$$$ | $$ ___$$\\ $$ ___$$\\ \\____$$  |\n\
\\_$$ | \\_/   $$ |\\_/   $$ |    $$  / \n\
  $$ |   $$$$$ /   $$$$$ /    $$  /  \n\
  $$ |   \\___$$\\   \\___$$\\   $$  /   \n\
  $$ | $$\\   $$ |$$\\   $$ | $$  /    \n\
$$$$$$\\\\$$$$$$  |\\$$$$$$  |$$  /     \n\
\\______|\\______/  \\______/ \\__/\n\n");
}

int read_num(char *msg) {
  char buf[12] = {'\0'};

  read_str(msg, buf, 12);
  return atoi(buf);
}

void read_str(char *msg, char *buf, unsigned int max_size) {
  ssize_t read_count;

  printf("%s", msg);
  read_count = read(STDIN_FILENO, buf, max_size-1);
  buf[(int)read_count] = '\0';
}

unsigned int random_num(unsigned int min, unsigned int max) {
  unsigned int a, b, num;

  a = min + rand() % (max+1 - min);
  b = min + rand() % (max+1 - min);
  num = (a ^ b) % (max+1);
  srand(num);

  return num;
}

void l33t(void) {
  int size;
  char name[MAX_SIZE] = {'\0'};

  l33t_banner();

  size = read_num("Enter size: ");
  if (size == 1337) {
    fprintf(stderr, "That's cool, but still, too much for us to handle!\n");
    exit(1);
  }
  if (size > MAX_SIZE-1) {
    fprintf(stderr, "Too much for us to handle!\n");
    exit(1);
  }

  read_str("Enter name: ", name, size+1);

  printf("Welcome to the l33t club %s !\n", name);
}
