;Level_Gantry
G90

G0 Z4
G0 X20 Y75		;Level Gantry Position 1
G28 Z			;Home Z
G0 Z4 			;Move up 4mm
G0 X190 Y75		;Level Gantry Position 2
G28 Z			;Home Z
G0 Z4 			;Move up 4mm
G38 			;Level gantry
