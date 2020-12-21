#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

extern uint32_t f(uint16_t x);
/*{
	return x1 * sqrt(y)
}*/

uint32_t hash[] = {
0x4a856f35,
0x4a8d10ca,
0x4a8f1369,
0x4a9cef82,
0x4a9af2dc,
0x4a81adfa,
0x4a456e0a,
0x4a7034e9,
0x495c0e39,
0x4a8f05ae,
0x49ad8381,
0x4a693752,
0x4a692156,
0x4a704b1d,
0x4a86e3a2,
0x4a98f05a,
0x4a9ceb77,
0x4a705637,
0x4a690f05,
0x4a7f68f3,
0x4a9488c7,
0x4a7f59d7,
0x4a9ceb77,
0x49ada321,
0x4a8b2fb1,
0x44aeb15c};
int main(int argc, char* argv[])
{
	if (argc != 2)
	{
		printf("[-] Usage: %s input\n", argv[0]);
		return 1;
	}
	
	char* input = argv[1];
	int len = strlen(input);
	
	if (len > 52)
	{
		printf("[-] Wrong input\n");
		return 1;
	}
	
	for (int i = 0; i < len/2; i++)
	{
		if (f(*(uint16_t*)(input+2*i)) != hash[i])
		{
			printf("[-] Wrong input\n");
			return 1;
		}
		/*printf("f(%p) = %p\n", *(uint16_t*)(input+2*i), \
			f(*(uint16_t*)(input+2*i))
		);*/
	}
	printf("[+] Congrats, correct input\n");
}
