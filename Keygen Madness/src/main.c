#include <windows.h>
#include <psapi.h>
#include <stdio.h>
#include <winternl.h>
#define MYERR while(1){printf("ERROR! %d\n",GetLastError());Sleep(1000);break;}
#define SIZE_EXE 1134592
CONTEXT ctx;
typedef __int64 QWORD;

typedef LONG( WINAPI * NtUnmapViewOfSection )(HANDLE ProcessHandle, PVOID BaseAddress);
NtUnmapViewOfSection NtUnmapViewOfSection_fun;
char charset[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

char blob[] = "\x01\x02\x01\x01\x01\x01\x01\x01";

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

DWORD load_stage(PVOID* res)
{
	return load_res(blob+1, res);
}

DWORD load_dll(PVOID* res)
{
	return load_res(blob, res);
}

VOID hide_console()
{
	HWND hConsole = GetConsoleWindow();
	ShowWindow( hConsole, SW_MINIMIZE );
    ShowWindow( hConsole, SW_HIDE );
}

int main(int argc, char* argv[], char* envp[])
{
	hide_console();
	srand(time(NULL));
	PEB peb;
	STARTUPINFOA startinfo;
	memset(&startinfo, 0, sizeof(startinfo));
	startinfo.cb = sizeof(startinfo);
	PROCESS_INFORMATION processinfo;
	memset(&processinfo, 0, sizeof(processinfo));	
	if (!CreateProcess(/*"C:\\Windows\\System32\\calc.exe"*/argv[0], "", NULL, NULL, 0, CREATE_SUSPENDED, NULL, NULL, &startinfo, &processinfo))
	{
		//printf("[-] CreateProcess\n");
		MYERR;
		return 1;
	}
	//HANDLE hprocess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processinfo.dwProcessId);
	ctx.ContextFlags = CONTEXT_FULL;
	printf("hprocess=%p\n",processinfo.hProcess);
	if (!GetThreadContext(processinfo.hThread, &ctx))
	{
		//printf("[-] GetThreadContext\n");
		MYERR;
		return 1;
	}
	PVOID imagebase;
	printf("PEB = %p\n", ctx.Rdx);
	if (!ReadProcessMemory(processinfo.hProcess, (LPCVOID) ctx.Rdx, (LPVOID)&peb, sizeof(peb), NULL))
	{
		//printf("[-] ReadProcessMemory imagebase\n");
		MYERR;
		return 1;
	}
	imagebase = peb.Reserved3[1];
	printf("[+] main module = %p\n", imagebase);
	NtUnmapViewOfSection_fun = (NtUnmapViewOfSection) GetProcAddress(GetModuleHandle("ntdll.dll"), "NtUnmapViewOfSection");
	printf("[+] NtUnmapViewOfSection = %p\n", NtUnmapViewOfSection_fun);
	//NtUnmapViewOfSection_fun(hprocess, (PVOID) imagebase);
	//printf("RAX=%p\nRBX=%p\nRCX=%p\nRDX=%p\nRSP=%p\nRBP=%p\nRSI=%p\nRDI=%p\nRIP=%p\nr8=%p\nr9=%p\nr10=%p\nr11=%p\nr12=%p\nr13=%p\nr14=%p\nr15=%p\n",
	//        ctx.Rax,ctx.Rbx,ctx.Rcx,ctx.Rdx,ctx.Rsp,ctx.Rbp,ctx.Rsi,ctx.Rdi,ctx.Rip,ctx.R8,ctx.R9,ctx.R10,ctx.R11,ctx.R12,ctx.R13,ctx.R14,ctx.R15);
	// get main module address of the created process
    /*
	if (NtUnmapViewOfSection_fun(processinfo.hProcess, (PVOID) imagebase))
	{
		//printf("[-] NtUnmapViewOfSection imagebase\n");
		MYERR;
		return 1;
	}*/
	//printf("[+] unmapped\n");
	printf("Unmapview at %p\n", imagebase);
	LPSTR mem;//loadfile("C:\\Users\\Redouane\\Desktop\\Work\\infosec\\megacrackme\\crackme.exe");
	int size_stage = load_stage(&mem);
	for (int i = 0; i < size_stage; i++)
	{
		mem[i] = (mem[i] + 99) ^ 0x2f;
	}
	PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER) mem;
	PIMAGE_NT_HEADERS64 nt_header = (PIMAGE_NT_HEADERS64) ((__int64)mem + dos_header->e_lfanew);
	printf("[?] Number of sections : %d\n", nt_header->FileHeader.NumberOfSections);
	if (imagebase == nt_header->OptionalHeader.ImageBase)
		if (NtUnmapViewOfSection_fun(processinfo.hProcess, (PVOID)imagebase))
		  printf("[-] NtUnmapViewOfSection\n");
	printf("sizeof(image) = %p\n", nt_header->OptionalHeader.SizeOfImage);
	printf("? imagebase = %p\n", imagebase);
	LPVOID new_imagebase = VirtualAllocEx(
		processinfo.hProcess,
		(PVOID)nt_header->OptionalHeader.ImageBase,
		nt_header->OptionalHeader.SizeOfImage,
		MEM_COMMIT | MEM_RESERVE,
		PAGE_EXECUTE_READWRITE
	);
	if (new_imagebase == NULL)
	{
		printf("[-] VirtualAllocEx imagebase\n");
		MYERR;
		return 1;
	}
	printf("[?] new_imagebase = %p\n", new_imagebase);
	if (!WriteProcessMemory(processinfo.hProcess, new_imagebase, mem, nt_header->OptionalHeader.SizeOfHeaders, NULL))
	{
		printf("[-] WriteProcessMemory headers\n");
		MYERR;
		return 1;
	}
	for (int i = 0; i < nt_header->FileHeader.NumberOfSections; i++)
	{
		PIMAGE_SECTION_HEADER section_header = (PIMAGE_SECTION_HEADER) ((__int64)mem + dos_header->e_lfanew + sizeof(IMAGE_NT_HEADERS64) + (i * sizeof(IMAGE_SECTION_HEADER)));
		//printf("[?] section : %s\nVirtualAddress : 0x%x\nRaw size : %x\nPointer to raw data : %p\n", section_header->Name, section_header->VirtualAddress, section_header->SizeOfRawData, section_header->PointerToRawData);
		if (!WriteProcessMemory(processinfo.hProcess, new_imagebase+section_header->VirtualAddress, (LPVOID)((__int64)mem+section_header->PointerToRawData), section_header->SizeOfRawData, NULL))
		{
			printf("[-] WriteProcessMemory section\n");
			MYERR;
			return 1;
		}
	}
	if (!WriteProcessMemory(processinfo.hProcess, (LPVOID)ctx.Rdx+0x10, &new_imagebase, 8, NULL))
	{
		printf("[-] WriteProcessMemory newimagebase\n");
		MYERR;
		return 1;
	}
	
	ctx.Rcx = /*nt_header->OptionalHeader.ImageBase*/(__int64)new_imagebase + nt_header->OptionalHeader.AddressOfEntryPoint;

	if (!SetThreadContext(processinfo.hThread, &ctx))
	{
		printf("[-] SetThreadContext\n");
		MYERR;
		return 1;
	}
	
	if (ResumeThread(processinfo.hThread) == -1)
	{
		printf("[-] ResumeThread\n");
		MYERR;
		return -1;
	}

	// inject the dll
	char* dll;
	int dll_size = load_dll(&dll);
	
	for (int i = 0; i < dll_size; i++)
	{
		dll[i] = (dll[i] + 0x55) ^ 0xe3;
	}
	
	char dll_path[] = "C:\\Users\\Redouane\\Desktop\\Work\\infosec\\megacrackme\\MzEzMzcx.dll";
	
	
	LPVOID dllpath_addr = VirtualAllocEx(processinfo.hProcess, NULL, _MAX_PATH, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	WriteProcessMemory(processinfo.hProcess, dllpath_addr, dll_path, strlen(dll_path)+1, NULL);
	
	LPVOID loadlibrary_addr = (LPVOID) GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
	
	HANDLE dllloader_handle = CreateRemoteThread(processinfo.hProcess, NULL, 0, loadlibrary_addr, dllpath_addr, 0, NULL);
	
	if (!dllloader_handle)
	{
		printf("[-] CreateRemoteThread\n");
		MYERR;
		return 1;
	}
	
	/*
	if (WaitForSingleObject(dllloader_handle, 0) == -1)
	{
		printf("[-] WaitForSingleObject\n");
		MYERR;
		return -1;
	}
	*/
	printf("Exiting\n");
	ExitProcess(0);
}
