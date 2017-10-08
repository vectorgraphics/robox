M103 S220 T220

Macro:Home_all_Axis_in_sequence

T0
M109			;wait to get to nozzle temp
T1
M109			;wait to get to nozzle temp

M129			;Head LED on
M106			;Fan on

G36 D1000 F12000 ; Un-Park
G36 E1000 F12000 ; Un-Park

G0 X10 Y15
Macro:Purge_T0
G0 X200 Y25
Macro:Purge_T1
G0 X10 Y45
Macro:Purge_T0
G0 X200 Y55
Macro:Purge_T1
G0 X10 Y75
Macro:Purge_T0
G0 X200 Y85
Macro:Purge_T1
G0 X10 Y105
Macro:Purge_T0
G0 X200 Y115
Macro:Purge_T1
G0 X10 Y135
Macro:Purge_T0
G0 X200 Y145
Macro:Purge_T1

Macro:Finish-Abort_Print
