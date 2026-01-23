
# Touren
R = ['t-4', 't-5', 't-6', 's-1', 's-2', 's-3', 's-4', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7', 'r1', 'r2', 'r3', 'h3', 'h4', 'k1']
# LKW-Typen Diesel
TD = ['ActrosL']
# LKW-Typen Elektro
TE = ['eActros600', 'eActros400']
# Ladesäulen
L = ['Alpitronic-50', 'Alpitronic-200', 'Alpitronic-400']

# Distanzen
dist = {
	't-4': 250, 't-5': 250, 't-6': 250,
	's-1': 120, 's-2': 120, 's-3': 120, 's-4': 120,
	'w1': 100, 'w2': 100, 'w3': 100, 'w4': 100, 'w5': 100, 'w6': 100, 'w7': 100,
	'r1': 285, 'r2': 250, 'r3': 235,
	'h3': 180, 'h4': 180, 'k1': 275
}

# Maut Distanzen
mDist = {
	't-4': 150, 't-5': 150, 't-6': 150,
	's-1': 32, 's-2': 32, 's-3': 32, 's-4': 32,
	'w1': 32, 'w2': 32, 'w3': 32, 'w4': 32, 'w5': 32, 'w6': 32, 'w7': 32,
	'r1': 259, 'r2': 220, 'r3': 219,
	'h3': 160, 'h4': 160, 'k1': 235
}

# Startzeiten (als Strings)
start = {
	't-4': '06:45', 't-5': '06:30', 't-6': '06:00',
	's-1': '05:30', 's-2': '06:00', 's-3': '09:00', 's-4': '06:30',
	'w1': '05:30', 'w2': '08:00', 'w3': '06:45', 'w4': '06:00', 'w5': '07:00', 'w6': '05:30', 'w7': '07:15',
	'r1': '18:00', 'r2': '16:30', 'r3': '17:45',
	'h3': '18:45', 'h4': '18:30', 'k1': '16:30'
}

# Endzeiten (als Strings)
end = {
	't-4': '17:00', 't-5': '17:15', 't-6': '16:30',
	's-1': '15:30', 's-2': '16:00', 's-3': '16:00', 's-4': '16:30',
	'w1': '15:30', 'w2': '18:00', 'w3': '16:45', 'w4': '16:00', 'w5': '17:00', 'w6': '15:30', 'w7': '17:15',
	'r1': '22:30', 'r2': '21:45', 'r3': '21:30',
	'h3': '22:45', 'h4': '22:30', 'k1': '22:30'
}

# Diesel-LKW Parameter
cap_d = {'ActrosL': 24000}  # Leasingkosten
opx_d = {'ActrosL': 6000}   # Wartungskosten
avgDv_d = {'ActrosL': 2.6}  # Durchschnitt Dieselverbrauch pro km
kfz_d = {'ActrosL': 556}    # KFZ-Steuer

# Elektro-LKW Parameter
cap_e = {'eActros600': 60000, 'eActros400': 50000}  # Leasingkosten
opx_e = {'eActros600': 6000, 'eActros400': 5000}    # Wartungskosten
avgEv_e = {'eActros600': 1.1, 'eActros400': 1.05}   # Durchschnitt Energieverbrauch pro km
thg_e = {'eActros600': 1000, 'eActros400': 1000}    # Treibhausgassteuer
max_p_e = {'eActros600': 400, 'eActros400': 400}    # Maximale Ladeleistung
soc_e = {'eActros600': 621, 'eActros400': 414}      # Batteriekapazität

# Ladesäulen Parameter
cap_l = {'Alpitronic-50': 3000, 'Alpitronic-200': 10000, 'Alpitronic-400': 16000}  # Leasingkosten
opx_l = {'Alpitronic-50': 1000, 'Alpitronic-200': 1500, 'Alpitronic-400': 2000}    # Wartungskosten
max_p_l = {'Alpitronic-50': 50, 'Alpitronic-200': 200, 'Alpitronic-400': 400}      # Maximale Ladeleistung
cs_l = {'Alpitronic-50': 2, 'Alpitronic-200': 2, 'Alpitronic-400': 2}              # Anzahl Chargingspots

# Weitere Parameter
Nmax = 3  # Maximale Anzahl Ladesäulen pro Standort
P_grid_max = 500  # Maximale Ladeleistung pro Standort (kW)
c_e = 0.25  # €/kWh Arbeitspreis Strom
c_m_d = 0.34  # €/km mautpflichtige Distanz (Kosten für Maut)

