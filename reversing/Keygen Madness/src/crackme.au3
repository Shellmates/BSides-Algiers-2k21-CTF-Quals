#include <StringConstants.au3>
#include <Memory.au3>
#include <WinAPISys.au3>
#include <WinAPIProc.au3>
#include <String.au3>
Local $blacklist_processes = [ "ollydbg", "x32dbg", "x64dbg", "ida", "windbg", "cheatengine", "ImmunityDebugger", "radare2", "r2", "gdb", "hiew", "ghidra" ]
Func detect_forbidden_programs()
    Local $list = ProcessList();
	For $i = 0 To Ubound($list)-1
		Local $processname = $list[$i][0]
		for $j = 0 To Ubound($blacklist_processes)-1
			if StringInStr($processname, $blacklist_processes[$j], $STR_NOCASESENSEBASIC) Then
				MsgBox(0, "ERROR", "blacklisted tool detected! (" & $blacklist_processes[$j] & ")")
				Exit 1
			Endif
		Next
	Next
Endfunc

Local $shellcode_address = NULL
Local $kernel32 = _WinAPI_GetModuleHandle("kernel32.dll")
Local $GetModuleHandle_addr = _WinAPI_GetProcAddress($kernel32, "GetModuleHandleA")
Local $GetProcAddress_addr = _WinAPI_GetProcAddress($kernel32, "GetProcAddress")
Local $shellcode = BinaryToString("0xe800000000415d4983ed1d4889e54883e4f049c74510000000004989ceb82e646c6c5048b84d7a457a4d7a6378504889e14883ec2041ff55004883c4304989c44831c948ffc930c04c89f7f2ae4d8d7e114883f9d00f853c0100006a045941c647ff006a055f30c0b32d41321c3f08d84883c706e2f284c00f85190100004c89e148b84b726b4265435400504889e24883ec2841ff55084883c4304885c00f84000100004883ec104889e14c89f24d31c049ffc049c1e0044883ec20ffd04883c4204885c00f84d90000004889e6488b3e4831c980f9280f8da400000041803f000f84a300000041803f2d498d47014c0f44f84889f848d3e84883e01f41b81600000041b9410000004883f81a4d0f4cc14c01c0515048b86d4c66725a394d00504c89e14889e24883ec2841ff55084883c430594883ec28ffd04883c4285048b84b6c363246414a00504c89e14889e24883ec2841ff55084883c4284831c9418a0f4883ec28ffd04883c4305938c80f85220000005980c10549ffc7e953ffffff4883c605e944ffffff49c7451001000000e91500000049c7451002000000e90800000049c74510030000004889ecc3")
;MsgBox(0, "info", "GetModuleHandle = " & $GetModuleHandle_addr & @CRLF & "GetProcAddress = " & $GetProcAddress_addr)

Func p32($x)
	if IsPtr($x) Then
		$x = Number($x, 2)
	Endif

	Local $inp_array[4]
	For $i = 0 to 3
		$inp_array[$i] = BitAND($x, 0xff)
		$x = Int($x / 256, 2)
	Next
	if $x <> 0 Then
		return -1
	Else
		return StringFromASCIIArray($inp_array)
	Endif
Endfunc

Func p64($x)
	if IsPtr($x) Then
		$x = Number($x, 2)
	Endif
	Local $inp_array[8]
	For $i = 0 to 7
		$inp_array[$i] = BitAND($x, 0xff)
		$x = Int($x / 256, 2)
	Next
	if $x <> 0 Then
		return -1
	Else
		return StringFromASCIIArray($inp_array)
	Endif
Endfunc

Func hexdump($s)
	Local $addr = 0
	Local $buff = ""
	for $i = 1 To StringLen($s)
		Local $c = StringMid($s, $i, 1)
		$buff = $buff & " " & Hex(Asc($c), 2)
		if Mod($i, 16) = 0 Then
			$buff = $buff & @CRLF
		Endif
	Next
	return $buff
Endfunc

Func inject_shellcode()
	if $shellcode_address Then
		return False
	Else
		Local $heap = DllCall("kernel32", "handle", "GetProcessHeap"); GetProcessHeap()
		;MsgBox(0, "heap", "Heap = " & $heap[0])
		;MsgBox(0, "code?", "Code is : " & @CRLF & hexdump($shellcode))
		Local $oldprot = DllStructCreate("DWORD_PTR")
		$shellcode_address = _MemVirtualAlloc(0, StringLen($shellcode)+8*3, BitOR($MEM_COMMIT, $MEM_RESERVE) , $PAGE_EXECUTE_READWRITE)
		;MsgBox(0, "VirtualAlloc", "returned addr = " & $shellcode_address)
		if $shellcode_address Then
			;MsgBox(0, "Win", "Buffer at " & $shellcode_address & " is now ERW")
			Local $dest_buffer = DllStructCreate("PTR getmodulehandle;PTR getprocaddress;ULONG_PTR res; char shellcode[" & StringLen($shellcode) & "]", $shellcode_address)
			DllStructSetData($dest_buffer, "getmodulehandle", $GetModuleHandle_addr)
			DllStructSetData($dest_buffer, "getprocaddress", $GetProcAddress_addr)
			DllStructSetData($dest_buffer, "res", 0)
			DllStructSetData($dest_buffer, "shellcode", $shellcode)
			if @AutoItX64 Then
			   $shellcode_address += 8*3
			Else
			   $shellcode_address += 4*3
			Endif
			;MsgBox(0, "Win", "Injected shellcode at " & $shellcode_address)
			;if DllCall("kernel32", "BOOL", "VirtualProtect", "PTR", $shellcode_address, "ULONG_PTR", StringLen($code), "DWORD", 0x20, "DWORD_PTR", DllStructGetPtr($oldprot))[0] == 1 Then
			;	MsgBox(0, "Win", "Set protections to ER- at " & $shellcode_address)
			;Else
			;	MsgBox(0, "Error", "Error")
			;Endif
		Endif
		return True
	Endif
Endfunc

;inject_shellcode()
;detect_forbidden_programs()

#include <GUIConstantsEx.au3>
Opt("GUIOnEventMode", 1)

Func close()
	Exit 0
Endfunc

Func checkbutton_click()
	Local $username_value = GUICtrlRead($username_input)
	Local $serial_value = GUICtrlRead($serial_input)

	if StringLen($username_value) = 0 Then
		GUICtrlSetData($result_label, "Length of username cannot be 0")
		GUICtrlSetColor($result_label, 0xff0000)
		return
	ElseIf StringLen($serial_value) = 0 Then
		GUICtrlSetData($result_label, "Length of serial cannot be 0")
		GUICtrlSetColor($result_label, 0xff0000)
		return
	Endif

	; compute serial

	Local $username_arr = StringToASCIIArray($username_value)
	Local $username_len = StringLen($username_value)

	Local $correct_serial[29]
	for $i = 0 to 4
		for $j = 0 to 4
			Local $correct_char = Mod(BitXOR($username_arr[Mod($i*6+$j, $username_len)]-10-$i-$j, BitXOR(0x54, $i*$j)), 36)
			if $correct_char < 26 Then
				$correct_char = $correct_char + 65
			Else
				$correct_char = $correct_char - 26 + 48
			Endif
			$correct_serial[$i*6+$j] = $correct_char
		Next
		if $i = 4 Then
			ExitLoop
		Endif
		$correct_serial[6*$i+5] = 45
	Next

	$correct_serial = StringFromASCIIArray($correct_serial)
	if StringCompare($correct_serial, $serial_value) = 0 Then
		MsgBox(0, "Correct serial", "Or is it?")
	Else
		MsgBox(0, "Wrong serial", "The serial you entered is incorrect :(")
	Endif
	; MsgBox(0, "info", "serial = " & $correct_serial)
Endfunc

#comments-start

Real serial computation:
1) In AutoIT : Run transposition on the username
2) In the DLL : Calculate md5(username)=h
3) In the injected code : In slices of 5 bits, combine index and element of username to get all charset characters
4) compare on the fly

#comments-end

Func success()
   ; Todo: make this a whole new GUI creation, and hide the original GUI
   GUICtrlSetData($result_label, "Correct serial!")
   GUICtrlSetColor($result_label, 0x014709)
Endfunc

Func wrong()
   GUICtrlSetData($result_label, "Wrong serial!")
   GUICtrlSetColor($result_label, 0xff0000)
Endfunc

Func err()
   GUICtrlSetData($result_label, "An error has occured!")
   GUICtrlSetColor($result_label, 0xff)
EndFunc

Func unexpected()
   GUICtrlSetData($result_label, "Something unexpected happened!")
   GUICtrlSetColor($result_label, 0xff00ff)
EndFunc

#include <Array.au3>
Func transpose($s)
   Local $replacements[16] = [3, 8, 4, 10, 0, 13, 6, 11, 15, 9, 1, 7, 14, 12, 2, 5]
   Local $codepoints[16]
   Local $seed = 0
   for $i = 1 To StringLen($s)
	  $codepoints[$i-1] = StringMid($s, $i, 1)
	  $seed = BitXOR($seed, BitShift(Asc($codepoints[$i-1]), -8*Mod($i-1, 4)))
   Next
   SRandom($seed)
   for $i = StringLen($s)+1 To 16
	  Local $c = Random(0, 35, 1)
	  ;MsgBox(0, "num", "n = " & $c)
	  if $c < 26 Then
		 $c = $c + 97
	  Else
		 $c = $c - 26 + 48
	  EndIf
	  $codepoints[$i-1] = Chr($c)
   Next

   Local $new_codepoints[16]
   for $i = 0 To 15
	  $new_codepoints[$i] = $codepoints[$replacements[$i]]
   Next
   return _ArrayToString($new_codepoints, '')
Endfunc


Func real_check()
   Local $val = transpose(GUICtrlRead($username_input)) & "&" & GUICtrlRead($serial_input)
   Local $data_passed = DllStructCreate("char data[" & (StringLen($val)+1) & "]")
   DllStructSetData($data_passed, "data", $val)
   if $shellcode_address Then
	  Local $thandle = DllCall("kernel32.dll", "handle", "CreateThread", "PTR", NULL, "ULONG_PTR", 0, "PTR", $shellcode_address, "PTR", DllStructGetPtr($data_passed), "DWORD", 0, "DWORD_PTR", NULL)
	  _WinAPI_WaitForSingleObject($thandle[0])
	  ; read from memory, and check success or failure
	  Local $res_struct = DllStructCreate("ULONG_PTR res", $shellcode_address-8)
	  Local $res = DllStructGetData($res_struct, "res")
	  if $res = 1 Then
		 success()
	  ElseIf $res = 2 Then
		 wrong()
	  ElseIf $res = 3 Then
		 err()
	  Else
		 MsgBox(0, "!", "res = " & $res)
		 unexpected()
	  Endif
   Endif
Endfunc
inject_shellcode()
;MsgBox(0, "test", "ptr = " & $shellcode_address)
GUICreate("KeygenMe (by red0xff)", 500, 300)
Local $username_lbl = GUICtrlCreateLabel("Username", 10, 40, 100, 60)
GUICtrlSetFont($username_lbl, 12, 700, 0, "Tunga")

Local $serial_lbl = GUICtrlCreateLabel("Serial", 10, 100, 100, 60)
GUICtrlSetFont($serial_lbl, 12, 700, 0, "Tunga")

Local $username_input = GUICtrlCreateInput("", 150, 40, 210, 30)
GUICtrlSetLimit($username_input, 16)
GUICtrlSetFont($username_input, 12, 700, 0, "Tunga")
Local $serial_input = GUICtrlCreateInput("", 100, 100, 300, 30)
Local $result_label = GUICtrlCreateLabel("", 200, 150, 200, 50)
GuiCTRLSetFont($result_label, 12, 700, 0, "Tunga")
GUICtrlSetLimit ($serial_input, 29) ; aaaaa-bbbbb-ccccc-ddddd-eeeee
GUICtrlSetFont($serial_input, 12, 700, 2, "Arial")
$check_button = GUICtrlCreateButton("check", 100, 200, 300, 50)
GUICtrlSetOnEvent($check_button, "real_check")
GUISetOnEvent($GUI_EVENT_CLOSE, "close")
GUISetState(@SW_SHOW)

while True
	Sleep(1000)
    detect_forbidden_programs()
Wend
