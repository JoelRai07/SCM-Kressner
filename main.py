# ============================================================================
# MILP-OPTIMIERUNGSMODELL FÜR LKW-FLOTTENPLANUNG MIT LADEINFRASTRUKTUR
# Pyomo ConcreteModel - Google Colab Ready
# MIT OPTIMIERUNG DER LKW-TYPEN
# ============================================================================
 
# Installation und Import
!pip install pyomo -q
 
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
 
# ============================================================================
# MODELL INITIALISIERUNG
# ============================================================================
 
model = pyo.ConcreteModel(name="LKW_Flottenplanung")
 
# ============================================================================
# 1️⃣ INDEXMENGEN (SETS)
# ============================================================================
 
# Touren
model.R = pyo.Set(initialize=[
    't-4', 't-5', 't-6', 's-1', 's-2', 's-3', 's-4',
    'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7',
    'r1', 'r2', 'r3', 'h3', 'h4', 'k1'
])
 
# LKWs - ERHÖHT AUF 15
model.K = pyo.Set(initialize=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
 
# Diesel-LKW-Typen
model.TD = pyo.Set(initialize=['ActrosL'])
 
# Elektro-LKW-Typen
model.TE = pyo.Set(initialize=['eActros600', 'eActros400'])
 
# Alle LKW-Typen
model.T = model.TD | model.TE
 
# Ladesäulentypen
model.L = pyo.Set(initialize=['Alpitronic-50', 'Alpitronic-200', 'Alpitronic-400'])
 
# Zeitintervalle
model.Z = pyo.Set(initialize=range(1, 97))  # 1...96
 
# Tagzeit (06:00-17:45)
model.Z_day = pyo.Set(initialize=range(25, 73))  # 25...72
 
# Nachtzeit
model.Z_night = pyo.Set(initialize=[z for z in range(1, 97) if z not in range(25, 73)])
 
# ============================================================================
# 2️⃣ PARAMETER
# ============================================================================
 
# --- Tourenparameter ---
 
# Distanz (km)
dist_data = {
    't-4': 250, 't-5': 250, 't-6': 250,
    's-1': 120, 's-2': 120, 's-3': 120, 's-4': 120,
    'w1': 100, 'w2': 100, 'w3': 100, 'w4': 100, 'w5': 100, 'w6': 100, 'w7': 100,
    'r1': 285, 'r2': 250, 'r3': 235, 'h3': 180, 'h4': 180, 'k1': 275
}
model.dist = pyo.Param(model.R, initialize=dist_data)
 
# Mautpflichtige Distanz (km)
mDist_data = {
    't-4': 150, 't-5': 150, 't-6': 150,
    's-1': 32, 's-2': 32, 's-3': 32, 's-4': 32,
    'w1': 32, 'w2': 32, 'w3': 32, 'w4': 32, 'w5': 32, 'w6': 32, 'w7': 32,
    'r1': 259, 'r2': 220, 'r3': 219, 'h3': 160, 'h4': 160, 'k1': 235
}
model.mDist = pyo.Param(model.R, initialize=mDist_data)
 
# Startintervall s_r(r)
s_r_data = {
    't-4': 28, 't-5': 27, 't-6': 25,
    's-1': 23, 's-2': 25, 's-3': 37, 's-4': 27,
    'w1': 23, 'w2': 33, 'w3': 28, 'w4': 25, 'w5': 29, 'w6': 23, 'w7': 30,
    'r1': 73, 'r2': 67, 'r3': 72, 'h3': 76, 'h4': 75, 'k1': 67
}
model.s_r = pyo.Param(model.R, initialize=s_r_data)
 
# Endintervall e_r(r)
e_r_data = {
    't-4': 69, 't-5': 70, 't-6': 67,
    's-1': 63, 's-2': 65, 's-3': 65, 's-4': 67,
    'w1': 63, 'w2': 73, 'w3': 69, 'w4': 65, 'w5': 69, 'w6': 63, 'w7': 70,
    'r1': 91, 'r2': 88, 'r3': 87, 'h3': 92, 'h4': 91, 'k1': 91
}
model.e_r = pyo.Param(model.R, initialize=e_r_data)
 
# Dauer der Tour in Intervallen
def dur_z_init(model, r):
    return model.e_r[r] - model.s_r[r]
model.dur_z = pyo.Param(model.R, initialize=dur_z_init)
 
# start_at[r,z]: 1 wenn Tour r in Intervall z startet
def start_at_init(model, r, z):
    return 1 if z == model.s_r[r] else 0
model.start_at = pyo.Param(model.R, model.Z, initialize=start_at_init)
 
# end_at[r,z]: 1 wenn Tour r in Intervall z endet
def end_at_init(model, r, z):
    return 1 if z == model.e_r[r] else 0
model.end_at = pyo.Param(model.R, model.Z, initialize=end_at_init)
 
# active_tour[r,z]: 1 wenn Tour r in Intervall z aktiv ist
def active_tour_init(model, r, z):
    return 1 if model.s_r[r] <= z < model.e_r[r] else 0
model.active_tour = pyo.Param(model.R, model.Z, initialize=active_tour_init)
 
# --- Diesel-LKW-Parameter ---
 
model.cap_d = pyo.Param(model.TD, initialize={'ActrosL': 24000})
model.opx_d = pyo.Param(model.TD, initialize={'ActrosL': 6000})
model.kfz_d = pyo.Param(model.TD, initialize={'ActrosL': 556})
model.avgDv_d = pyo.Param(model.TD, initialize={'ActrosL': 0.26})
model.c_diesel = pyo.Param(initialize=1.68)
model.c_m_d = pyo.Param(initialize=0.34)
 
# --- Elektro-LKW-Parameter ---
 
model.cap_e = pyo.Param(model.TE, initialize={'eActros600': 60000, 'eActros400': 50000})
model.opx_e = pyo.Param(model.TE, initialize={'eActros600': 6000, 'eActros400': 5000})
model.avgEv_e = pyo.Param(model.TE, initialize={'eActros600': 1.1, 'eActros400': 1.05})
model.soc_e = pyo.Param(model.TE, initialize={'eActros600': 621, 'eActros400': 414})
model.thg_e = pyo.Param(model.TE, initialize={'eActros600': 1000, 'eActros400': 1000})
 
# Maximale Ladeleistung (inkl. Diesel = 0)
max_p_e_data = {'eActros600': 400, 'eActros400': 400, 'ActrosL': 0}
model.max_p_e = pyo.Param(model.TD | model.TE, initialize=max_p_e_data)
 
# --- Ladesäulen-Parameter ---
 
model.cap_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 3000, 'Alpitronic-200': 10000, 'Alpitronic-400': 16000
})
model.opx_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 1000, 'Alpitronic-200': 1500, 'Alpitronic-400': 2000
})
model.max_p_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 50, 'Alpitronic-200': 200, 'Alpitronic-400': 400
})
model.cs_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 2, 'Alpitronic-200': 2, 'Alpitronic-400': 2
})
 
# --- Netz- und Speicherparameter ---
 
model.p_grid_max = pyo.Param(initialize=500)
model.capP_s = pyo.Param(initialize=30)
model.capQ_s = pyo.Param(initialize=350)
model.opx_s = pyo.Param(initialize=0.02)
model.nrt = pyo.Param(initialize=0.98)
model.dod = pyo.Param(initialize=0.025)
model.c_e = pyo.Param(initialize=0.25)
model.c_gr = pyo.Param(initialize=1000)
model.cPeak = pyo.Param(initialize=150)
model.Nmax = pyo.Param(initialize=3)
model.delta_t = pyo.Param(initialize=0.25)
model.M = pyo.Param(initialize=10000)
model.z6 = pyo.Param(initialize=25)
 
# --- Abgeleiteter Parameter: unplug_ok ---
 
def unplug_ok_init(model, z):
    if z in model.Z_day:
        return 1
    elif z + 1 == model.z6:
        return 1
    else:
        return 0
model.unplug_ok = pyo.Param(model.Z, initialize=unplug_ok_init, within=pyo.Binary)
 
# ============================================================================
# 3️⃣ ENTSCHEIDUNGSVARIABLEN (ERWEITERT)
# ============================================================================
 
# --- LKW-Typ-Zuordnung (NEU: Jetzt eine Variable!) ---
 
# type_assignment[k,t] = 1 wenn LKW k vom Typ t ist
model.type_assignment = pyo.Var(model.K, model.T, domain=pyo.Binary)
 
# --- Zuordnung & Bewegung ---
 
model.a = pyo.Var(model.R, model.K, domain=pyo.Binary)
model.depart = pyo.Var(model.K, model.Z, domain=pyo.Binary)
model.arrive = pyo.Var(model.K, model.Z, domain=pyo.Binary)
model.has_future = pyo.Var(model.K, model.Z_night, domain=pyo.Binary)
model.next = pyo.Var(model.R, model.K, model.Z_night, domain=pyo.Binary)
 
# --- Laden ---
 
model.assign = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.plug = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.real_p = pyo.Var(model.K, model.L, model.Z, domain=pyo.NonNegativeReals)
model.y_l = pyo.Var(model.L, domain=pyo.NonNegativeIntegers, bounds=(0, model.Nmax))
 
# --- Energiezustände ---
 
# soc für ALLE LKWs (wird 0 sein für Diesel)
model.soc = pyo.Var(model.K, model.Z, domain=pyo.NonNegativeReals)
 
model.need_charge = pyo.Var(model.K, model.Z_night, domain=pyo.Binary)
model.enough = pyo.Var(model.K, model.Z_night, domain=pyo.Binary)
 
# --- Speicherbetrieb ---
 
model.p_s = pyo.Var(domain=pyo.NonNegativeReals)
model.q_s = pyo.Var(domain=pyo.NonNegativeReals)
model.p_l_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)
model.p_e_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)
model.soc_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)
model.mode_s = pyo.Var(model.Z, domain=pyo.Binary)
 
# --- Netz ---
 
model.p_grid = pyo.Var(model.Z, domain=pyo.NonNegativeReals)
model.p_peak = pyo.Var(domain=pyo.NonNegativeReals)
model.u = pyo.Var(domain=pyo.Binary)
 
# ============================================================================
# 4️⃣ BERECHNETE VARIABLEN / EXPRESSIONS (ANGEPASST)
# ============================================================================
 
# --- Energieverbrauch cons[k,z] ---
 
def cons_init(model, k, z):
    # Verbrauch = Summe über alle Elektro-Typen
    return sum(
        model.type_assignment[k, t] * sum(
            model.active_tour[r, z] * model.a[r, k] *
            (model.dist[r] * model.avgEv_e[t] / model.dur_z[r])
            for r in model.R
        )
        for t in model.TE
    )
 
model.cons = pyo.Expression(model.K, model.Z, rule=cons_init)
 
# --- Energiebedarf e_next[k,z] ---
 
def e_next_init(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    return sum(
        model.type_assignment[k, t] * sum(
            model.next[r, k, z] * model.dist[r] * model.avgEv_e[t]
            for r in rAfter_z
        )
        for t in model.TE
    )
 
model.e_next = pyo.Expression(model.K, model.Z_night, rule=e_next_init)
 
# ============================================================================
# 5️⃣ NEBENBEDINGUNGEN (CONSTRAINTS)
# ============================================================================
 
# --- 5.0 LKW-TYP-ZUORDNUNG (NEU!) ---
 
# (NB0a) Jeder LKW muss genau einen Typ haben
def one_type_per_truck_rule(model, k):
    return sum(model.type_assignment[k, t] for t in model.T) == 1
model.con_one_type_per_truck = pyo.Constraint(model.K, rule=one_type_per_truck_rule)
 
# --- 5.1 TOUR-ZUORDNUNG ---
 
# (NB1) Jede Tour genau einem LKW
def tour_assignment_rule(model, r):
    return sum(model.a[r, k] for k in model.K) == 1
model.con_tour_assignment = pyo.Constraint(model.R, rule=tour_assignment_rule)
 
# --- 5.2 LKW-BEWEGUNGSLOGIK ---
 
# (NB4) LKW kann nicht zwei Touren gleichzeitig fahren
def no_concurrent_tours_rule(model, k, z):
    return sum(model.active_tour[r, z] * model.a[r, k] for r in model.R) <= 1
model.con_no_concurrent_tours = pyo.Constraint(model.K, model.Z, rule=no_concurrent_tours_rule)
 
# (NB5) Kein gleichzeitiges Ankommen zweier Touren
def no_concurrent_arrivals_rule(model, k, z):
    return sum(model.end_at[r, z] * model.a[r, k] for r in model.R) <= 1
model.con_no_concurrent_arrivals = pyo.Constraint(model.K, model.Z, rule=no_concurrent_arrivals_rule)
 
# (NB6) Definition depart
def depart_definition_rule(model, k, z):
    return model.depart[k, z] == sum(model.start_at[r, z] * model.a[r, k] for r in model.R)
model.con_depart_definition = pyo.Constraint(model.K, model.Z, rule=depart_definition_rule)
 
# (NB7) Definition arrive
def arrive_definition_rule(model, k, z):
    return model.arrive[k, z] == sum(model.end_at[r, z] * model.a[r, k] for r in model.R)
model.con_arrive_definition = pyo.Constraint(model.K, model.Z, rule=arrive_definition_rule)
 
# --- 5.3 ZUKUNFTSTOUREN-LOGIK ---
 
# (NB8) has_future nur wenn Touren nach z existieren
def has_future_upper_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return model.has_future[k, z] == 0
    return model.has_future[k, z] <= sum(model.a[r, k] for r in rAfter_z)
model.con_has_future_upper = pyo.Constraint(model.K, model.Z_night, rule=has_future_upper_rule)
 
# (NB9) has_future muss gesetzt sein, wenn Touren existieren
def has_future_lower_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return pyo.Constraint.Skip
    return sum(model.a[r, k] for r in rAfter_z) >= model.has_future[k, z]
model.con_has_future_lower = pyo.Constraint(model.K, model.Z_night, rule=has_future_lower_rule)
 
# (NB10) Obere Schranke für Tourenanzahl
def has_future_bound_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return pyo.Constraint.Skip
    return sum(model.a[r, k] for r in rAfter_z) <= len(rAfter_z) * model.has_future[k, z]
model.con_has_future_bound = pyo.Constraint(model.K, model.Z_night, rule=has_future_bound_rule)
 
# (NB11) Genau eine nächste Tour bei Ankunft mit Zukunftstouren
def next_tour_selection_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return pyo.Constraint.Skip
    return sum(model.next[r, k, z] for r in rAfter_z) <= model.arrive[k, z]
model.con_next_tour_selection = pyo.Constraint(model.K, model.Z_night, rule=next_tour_selection_rule)
 
# (NB11b) next erfordert has_future
def next_requires_future_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return pyo.Constraint.Skip
    return sum(model.next[r, k, z] for r in rAfter_z) <= model.has_future[k, z]
model.con_next_requires_future = pyo.Constraint(model.K, model.Z_night, rule=next_requires_future_rule)
 
# (NB11c) wenn arrive=1 und has_future=1, dann muss genau eine next=1
def next_when_both_rule(model, k, z):
    rAfter_z = [r for r in model.R if model.s_r[r] > z]
    if len(rAfter_z) == 0:
        return pyo.Constraint.Skip
    return sum(model.next[r, k, z] for r in rAfter_z) >= model.arrive[k, z] + model.has_future[k, z] - 1
model.con_next_when_both = pyo.Constraint(model.K, model.Z_night, rule=next_when_both_rule)
 
# (NB12) next nur wenn Tour zugeordnet
def next_requires_assignment_rule(model, r, k, z):
    return model.next[r, k, z] <= model.a[r, k]
model.con_next_requires_assignment = pyo.Constraint(model.R, model.K, model.Z_night, rule=next_requires_assignment_rule)
 
# (NB13) next=0 für Touren, die nicht nach z starten
def next_only_after_rule(model, r, k, z):
    if model.s_r[r] <= z:
        return model.next[r, k, z] == 0
    return pyo.Constraint.Skip
model.con_next_only_after = pyo.Constraint(model.R, model.K, model.Z_night, rule=next_only_after_rule)
 
# (NB14) next ist wirklich die zeitlich nächste Tour
def next_is_nearest_rule(model, r, k, z):
    if model.s_r[r] <= z:
        return pyo.Constraint.Skip
    intermediate_tours = [rp for rp in model.R if z < model.s_r[rp] < model.s_r[r]]
    if len(intermediate_tours) == 0:
        return pyo.Constraint.Skip
    return model.next[r, k, z] <= 1 - sum(model.next[rp, k, z] for rp in intermediate_tours)
model.con_next_is_nearest = pyo.Constraint(model.R, model.K, model.Z_night, rule=next_is_nearest_rule)
 
# --- 5.4 ENERGIE-DYNAMIK (ANGEPASST FÜR VARIABLE TYPEN) ---
 
# (NB15) SOC-Dynamik
def soc_dynamics_rule(model, k, z):
    if z == 96:
        return pyo.Constraint.Skip
    return (model.soc[k, z+1] == model.soc[k, z] - model.cons[k, z] +
            sum(model.real_p[k, l, z] for l in model.L) * 0.25)
model.con_soc_dynamics = pyo.Constraint(model.K, model.Z, rule=soc_dynamics_rule)
 
# (NB17) SOC-Obergrenze (muss für alle Typen gelten)
def soc_upper_rule(model, k, z):
    # SOC darf nicht größer sein als die Kapazität des zugewiesenen Typs
    return model.soc[k, z] <= sum(model.type_assignment[k, t] * model.soc_e[t] for t in model.TE) + \
                               sum(model.type_assignment[k, t] * 1000 for t in model.TD)  # Große Zahl für Diesel
model.con_soc_upper = pyo.Constraint(model.K, model.Z, rule=soc_upper_rule)
 
# (NB18) KREISLAUF: Start = Ende
def soc_cycle_rule(model, k):
    return model.soc[k, 1] == model.soc[k, 96]
model.con_soc_cycle = pyo.Constraint(model.K, rule=soc_cycle_rule)
 
# --- 5.5 LADE-LOGIK (ANGEPASST) ---
 
# (NB21) Ladeleistung begrenzt durch LKW-Typ
def charging_power_limit_rule(model, k, l, z):
    # max_p für den zugewiesenen Typ
    return model.real_p[k, l, z] <= sum(model.type_assignment[k, t] * model.max_p_e[t] for t in model.T)
model.con_charging_power_limit = pyo.Constraint(model.K, model.L, model.Z, rule=charging_power_limit_rule)
 
# (NB22) Nur angesteckte LKWs können laden
def assign_requires_plug_rule(model, k, l, z):
    return model.assign[k, l, z] <= model.plug[k, l, z]
model.con_assign_requires_plug = pyo.Constraint(model.K, model.L, model.Z, rule=assign_requires_plug_rule)
 
# (NB23) LKW nur an einer Säule gleichzeitig
def one_charger_per_truck_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1
model.con_one_charger_per_truck_constraint = pyo.Constraint(model.K, model.Z, rule=one_charger_per_truck_rule)
 
# (NB24+25) Diesel-LKWs dürfen nicht laden - LINEARISIERT
def diesel_no_charging_rule(model, k, l, z):
    # assign kann nur 1 sein wenn type_assignment[k,t] für t in TE
    return model.assign[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)
model.con_diesel_no_charging = pyo.Constraint(model.K, model.L, model.Z, rule=diesel_no_charging_rule)
 
def diesel_no_plug_rule(model, k, l, z):
    return model.plug[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)
model.con_diesel_no_plug = pyo.Constraint(model.K, model.L, model.Z, rule=diesel_no_plug_rule)
 
# (NB26) Nicht gleichzeitig laden und fahren
def no_charge_while_driving_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1 - sum(model.active_tour[r, z] * model.a[r, k] for r in model.R)
model.con_no_charge_while_driving = pyo.Constraint(model.K, model.Z, rule=no_charge_while_driving_rule)
 
# (NB27) Bei Tourstart nicht angesteckt
def unplug_before_departure_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] <= 1 - model.depart[k, z+1]
model.con_unplug_before_departure = pyo.Constraint(model.K, model.L, model.Z, rule=unplug_before_departure_rule)
 
# (NB28) Abstecken nur wenn erlaubt
def unplug_timing_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] - model.plug[k, l, z+1] <= model.unplug_ok[z]
model.con_unplug_timing = pyo.Constraint(model.K, model.L, model.Z, rule=unplug_timing_rule)
 
# --- 5.6 LADESÄULEN-KAPAZITÄTEN ---
 
# (NB29) Anzahl ladender LKWs pro Säule
def charger_assign_capacity_rule(model, l, z):
    return sum(model.assign[k, l, z] for k in model.K) <= model.y_l[l] * model.cs_l[l]
model.con_charger_assign_capacity = pyo.Constraint(model.L, model.Z, rule=charger_assign_capacity_rule)
 
# (NB30) Anzahl angesteckter LKWs pro Säule
def charger_plug_capacity_rule(model, l, z):
    return sum(model.plug[k, l, z] for k in model.K) <= model.y_l[l] * model.cs_l[l]
model.con_charger_plug_capacity = pyo.Constraint(model.L, model.Z, rule=charger_plug_capacity_rule)
 
# (NB31) Gesamtladeleistung pro Säule
def charger_power_capacity_rule(model, l, z):
    return sum(model.real_p[k, l, z] for k in model.K) <= model.y_l[l] * model.max_p_l[l]
model.con_charger_power_capacity = pyo.Constraint(model.L, model.Z, rule=charger_power_capacity_rule)
 
# --- 5.7 NACHT-LADELOGIK (VEREINFACHT) ---
 
# Vorerst deaktiviert für erste Tests
# Die SOC-Dynamik erzwingt bereits das notwendige Laden
 
# --- 5.8 NETZ UND SPEICHER ---
 
# (NB37) Netzlastbilanz
def grid_balance_rule(model, z):
    return (model.p_grid[z] == sum(model.real_p[k, l, z] for k in model.K for l in model.L) +
            model.p_l_s[z] - model.p_e_s[z])
model.con_grid_balance = pyo.Constraint(model.Z, rule=grid_balance_rule)
 
# (NB38) Netzanschluss-Limit
def grid_limit_rule(model, z):
    return model.p_grid[z] <= model.p_grid_max + 500 * model.u
 
model.con_grid_limit = pyo.Constraint(model.Z, rule=grid_limit_rule)
 
# (NB39) Leistungsspitze definieren
def peak_power_rule(model, z):
    return model.p_grid[z] <= model.p_peak
 
model.con_peak_power = pyo.Constraint(model.Z, rule=peak_power_rule)
 
# (NB40) Speicher-Dynamik
def storage_dynamics_rule(model, z):
    if z == 96:
        return pyo.Constraint.Skip
    return (model.soc_s[z+1] == model.soc_s[z] + model.p_l_s[z] * model.delta_t -
            (1/model.nrt) * model.p_e_s[z] * model.delta_t)
 
model.con_storage_dynamics = pyo.Constraint(model.Z, rule=storage_dynamics_rule)
 
# (NB41) Speicher tagesneutral
def storage_neutral_rule(model):
    return model.soc_s[1] == model.soc_s[96]
 
model.con_storage_neutral = pyo.Constraint(rule=storage_neutral_rule)
 
# (NB42) Speicher-Obergrenze
def storage_capacity_rule(model, z):
    return model.soc_s[z] <= model.q_s
 
model.con_storage_capacity = pyo.Constraint(model.Z, rule=storage_capacity_rule)
 
# (NB43) Speicher-Untergrenze
def storage_reserve_rule(model, z):
    return model.soc_s[z] >= model.dod * model.q_s
 
model.con_storage_reserve = pyo.Constraint(model.Z, rule=storage_reserve_rule)
 
# (NB44) Speicher-Lademodus
def storage_charge_mode_rule(model, z):
    return model.p_l_s[z] <= model.p_s
 
model.con_storage_charge_mode = pyo.Constraint(model.Z, rule=storage_charge_mode_rule)
 
def storage_charge_mode_binary_rule(model, z):
    return model.p_l_s[z] <= 10000 * model.mode_s[z]
 
model.con_storage_charge_mode_binary = pyo.Constraint(model.Z, rule=storage_charge_mode_binary_rule)
 
# (NB45) Speicher-Entlademodus
def storage_discharge_mode_rule(model, z):
    return model.p_e_s[z] <= model.p_s
 
model.con_storage_discharge_mode = pyo.Constraint(model.Z, rule=storage_discharge_mode_rule)
 
def storage_discharge_mode_binary_rule(model, z):
    return model.p_e_s[z] <= 10000 * (1 - model.mode_s[z])
 
model.con_storage_discharge_mode_binary = pyo.Constraint(model.Z, rule=storage_discharge_mode_binary_rule)
 
# ============================================================================
# 6. ZIELFUNKTION (ANGEPASST)
# ============================================================================
 
def objective_rule(model):
    # C_trucks: LKW-Fixkosten (jetzt ueber type_assignment)
    C_trucks = sum(
        sum(
            model.type_assignment[k, t] * (model.cap_d[t] + model.opx_d[t] + model.kfz_d[t])
            for t in model.TD
        ) +
        sum(
            model.type_assignment[k, t] * (model.cap_e[t] + model.opx_e[t])
            for t in model.TE
        )
        for k in model.K
    )
 
    # C_chargers: Ladeinfrastruktur
    C_chargers = sum(
        model.y_l[l] * (model.cap_l[l] + model.opx_l[l])
        for l in model.L
    )
 
    # C_grid_trafo: Netzanschluss/Trafo
    C_grid_trafo = 10000 * model.u
 
    # C_storage: Stationaerer Speicher
    C_storage = (model.capP_s * model.p_s + model.capQ_s * model.q_s) + \
                model.opx_s * (model.capP_s * model.p_s + model.capQ_s * model.q_s)
 
    # C_diesel_var: Dieselverbrauch + Maut (linearisiert)
    C_diesel_var = 260 * sum(
        sum(
            sum(
                model.a[r, k] * model.type_assignment[k, t] *
                (model.c_m_d * model.mDist[r] + model.c_diesel * (model.dist[r]/100) * model.avgDv_d[t])
                for t in model.TD
            )
            for k in model.K
        )
        for r in model.R
    )
 
    # C_electricity: Strom
    C_electricity = model.c_gr + model.cPeak * model.p_peak + \
                    260 * model.c_e * sum(model.p_grid[z] * model.delta_t for z in model.Z)
 
    # C_revenue: THG-Erloese
    C_revenue = sum(
        sum(
            model.type_assignment[k, t] * model.thg_e[t]
            for t in model.TE
        )
        for k in model.K
    )
 
    return C_trucks + C_chargers + C_grid_trafo + C_storage + C_diesel_var + C_electricity - C_revenue
 
model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
 
# ============================================================================
# SOLVER INSTALLATION UND SETUP
# ============================================================================
 
# Solver installieren
print("Installiere Solver...")
# !apt-get install -y -qq glpk-utils
# !apt-get install -y -qq coinor-cbc
print("Solver-Installation abgeschlossen.\n")
 
# ============================================================================
# 7. SOLVER
# ============================================================================
 
print("=" * 80)
print("MODELL WIRD GELOEST...")
print("=" * 80)
 
# Versuche verschiedene Solver
solver = None
solver_name = None
 
# Versuche zuerst GLPK
try:
    solver = SolverFactory('glpk')
    if solver.available():
        solver_name = 'glpk'
        print(f"Verwende Solver: {solver_name}")
except:
    pass
 
# Falls GLPK nicht verfuegbar, versuche CBC
if solver is None or not solver.available():
    try:
        solver = SolverFactory('cbc')
        if solver.available():
            solver_name = 'cbc'
            print(f"Verwende Solver: {solver_name}")
    except:
        pass
 
# Wenn kein Solver verfuegbar
if solver is None or not solver.available():
    print("FEHLER: Kein Solver verfuegbar!")
    print("Versuche manuelle Installation...")
    # !pip install -q glpk
    solver = SolverFactory('glpk')
    solver_name = 'glpk'
 
# Optional: Solver-Optionen setzen
if solver_name == 'glpk':
    solver.options['tmlim'] = 600  # Zeitlimit 10 Minuten fuer GLPK
elif solver_name == 'cbc':
    solver.options['seconds'] = 600  # Zeitlimit 10 Minuten fuer CBC
 
# Modell loesen
print(f"\nStarte Optimierung mit {solver_name}...\n")
results = solver.solve(model, tee=True)
 
# ============================================================================
# 8. ERGEBNIS-AUSGABE
# ============================================================================
 
print("\n" + "=" * 80)
print("OPTIMIERUNGSERGEBNISSE")
print("=" * 80)
 
# Status pruefen
if (results.solver.status == pyo.SolverStatus.ok and
    results.solver.termination_condition == pyo.TerminationCondition.optimal):
 
    print("\n OPTIMALE LOESUNG GEFUNDEN\n")
 
    # A) ZIELFUNKTIONSWERT
    print("-" * 80)
    print("ZIELFUNKTIONSWERT")
    print("-" * 80)
    print(f"Gesamtkosten (jaehrlich): {pyo.value(model.obj):,.2f} EUR")
    print()
 
    # FLOTTENZUSAMMENSETZUNG (NEU!)
    print("-" * 80)
    print("OPTIMALE FLOTTENZUSAMMENSETZUNG")
    print("-" * 80)
 
    fleet_composition = {}
    for k in model.K:
        for t in model.T:
            if pyo.value(model.type_assignment[k, t]) > 0.5:
                if t not in fleet_composition:
                    fleet_composition[t] = []
                fleet_composition[t].append(k)
 
    for t in sorted(fleet_composition.keys()):
        print(f"\n{t}: {len(fleet_composition[t])} LKW(s)")
        print(f"  LKW-IDs: {fleet_composition[t]}")
 
    print()
 
    # B) ZUORDNUNG LKW <-> TOUREN
    print("-" * 80)
    print("TOUR-ZUORDNUNG ZU LKWs")
    print("-" * 80)
 
    for k in sorted(model.K):
        tours_assigned = [r for r in model.R if pyo.value(model.a[r, k]) > 0.5]
        if tours_assigned:
            # Finde Typ
            truck_type = None
            for t in model.T:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    truck_type = t
                    break
            print(f"\nLKW {k} (Typ: {truck_type}):")
            for r in tours_assigned:
                start_time = (model.s_r[r] - 1) * 0.25
                end_time = (model.e_r[r] - 1) * 0.25
                print(f"  - Tour {r:4s}: Start {start_time:5.2f}h (Int {model.s_r[r]:2d}), "
                      f"Ende {end_time:5.2f}h (Int {model.e_r[r]:2d}), "
                      f"Distanz {model.dist[r]:3.0f} km")
    print()
 
    # C) LADEINFRASTRUKTUR
    print("-" * 80)
    print("INSTALLIERTE LADEINFRASTRUKTUR")
    print("-" * 80)
 
    total_chargers = 0
    for l in model.L:
        num_chargers = int(pyo.value(model.y_l[l]))
        if num_chargers > 0:
            total_points = num_chargers * model.cs_l[l]
            print(f"{l:20s}: {num_chargers} Saeule(n) x {model.cs_l[l]} Ladepunkte "
                  f"= {total_points} Ladepunkte gesamt")
            print(f"                      Max. Leistung: {model.max_p_l[l]} kW pro Saeule")
            total_chargers += num_chargers
 
    print(f"\nGesamt: {total_chargers} Ladesaeule(n)")
    print()
 
    # D) ZUSAETZLICHE INFORMATIONEN
    print("-" * 80)
    print("WEITERE KENNZAHLEN")
    print("-" * 80)
 
    # Trafo
    trafo_installed = pyo.value(model.u) > 0.5
    print(f"Transformator installiert: {'Ja' if trafo_installed else 'Nein'}")
 
    # Netzspitze
    peak_power = pyo.value(model.p_peak)
    print(f"Netzspitzenleistung: {peak_power:.2f} kW")
 
    # Speicher
    storage_power = pyo.value(model.p_s)
    storage_capacity = pyo.value(model.q_s)
    if storage_power > 0.01 or storage_capacity > 0.01:
        print(f"Speicher installiert: Leistung {storage_power:.2f} kW, "
              f"Kapazitaet {storage_capacity:.2f} kWh")
    else:
        print("Speicher installiert: Nein")
 
    print()
 
    # E) SOC-INFORMATIONEN (optional, nur fuer E-LKWs)
    print("-" * 80)
    print("LADEZUSTAENDE E-LKWs (Start und Ende)")
    print("-" * 80)
 
    for k in model.K:
        is_electric = sum(pyo.value(model.type_assignment[k, t]) for t in model.TE) > 0.5
        if is_electric:
            truck_type = None
            for t in model.TE:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    truck_type = t
                    break
            soc_start = pyo.value(model.soc[k, 1])
            soc_end = pyo.value(model.soc[k, 96])
            print(f"LKW {k} ({truck_type}): Start {soc_start:.1f} kWh, "
                  f"Ende {soc_end:.1f} kWh "
                  f"(Kapazitaet: {model.soc_e[truck_type]} kWh)")
 
    print()
 
elif results.solver.termination_condition == pyo.TerminationCondition.infeasible:
    print("\n MODELL IST INFEASIBLE (keine zulaessige Loesung)")
    print("Moegliche Ursachen:")
    print("  - Widerspruechliche Nebenbedingungen")
    print("  - Zu restriktive Zeitfenster")
    print("  - Unzureichende Ladeinfrastruktur-Kapazitaeten")
 
else:
    print(f"\n SOLVER-STATUS: {results.solver.status}")
    print(f"TERMINATION CONDITION: {results.solver.termination_condition}")
 
print("\n" + "=" * 80)
print("OPTIMIERUNG ABGESCHLOSSEN")
print("=" * 80)