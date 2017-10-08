M103 S

Macro:Home_all_Axis_in_sequence

T0
M109			;wait to get to nozzle temp

M129			;Head LED on
M106			;Fan on

G36 D1000 F12000 ; Un-Park

G0 X10 Y15
Macro:Purge_T0
G0 X10 Y45
Macro:Purge_T0
G0 X10 Y75
Macro:Purge_T0
G0 X10 Y105
Macro:Purge_T0
G0 X10 Y135
Macro:Purge_T0

Macro:Finish-Abort_Print
