M103 S

Macro:Home_all_Axis_in_sequence

M109			;wait to get to nozzle temp

M129			;Head LED on
M106			;Fan on

G36 E1000 F12000 ; Un-Park

G0 X200 Y25
Macro:Purge_T1
G0 X200 Y55
Macro:Purge_T1
G0 X200 Y85
Macro:Purge_T1
G0 X200 Y115
Macro:Purge_T1
G0 X200 Y145
Macro:Purge_T1

Macro:Finish-Abort_Print
