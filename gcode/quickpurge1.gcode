M103 T

Macro:Home_all_Axis_in_sequence

T1
M109			;wait to get to nozzle temp

M129			;Head LED on
M106			;Fan on

G36 E1000 F12000 ; Un-Park

G0 X190 Y25
Macro:Purge_T1
G0 X190 Y55
Macro:Purge_T1
G0 X190 Y85
Macro:Purge_T1
G0 X190 Y115
Macro:Purge_T1
G0 X190 Y145
Macro:Purge_T1

Macro:Finish-Abort_Print
