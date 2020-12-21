all:
	as prog.asm -msyntax=intel -oassembly
	gcc lookups.c assembly -olookups -s
	rm assembly
