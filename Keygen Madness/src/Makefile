
all: 
	.\compile_autoit.bat
	gcc dll.c -oMzEzMzcx.dll -shared -lbcrypt
	gcc main.c -omain.exe -lbcrypt
	ruby encode_resource.rb crackme.exe 99 0x2f crackme.exe.bin
	ruby encode_resource.rb MzEzMzcx.dll 0x55 0xe3 MzEzMzcx.dll.bin
	ResourceHacker.exe -open main.exe -resource crackme.exe.bin -action add -mask RCDATA,CRACKME, -save new.exe
	ResourceHacker.exe -open new.exe -resource MzEzMzcx.dll.bin -action add -mask RCDATA,MzEzMzcx, -save main.exe
	rm new.exe
	ruby rename_resource.rb main.exe
	rm crackme.exe.bin MzEzMzcx.dll.bin
