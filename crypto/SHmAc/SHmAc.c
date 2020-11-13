#include <openssl/crypto.h>
#include <openssl/sha.h>
#include <b64/cencode.h>
#include <b64/cdecode.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <endian.h>

// gcc SHmAc.c -o SHmAc -Wl,-z,relro,-z,now -fstack-protector -lcrypto -lb64


#define MAX_NAME_LENGTH 100
#define MAX_TOKEN_LENGTH 1024
#define KEY_SIZE SHA256_DIGEST_LENGTH

unsigned char key[SHA256_DIGEST_LENGTH];

typedef struct TOKEN_STRUCT {
	char username[MAX_NAME_LENGTH];
	unsigned long expiry_date;
	char isadmin;
} TOKEN_STRUCT;
char colors = 1;


void remove_newlines(unsigned char* input)
{
	int i, j;
	for (i = 0, j = 0; j < strlen(input); i++, j++)
	{
		if (input[j] == '\n')
			j++;
		input[i] = input[j];
	}
	input[i] = '\0';
}

void file_print_content(const char* path)
{
	char c;
	if (!access(path, R_OK))
	{
		int fd = open(path, O_RDONLY, 0);
		while (read(fd, &c, 1)) write(1, &c, 1);
		close(fd);
		c = '\n';
		write(1, &c, 1);
	}
}

char* base64_encode(unsigned char* input, size_t len)
{
	size_t output_len = len * 3; // base64(x) never exceeds 3*len(x) in length
	char* output = (char*)malloc(output_len);
	base64_encodestate state;
	base64_init_encodestate(&state);
	int c = base64_encode_block(input, len, output, &state);
	c += base64_encode_blockend(output+c, &state);
	output[c] = '\0';
	remove_newlines(output);
	return output;
}

char* base64_decode(unsigned char* input, size_t* size)
{
	int len;
	for (len = 0; len < strlen(input); len++)
		if (
			(input[len] < 'a' || input[len] > 'z') &&
			(input[len] < 'A' || input[len] > 'Z') &&
			(input[len] < '0' || input[len] > '9') &&
			(input[len] != '+' && input[len] != '/' && input[len] != '=')
		) break;
	
	char* output = (char*)malloc(len);
	base64_decodestate state;
	base64_init_decodestate(&state);
	int c = base64_decode_block(input, len, output, &state);
	if (size != NULL)
		*size = c;
	output[c] = '\0';
	return output;
}
void SHmAc_LoadKey()
{
	memset(key, 0, SHA256_DIGEST_LENGTH);
	int fd = open("/SHmAc_key", O_RDONLY, 0);
	if (fd == -1)
	{
		printf("[-] Error: /SHmAc_key not found\n");
		exit(1);
	}
	for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
		if (!read(fd, key+i, 1)) break;
}

int SHmAc_Init(SHA256_CTX* ctx, SHA_LONG* key)
{
	memset(ctx, 0, sizeof(*ctx));
	for (int i = 0; i < 8; i++)
		ctx->h[i] = key[i];
	ctx->md_len = SHA256_DIGEST_LENGTH;
	return 1;
}

unsigned char* SHmAc(const unsigned char* data, const unsigned char* key, size_t data_len, size_t key_len)
{
	if (key_len > SHA256_DIGEST_LENGTH)
		return NULL;
	SHA256_CTX ctx;
	unsigned char md[SHA256_DIGEST_LENGTH]; // will hold the result
	unsigned char key_local[SHA256_DIGEST_LENGTH];
	for (int i = 0; i < key_len; i++)
		key_local[i] = key[i];
	for (int i = key_len; i < SHA256_DIGEST_LENGTH; i++)
		key_local[i] = 0;
	
	SHmAc_Init(&ctx, (SHA_LONG*) &key_local);
	SHA256_Update(&ctx, data, data_len);
	SHA256_Final(md, &ctx);
	//OPENSSL_cleanse(&ctx, sizeof(ctx));
	return base64_encode(md, SHA256_DIGEST_LENGTH);
}

void disable_buffering()
{
	setvbuf(stdout, NULL, _IONBF, 0);
}

void print_menu()
{
	printf("[1] Register\n[2] Login\n[3] %s colored output\n[_] Exit\n", colors ? "Disable" : "Enable");
}


void infos()
{
	
}
void registation()
{
	unsigned char username[MAX_NAME_LENGTH];
	unsigned char token[MAX_TOKEN_LENGTH];
	memset(username, 0, MAX_NAME_LENGTH);
	printf("> Enter your username: ");
	fgets(username, MAX_NAME_LENGTH, stdin);
	
	for (int i = 0; i < MAX_NAME_LENGTH; i++)
		if ((username[i] < 'a' || username[i] > 'z') &&
			(username[i] < 'A' || username[i] > 'Z') &&
			(username[i] < '0' || username[i] > '9') &&
			username[i] != '_' && username[i] != '@'
		)
		{
			username[i] = '\0';
			break;
		}
	snprintf(token, sizeof(token), "|user:%s|admin:0|expires:%lu|", username, (unsigned long) time(NULL)+180);
	char* encoded_token = base64_encode(token, strlen(token));
	char* mac = SHmAc(token, key, strlen(token), KEY_SIZE);
	if (colors)
		printf("[\e[0;94;49m*\e[0m] Generating your token, please wait\n");
	else
		printf("[*] Generating your token, please wait\n");
	sleep(2);
	if (colors)
		printf("Your access token : \e[0;94;49m%s.%s\e[0m\nIt's valid for \e[0;91;49m3\e[0m minutes only!\n\n", encoded_token, mac);
	else
		printf("Your access token : %s.%s\nIt's valid for 3 minutes only!\n\n", encoded_token, mac);
	free(encoded_token);
	free(mac);
}
int parse_token(unsigned char* token, size_t len, TOKEN_STRUCT* info)
{
	memset(info->username, 0, sizeof(info->username));
	info->expiry_date = 0;
	info->isadmin = 0;
	char found_username = 0, found_isadmin = 0, found_expirydate = 0;
	int i = 1;
	while (i < len)
	{
		if (!strncmp(token+i, "user:", 5))
		{
			//printf("[+] found user : %s\n", token+i+5);
			i += 5;
			int j = 0;
			while (i < len && token[i] != '|')
				info->username[j++] = token[i++];
			found_username = 1;
		}
		else if (!strncmp(token+i, "admin:", 6))
		{
			//printf("[+] found admin\n");
			i += 6;
			if (i >= len) return 0;
			if (token[i] == '0')
				info->isadmin = 0;
			else if (token[i] == '1')
				info->isadmin = 1;
			else
			{
				printf("[-] isadmin property should hold 1 or 0\n");
				return 0;
			}
			found_isadmin = 1;
		}
		else if (!strncmp(token+i, "expires:", 8))
		{
			//printf("[+] found expires\n");
			i += 8;
			if (i >= len) return 0;
			info->expiry_date = strtoul(token+i, NULL, 10);
			while (token[i] >= '0' && token[i] <= '9') i++;
			found_expirydate = 1;
		}
		//printf("remains %s\n", token+i);
		while (i < len && token[i++] != '|');
	}
	if (!found_username || !found_isadmin || !found_expirydate)
		return 0;
	return 1;
}
void toggle_colors()
{
	colors = !colors;
}

void login()
{
	size_t len_token;
	printf("> Enter your token: ");
	char token[MAX_TOKEN_LENGTH];
	fgets(token, MAX_TOKEN_LENGTH, stdin);
	if (token[strlen(token)-1] == '\n')
		token[strlen(token)-1] = '\0';
	size_t mac_part;
	for (mac_part = 0; token[mac_part] && token[mac_part] != '.'; mac_part++);
	if (!token[mac_part])
	{
		if (colors)
			printf("\n\n\e[0;91;49mo-O-o                o      o      o      o             \n  |                  | o    |      |      | /           \n  |   o-o  o   o  oo |    o-O     -o- o-o OO   o-o o-o  \n  |   |  |  \\ /  | | | | |  |      |  | | | \\  |-' |  | \no-O-o o  o   o   o-o-o |  o-o      o  o-o o  o o-o o  o \n                                                        \n                                                        \n\e[0m\n\n");
		else
			printf("[-] Invalid token\n");
		return;
	}
	char* decoded_token = base64_decode(token, &len_token);
	char* given_mac = token+mac_part+1;
	unsigned char* correct_mac = SHmAc(decoded_token, key, len_token, KEY_SIZE);

	if (!strcmp(given_mac, correct_mac))
	{
		if (colors)
			printf("[\e[0;94;49m*\e[0m] Parsing token, please wait ...\n");
		else
			printf("[*] Parsing token, please wait ...\n");
		sleep(2);
		TOKEN_STRUCT user_info;
		if (!parse_token(decoded_token, len_token, &user_info))
			return;
		unsigned long time_now = (unsigned long) time(NULL);
		if (colors)
			printf("Token: \n{\n\tusername : \e[0;94;49m%s\e[0m\n\tisadmin : %s\n\texpiry_date : %s%lu\e[0m\n}\n\n", user_info.username, user_info.isadmin ? "\e[0;92;49m1\e[0m" : "\e[0;91;49m0\e[0m", time_now > user_info.expiry_date ? "\e[0;91;49m" : "\e[0;92;49m", user_info.expiry_date);
		else
			printf("Token: \n{\n\tusername : %s\n\tisadmin : %d\n\texpiry_date : %lu\n}\n\n", user_info.username, user_info.isadmin, user_info.expiry_date);

		if (time_now > user_info.expiry_date)
			if (colors)
				printf("\n\n\e[0;91;49mo--o                       o      o      o             \n|             o            |      |      | /           \nO-o  \\ / o-o    o-o o-o  o-O     -o- o-o OO   o-o o-o  \n|     o  |  | | |   |-' |  |      |  | | | \\  |-' |  | \no--o / \\ O-o  | o   o-o  o-o      o  o-o o  o o-o o  o \n         |                                             \n         o                                             \n\e[0m\n\n");
			else
				printf("[-] Expired token !\n");
		else
		{
			if (colors)
				printf("[\e[0;92;49m+\e[0m] Welcome %s\n", user_info.username);
			else
				printf("[+] Welcome %s\n", user_info.username);
			if (user_info.isadmin)
			{
				if (colors)
					printf("\n\n\e[0;92;49mo   o                                     o              \n \\ /                                      |       o      \n  O   o-o o  o      oo o-o o-o      oo  o-O o-O-o   o-o  \n  |   | | |  |     | | |   |-'     | | |  | | | | | |  | \n  o   o-o o--o     o-o-o   o-o     o-o- o-o o o o | o  o \n                                                         \n                                                         \n\e[0m\n\n");
				else
					printf("[+] You are admin\n");
				sleep(1);
				file_print_content("/flag.txt");
			}
			else
			{
				if (colors)
					printf("\n\n\e[0;93;49mo   o      o                          o              \n|\\  |      |                          |       o      \n| \\ | o-o -o-      oo o-o       oo  o-O o-O-o   o-o  \n|  \\| | |  |      | | |  |     | | |  | | | | | |  | \no   o o-o  o      o-o-o  o     o-o- o-o o o o | o  o \n                                                     \n                                                     \n\e[0m\n\n");
				else
					printf("[-] Not an admin!\n");
				sleep(1);
				if (colors)
					printf("\n[\e[0;91;49m-\e[0m] Nothing interesting here for now, only the admin can read the flag\n\n");
				else
					printf("\n[-] Nothing interesting here for now, only the admin can read the flag\n\n");
			}
		}
	}
	else
	{
	if (colors)
		printf("\n\n\e[0;91;49mo-O-o                o      o      o      o             \n  |                  | o    |      |      | /           \n  |   o-o  o   o  oo |    o-O     -o- o-o OO   o-o o-o  \n  |   |  |  \\ /  | | | | |  |      |  | | | \\  |-' |  | \no-O-o o  o   o   o-o-o |  o-o      o  o-o o  o o-o o  o \n                                                        \n                                                        \n\e[0m\n\n");
	else
		printf("[-] Invalid token\n");
	}
	free(correct_mac);
	free(decoded_token);
}


int main()
{
	SHmAc_LoadKey();
	disable_buffering();
	char user_input[8];
	while (1)
	{
		print_menu();
		fgets(user_input, sizeof(user_input), stdin);
		int choice = atoi(user_input);
		if (choice == 1)
			registation();
		else if (choice == 2)
			login();
		else if (choice == 3)
			toggle_colors();
		else
			exit(0);
	}
}
