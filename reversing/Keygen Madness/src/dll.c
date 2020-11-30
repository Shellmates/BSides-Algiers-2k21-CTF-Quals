#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <ntstatus.h>
#define ERR goto cleanup
#define USERNAME_LEN 16

DWORD g5UNkB6(PBYTE dest, PBYTE src) // aes(data=const, key=username)
{
	// dest = aes(const, key=src)
	BCRYPT_ALG_HANDLE alg_handle;
	BCRYPT_HASH_HANDLE key_handle;
	ULONG temp;
	DWORD digest_size;
	DWORD key_size;
	DWORD success = 0;
	unsigned char const_buffer[16];
	for (int i = 0; i < 16; i++) const_buffer[i] = i+1;
	if (BCryptOpenAlgorithmProvider(&alg_handle, BCRYPT_AES_ALGORITHM, NULL, 0))
	{
		//MessageBox(0, "Err", "[-] BCryptOpenAlgorithmProvider\n", 0);
		ERR;
	}
	if (BCryptGetProperty(alg_handle, BCRYPT_OBJECT_LENGTH, (PUCHAR) &key_size, sizeof(DWORD), &temp, 0))
	{
		//MessageBox(0, "Err", "[-] BCryptGetProperty\n", 0);
		ERR;
	}

	if (BCryptGetProperty(alg_handle, BCRYPT_BLOCK_LENGTH, (PUCHAR) &digest_size, sizeof(DWORD), &temp, 0))
	{
		//MessageBox(0, "Err", "[-] BCryptGetProperty\n", 0);
		ERR;
	}
	
	PBYTE key_object = HeapAlloc( GetProcessHeap(), 0, key_size );
	if (!key_object)
	{
		//MessageBox(0, "Err", "[-] HeapAlloc\n", 0);
		ERR;
	}
	
	if (BCryptGenerateSymmetricKey(alg_handle, &key_handle, key_object, key_size, src, USERNAME_LEN, 0))
	{
		//MessageBox(0, "Err", "[-] BCryptGenerateSymmetricKey\n", 0);
		ERR;
	}
	NTSTATUS x;
	BYTE tmp_dst[32];
	if (x=BCryptEncrypt(key_handle, const_buffer, 16, NULL, NULL, 0, tmp_dst, sizeof(tmp_dst), &temp, BCRYPT_PAD_NONE))
	{
		//MessageBox(0, "Err", "[-] BCryptEncrypt\n", 0);
		/*
		switch (x)
		{
			case STATUS_BUFFER_TOO_SMALL: MessageBox(0, "Err", "STATUS_BUFFER_TOO_SMALL\n", 0);break;
			case STATUS_INVALID_BUFFER_SIZE: MessageBox(0, "Err", "STATUS_INVALID_BUFFER_SIZE\n", 0);break;
			case STATUS_INVALID_HANDLE: MessageBox(0, "Err", "STATUS_INVALID_HANDLE\n", 0); break;
			case STATUS_INVALID_PARAMETER: MessageBox(0, "Err", "STATUS_INVALID_PARAMETER\n", 0);break;
			case STATUS_NOT_SUPPORTED: MessageBox(0, "Err", "STATUS_NOT_SUPPORTED\n", 0);break;
		}
		*/
		ERR;
	}
	for (int i = 0; i < 16; i++)
		dest[i] = tmp_dst[i];
	success = 1;
	
	cleanup:
	
	if (alg_handle)
		BCryptCloseAlgorithmProvider(alg_handle, 0);

	if (key_handle)
		BCryptDestroyKey(key_handle);
	
	if (key_object)
		HeapFree( GetProcessHeap(), 0, key_object );
	
	return success;
}
DWORD CvY9Z5k(PBYTE dest, PBYTE src) // md5
{
	// dest = md5(src[0,len])
	BCRYPT_ALG_HANDLE alg_handle;
	BCRYPT_HASH_HANDLE hashobj_handle;
	DWORD temp;
	DWORD digest_size;
	DWORD hashobj_size;
	DWORD success = 0;
	if (BCryptOpenAlgorithmProvider(&alg_handle, BCRYPT_MD5_ALGORITHM, NULL, 0))
	{
		ERR;
	}
	if (BCryptGetProperty(alg_handle, BCRYPT_OBJECT_LENGTH, (PUCHAR) &hashobj_size, sizeof(DWORD), &temp, 0))
	{
		ERR;
	}

	if (BCryptGetProperty(alg_handle, BCRYPT_HASH_LENGTH, (PUCHAR) &digest_size, sizeof(DWORD), &temp, 0))
	{
		ERR;
	}
	
	PBYTE hash_object = HeapAlloc( GetProcessHeap(), 0, hashobj_size );
	if (!hash_object)
	{
		ERR;
	}
	
	if (BCryptCreateHash(alg_handle, &hashobj_handle, hash_object, hashobj_size, NULL, 0, 0))
	{
		ERR;
	}
	
	if (BCryptHashData(hashobj_handle, src, USERNAME_LEN, 0))
	{
		ERR;
	}
	
	if (BCryptFinishHash(hashobj_handle, dest, 16, 0))
	{
		ERR;
	}
	
	success = 1;
	
	cleanup:
	
	if (alg_handle)
		BCryptCloseAlgorithmProvider(alg_handle, 0);

	if (hashobj_handle)
		BCryptDestroyHash(hashobj_handle);
	
	if (hash_object)
		HeapFree( GetProcessHeap(), 0, hash_object );
	
	return success;
}

BYTE sbox1[32] = { 20, 14, 22, 11, 24, 13, 5, 9, 8, 28, 29, 1, 23, 30, 19, 4, 3, 16, 2, 31, 10, 17, 26, 21, 12, 7, 18, 6, 0, 25, 15, 27 };
BYTE sbox2[32] = { 9, 24, 19, 25, 10, 12, 2, 16, 4, 14, 6, 27, 22, 21, 30, 20, 26, 15, 28, 31, 7, 3, 13, 0, 18, 8, 11, 23, 17, 1, 29, 5 };

BYTE as_char(BYTE c)
{
	if (c < 26)
		return c + 'A';
	else
		return c + '0' - 26;
}

BYTE as_byte(BYTE c)
{
	if (c >= 'A' && c <= 'Z')
		return c - 'A';
	else if (c >= '0' && c <= '9')
		return c - '0' + 26;
}

__declspec( dllexport) BYTE mLfrZ9M(BYTE c)
{
	// sbox1
	return as_char(sbox1[as_byte(c)]);
}

__declspec( dllexport) BYTE Kl62FAJ(BYTE c)
{
	// sbox2
	return as_char(sbox2[as_byte(c)]);
}

__declspec( dllexport) DWORD KrkBeCT(PBYTE dest, PBYTE src)
{
	BYTE aes_buf[16];
	BYTE md5_buf[16];
	if (!g5UNkB6(aes_buf, src)) return 0; // aes
	if (!CvY9Z5k(md5_buf, src)) return 0; // md5
	for (int i = 0; i < 16; i++)
		dest[i] = aes_buf[i] ^ md5_buf[i];
	return 1;
}

/*
int main()
{
	char test[] = "aaaabbbbccccdddd";
	char output[16] = { 0 };
	if (!KrkBeCT(output, test))
	{
		printf("[-] error!\n");
		exit(1);
	}
	for (int i = 0; i < 16; i++)
		printf("%02x", (unsigned char) output[i]);
	printf("\n");
}
*/
