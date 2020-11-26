#include <openssl/crypto.h>
#include <openssl/sha.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

#define MAX_NAME_LENGTH 100
#define MAX_TOKEN_LENGTH 1024

unsigned char key[SHA256_DIGEST_LENGTH];
#define KEY_SIZE SHA256_DIGEST_LENGTH

unsigned char* SHA(const unsigned char* data, size_t data_len, unsigned char* md)
{
	SHA256_CTX ctx;
	SHA256_Init(&ctx);
	SHA256_Update(&ctx, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", 64);
	for (int i = 0; i < 8; i++)
		ctx.h[i] = htobe32(*(SHA_LONG*)(key+i*sizeof(SHA_LONG)));
	ctx.md_len = SHA256_DIGEST_LENGTH;
	SHA256_Update(&ctx, data, data_len);
	SHA256_Final(md, &ctx);
}

int main(int argc, char** argv)
{
	unsigned char md[SHA256_DIGEST_LENGTH];
	if (argc != 3)
	{
		printf("[-] Usage : %s <InitialState> <data>\nInitialState:\tThe internal state of the sha256 hash function initially\ndata:\tThe data to hash\n", argv[0]);
		exit(1);
	}
	char s[3] = {0};
	for (size_t i = 0; i < strlen(argv[1]); i++)
	{
		*s = argv[1][2*i];
		s[1] = argv[1][2*i+1];
		key[i] = (unsigned char) strtol(s, NULL, 16);
	}
	
	SHA(argv[2], strlen(argv[2]), &md); // hash the data
	
	for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
		printf("%02x", (unsigned char)md[i]);
	printf("\n");
	
	//SHmAc_LoadKey();
	//disable_buffering();
}
