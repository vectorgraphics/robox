M103 S

Macro:Home_all_Axis_in_sequence

M109			;wait to get to nozzle temp

M129			;Head LED on
M106			;Fan on

G36 E1000 F12000 ; Un-Park

G0 X10 Y16
Macro:Purge_T0
G0 X10 Y20
Macro:Purge_T0
G0 X10 Y24
Macro:Purge_T0
G0 X10 Y28
Macro:Purge_T0
G0 X10 Y32
Macro:Purge_T0

Macro:Finish-Abort_Print
