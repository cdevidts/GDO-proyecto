\* ModeloD_Sol5_multa_y_cero_pend *\
Minimize
OBJ: 750 B_0 + 750 B_1 + 750 B_10 + 750 B_11 + 750 B_2 + 750 B_3 + 750 B_4
 + 750 B_5 + 750 B_6 + 750 B_7 + 750 B_8 + 750 B_9 + 3000000 F_0 + 3000000 F_1
 + 3000000 F_10 + 3000000 F_11 + 3000000 F_2 + 3000000 F_3 + 3000000 F_4
 + 3000000 F_5 + 3000000 F_6 + 3000000 F_7 + 3000000 F_8 + 3000000 F_9
 + 2500000 H_0 + 2500000 H_1 + 2500000 H_10 + 2500000 H_11 + 2500000 H_2
 + 2500000 H_3 + 2500000 H_4 + 2500000 H_5 + 2500000 H_6 + 2500000 H_7
 + 2500000 H_8 + 2500000 H_9 + 1000 I_0 + 1000 I_1 + 1000 I_10 + 1000 I_11
 + 1000 I_2 + 1000 I_3 + 1000 I_4 + 1000 I_5 + 1000 I_6 + 1000 I_7 + 1000 I_8
 + 1000 I_9 + 2500 O_0 + 2500 O_1 + 2500 O_10 + 2500 O_11 + 2500 O_2
 + 2500 O_3 + 2500 O_4 + 2500 O_5 + 2500 O_6 + 2500 O_7 + 2500 O_8 + 2500 O_9
 + 1200000 W_0 + 1200000 W_1 + 1200000 W_10 + 1200000 W_11 + 1200000 W_2
 + 1200000 W_3 + 1200000 W_4 + 1200000 W_5 + 1200000 W_6 + 1200000 W_7
 + 1200000 W_8 + 1200000 W_9 + 3000000 y_0 + 3000000 y_1 + 3000000 y_10
 + 3000000 y_11 + 3000000 y_2 + 3000000 y_3 + 3000000 y_4 + 3000000 y_5
 + 3000000 y_6 + 3000000 y_7 + 3000000 y_8 + 3000000 y_9
Subject To
balance_0: B_0 - I_0 + O_0 + R_0 = 8500
balance_1: - B_0 + B_1 + I_0 - I_1 + O_1 + R_1 = 9000
balance_10: B_10 - B_9 - I_10 + I_9 + O_10 + R_10 = 11500
balance_11: - B_10 + B_11 + I_10 - I_11 + O_11 + R_11 = 10500
balance_2: - B_1 + B_2 + I_1 - I_2 + O_2 + R_2 = 8500
balance_3: - B_2 + B_3 + I_2 - I_3 + O_3 + R_3 = 8500
balance_4: - B_3 + B_4 + I_3 - I_4 + O_4 + R_4 = 9000
balance_5: - B_4 + B_5 + I_4 - I_5 + O_5 + R_5 = 9500
balance_6: - B_5 + B_6 + I_5 - I_6 + O_6 + R_6 = 10000
balance_7: - B_6 + B_7 + I_6 - I_7 + O_7 + R_7 = 10000
balance_8: - B_7 + B_8 + I_7 - I_8 + O_8 + R_8 = 11500
balance_9: - B_8 + B_9 + I_8 - I_9 + O_9 + R_9 = 12500
cap_HE_0: O_0 - 150 W_0 <= 0
cap_HE_1: O_1 - 150 W_1 <= 0
cap_HE_10: O_10 - 150 W_10 <= 0
cap_HE_11: O_11 - 150 W_11 <= 0
cap_HE_2: O_2 - 150 W_2 <= 0
cap_HE_3: O_3 - 150 W_3 <= 0
cap_HE_4: O_4 - 150 W_4 <= 0
cap_HE_5: O_5 - 150 W_5 <= 0
cap_HE_6: O_6 - 150 W_6 <= 0
cap_HE_7: O_7 - 150 W_7 <= 0
cap_HE_8: O_8 - 150 W_8 <= 0
cap_HE_9: O_9 - 150 W_9 <= 0
cap_regular_0: R_0 - 500 W_0 <= 0
cap_regular_1: R_1 - 500 W_1 <= 0
cap_regular_10: R_10 - 500 W_10 <= 0
cap_regular_11: R_11 - 500 W_11 <= 0
cap_regular_2: R_2 - 500 W_2 <= 0
cap_regular_3: R_3 - 500 W_3 <= 0
cap_regular_4: R_4 - 500 W_4 <= 0
cap_regular_5: R_5 - 500 W_5 <= 0
cap_regular_6: R_6 - 500 W_6 <= 0
cap_regular_7: R_7 - 500 W_7 <= 0
cap_regular_8: R_8 - 500 W_8 <= 0
cap_regular_9: R_9 - 500 W_9 <= 0
cero_pendientes_0: B_0 = 0
cero_pendientes_1: B_1 = 0
cero_pendientes_10: B_10 = 0
cero_pendientes_11: B_11 = 0
cero_pendientes_2: B_2 = 0
cero_pendientes_3: B_3 = 0
cero_pendientes_4: B_4 = 0
cero_pendientes_5: B_5 = 0
cero_pendientes_6: B_6 = 0
cero_pendientes_7: B_7 = 0
cero_pendientes_8: B_8 = 0
cero_pendientes_9: B_9 = 0
dotacion_0: F_0 - H_0 + W_0 = 20
dotacion_1: F_1 - H_1 - W_0 + W_1 = 0
dotacion_10: F_10 - H_10 + W_10 - W_9 = 0
dotacion_11: F_11 - H_11 - W_10 + W_11 = 0
dotacion_2: F_2 - H_2 - W_1 + W_2 = 0
dotacion_3: F_3 - H_3 - W_2 + W_3 = 0
dotacion_4: F_4 - H_4 - W_3 + W_4 = 0
dotacion_5: F_5 - H_5 - W_4 + W_5 = 0
dotacion_6: F_6 - H_6 - W_5 + W_6 = 0
dotacion_7: F_7 - H_7 - W_6 + W_7 = 0
dotacion_8: F_8 - H_8 - W_7 + W_8 = 0
dotacion_9: F_9 - H_9 - W_8 + W_9 = 0
inventario_final: I_11 >= 1000
multa_0: B_0 - 8405 y_0 <= 95
multa_1: B_1 - 17410 y_1 <= 90
multa_10: B_10 - 108385 y_10 <= 115
multa_11: B_11 - 118895 y_11 <= 105
multa_2: B_2 - 25915 y_2 <= 85
multa_3: B_3 - 34415 y_3 <= 85
multa_4: B_4 - 43410 y_4 <= 90
multa_5: B_5 - 52905 y_5 <= 95
multa_6: B_6 - 62900 y_6 <= 100
multa_7: B_7 - 72900 y_7 <= 100
multa_8: B_8 - 84385 y_8 <= 115
multa_9: B_9 - 96875 y_9 <= 125
pendientes_final: B_11 <= 0
Bounds
 0 <= F_0 <= 3
 0 <= F_1 <= 3
 0 <= F_10 <= 3
 0 <= F_11 <= 3
 0 <= F_2 <= 3
 0 <= F_3 <= 3
 0 <= F_4 <= 3
 0 <= F_5 <= 3
 0 <= F_6 <= 3
 0 <= F_7 <= 3
 0 <= F_8 <= 3
 0 <= F_9 <= 3
 0 <= H_0 <= 3
 0 <= H_1 <= 3
 0 <= H_10 <= 3
 0 <= H_11 <= 3
 0 <= H_2 <= 3
 0 <= H_3 <= 3
 0 <= H_4 <= 3
 0 <= H_5 <= 3
 0 <= H_6 <= 3
 0 <= H_7 <= 3
 0 <= H_8 <= 3
 0 <= H_9 <= 3
 I_0 <= 7500
 I_1 <= 7500
 I_10 <= 7500
 I_11 <= 7500
 I_2 <= 7500
 I_3 <= 7500
 I_4 <= 7500
 I_5 <= 7500
 I_6 <= 7500
 I_7 <= 7500
 I_8 <= 7500
 I_9 <= 7500
 15 <= W_0 <= 25
 15 <= W_1 <= 25
 15 <= W_10 <= 25
 15 <= W_11 <= 25
 15 <= W_2 <= 25
 15 <= W_3 <= 25
 15 <= W_4 <= 25
 15 <= W_5 <= 25
 15 <= W_6 <= 25
 15 <= W_7 <= 25
 15 <= W_8 <= 25
 15 <= W_9 <= 25
Generals
F_0
F_1
F_10
F_11
F_2
F_3
F_4
F_5
F_6
F_7
F_8
F_9
H_0
H_1
H_10
H_11
H_2
H_3
H_4
H_5
H_6
H_7
H_8
H_9
W_0
W_1
W_10
W_11
W_2
W_3
W_4
W_5
W_6
W_7
W_8
W_9
Binaries
y_0
y_1
y_10
y_11
y_2
y_3
y_4
y_5
y_6
y_7
y_8
y_9
End
