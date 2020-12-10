
all:
	.\compile_autoit.bat
	gcc dll.c -odll.dll -shared -lbcrypt -s
	windres main.rc -O coff -o main.res
	gcc main.c main.res -okeygen_madness.exe -lbcrypt -mwindows -s
	ruby encode_resource.rb crackme.exe 99 0x2f crackme.exe.bin
	ruby encode_resource.rb dll.dll 0x55 0xe3 dll.dll.bin
	ResourceHacker.exe -open keygen_madness.exe -resource crackme.exe.bin -action add -mask RCDATA,Kerne132, -save new.exe
	ResourceHacker.exe -open new.exe -resource dll.dll.bin -action add -mask RCDATA,Kernel32, -save keygen_madness.exe
	rm new.exe crackme.exe.bin crackme.exe dll.dll.bin dll.dll main.res
