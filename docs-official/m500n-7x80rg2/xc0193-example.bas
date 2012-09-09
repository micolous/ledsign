                                                                     
                                                                     
                                                                     
                                             
'
' QBASIC example for XC0193 7x50 LED display by COM port
'
' written by: Peter King, www.procontechnology.com.au
'
' To download a copy of QBASIC from Microsoft - GO TO:
' http://download.microsoft.com/download/win95upg/tool_s/1.0/w95/en-us/olddos.exe
' olddos.exe (837KB) - to extract the files execute 'olddos.exe', the only files you need are QBASIC.EXE and QBASIC.HLP 
'
CONST CPORT$ = "COM1" 'COM port used

' open COM port @ 2400 baud, No parity, 8 data bits, 1 stop bit.

OPEN CPORT$ + ":2400,N,8,1,BIN,CS0,DS0,RS" FOR OUTPUT AS #1

' start transmission - must send for all transmissions

PRINT #1, CHR$(0) + CHR$(&HFF) + CHR$(&HFF) + CHR$(0); 'last chr=1 reset unit/clear all messages!

PRINT #1, CHR$(11); CHR$(0); CHR$(1);       'data for signs 0 or 1 OK!
PRINT #1, CHR$(&HFF);                       'end code

' optional commands here (one or more)

PRINT #1, CHR$(1); "01";                    'file 1
PRINT #1, CHR$(1);                          'run mode = cyclic
PRINT #1, CHR$(&HEF); CHR$(&HA2);           'font = standard
PRINT #1, CHR$(&HEF); CHR$(&HB0);           'colour = bright red
PRINT #1, CHR$(&HEF); CHR$(&HC0);           'speed = normal
PRINT #1, "time";
PRINT #1, CHR$(&HFF);                       'end frame
PRINT #1, CHR$(&HFF);                       'end code

PRINT #1, CHR$(1); "02";                    'file 2
PRINT #1, CHR$(2);                          'run mode = immediate
PRINT #1, CHR$(&HEF); CHR$(&H80);           'insert time
PRINT #1, CHR$(&HFF);                       'end frame
PRINT #1, CHR$(&HFF);                       'end code

PRINT #1, CHR$(1); "03";                    'file 3
PRINT #1, CHR$(1);                          'run mode = cyclic
PRINT #1, " The date is";
PRINT #1, CHR$(&HFF);                       'end frame
PRINT #1, CHR$(1);                          'run mode = cyclic
PRINT #1, CHR$(&HEF); CHR$(&H81);           'insert date
PRINT #1, CHR$(&HFF);                       'end frame
PRINT #1, CHR$(&HFF);                       'end code

PRINT #1, CHR$(1); "04";                    'file 4
PRINT #1, CHR$(1);                          'run mode = cyclic
PRINT #1, " "; CHR$(&HEF); CHR$(&H76);      'insert symbol ->
PRINT #1, "To infinity and beyond with www.procontechnology.com.au";
PRINT #1, CHR$(&HEF); CHR$(&H77);           'insert symbol <-
PRINT #1, CHR$(&HEF); CHR$(&HDB);           'insert TEL:
PRINT #1, CHR$(&HEF); CHR$(&HA0);           'font = 5x9
PRINT #1, CHR$(&HEF); CHR$(&HB0);           'colour = bright red
PRINT #1, CHR$(&HEF); CHR$(&HC1);           'speed = slower
PRINT #1, "1300304125 ";
PRINT #1, CHR$(&HFF);                       'end frame
PRINT #1, CHR$(&HFF);                       'end code

PRINT #1, CHR$(2); CHR$(0);                 'special file - S0..S9
PRINT #1, CHR$(&H7F); "0000"; "0000";       'always on
PRINT #1, "01"; "02"; "03"; "04";           'file 1..99
PRINT #1, CHR$(&HFF);                       'end code

'set date/time Sat = 6, 24hr = 0, 2008/July/25/18:59:50
'PRINT #1, CHR$(8); CHR$(6); CHR$(0); "080725185950"; CHR$(&HFF);

d$ = DATE$ 'DD-MM-YYYY
t$ = TIME$ 'HH:MM:SS

PRINT #1, CHR$(8); CHR$(0); CHR$(0);
PRINT #1, MID$(d$, 9, 2); MID$(d$, 4, 2); MID$(d$, 1, 2); 'date YYMMDD
PRINT #1, MID$(t$, 1, 2); MID$(t$, 4, 2); MID$(t$, 7, 2); 'time HHMMSS
PRINT #1, CHR$(&HFF);                       'end code

'Other functions available...

'PRINT #1, CHR$(4); CHR$(255); CHR$(1); CHR$(&HFF);  'alarm 255 times, 1 minute intervals
'PRINT #1, CHR$(5); CHR$(0); CHR$(&HFF);             'alarm off <>0 for on!
'PRINT #1, CHR$(6); "083000"; CHR$(&HFF);            'sign ON at 08:30:00
'PRINT #1, CHR$(7); "183000"; CHR$(&HFF);            'sign OFF at 18:30:00
'PRINT #1, CHR$(9); '... Custom graphic - see manual
'PRINT #1, CHR$(10); CHR$(1); CHR$(&HFF);            'test mode

'end transmission - must send for all transmissions

PRINT #1, CHR$(0);

