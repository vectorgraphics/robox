G90
T0

;G0 Z4
;G0 X20 Y75		;Level Gantry Position 1
;G28 Z			;Home Z
;G0 Z4 			;Move up 4mm
;G0 X190 Y75		;Level Gantry Position 2
;G28 Z			;Home Z
;G0 Z4 			;Move up 4mm
;G38 			;Level gantry

G0 Z2
T1 X107 Y75
G28 Z
G0 Z2

T0
G39
G28 Z
G39 S1.0
G0 Z0.09

; Adjust T0 until paper of thickness 0.09 has slight drag under T0.
; Subtract M113 result from T1
