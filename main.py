# ============================================================================
# MILP-OPTIMIERUNGSMODELL FÜR LKW-FLOTTENPLANUNG MIT LADEINFRASTRUKTUR
# Pyomo ConcreteModel - Google Colab Ready
# MIT OPTIMIERUNG DER LKW-TYPEN - VOLLSTÄNDIG LINEARISIERT
# ============================================================================
 
# Installation und Import
!pip install pyomo -q
!apt-get install -y -qq glpk-utils
 
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
model.K = pyo.Set(initialize=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
 
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
 
dist_data = {
    't-4': 250, 't-5': 250, 't-6': 250,
    's-1': 120, 's-2': 120, 's-3': 120, 's-4': 120,
    'w1': 100, 'w2': 100, 'w3': 100, 'w4': 100, 'w5': 100, 'w6': 100, 'w7': 100,
    'r1': 285, 'r2': 250, 'r3': 235, 'h3': 180, 'h4': 180, 'k1': 275
}
model.dist = pyo.Param(model.R, initialize=dist_data)
 
mDist_data = {
    't-4': 150, 't-5': 150, 't-6': 150,
    's-1': 32, 's-2': 32, 's-3': 32, 's-4': 32,
    'w1': 32, 'w2': 32, 'w3': 32, 'w4': 32, 'w5': 32, 'w6': 32, 'w7': 32,
    'r1': 259, 'r2': 220, 'r3': 219, 'h3': 160, 'h4': 160, 'k1': 235
}
model.mDist = pyo.Param(model.R, initialize=mDist_data)
 
s_r_data = {
    't-4': 28, 't-5': 27, 't-6': 25,
    's-1': 23, 's-2': 25, 's-3': 37, 's-4': 27,
    'w1': 23, 'w2': 33, 'w3': 28, 'w4': 25, 'w5': 29, 'w6': 23, 'w7': 30,
    'r1': 73, 'r2': 67, 'r3': 72, 'h3': 76, 'h4': 75, 'k1': 67
}
model.s_r = pyo.Param(model.R, initialize=s_r_data)
 
e_r_data = {
    't-4': 69, 't-5': 70, 't-6': 67,
    's-1': 63, 's-2': 65, 's-3': 65, 's-4': 67,
    'w1': 63, 'w2': 73, 'w3': 69, 'w4': 65, 'w5': 69, 'w6': 63, 'w7': 70,
    'r1': 91, 'r2': 88, 'r3': 87, 'h3': 92, 'h4': 91, 'k1': 91
}
model.e_r = pyo.Param(model.R, initialize=e_r_data)
 
def dur_z_init(model, r):
    return model.e_r[r] - model.s_r[r]
model.dur_z = pyo.Param(model.R, initialize=dur_z_init)
 
def start_at_init(model, r, z):
    return 1 if z == model.s_r[r] else 0
model.start_at = pyo.Param(model.R, model.Z, initialize=start_at_init)
 
def end_at_init(model, r, z):
    return 1 if z == model.e_r[r] else 0
model.end_at = pyo.Param(model.R, model.Z, initialize=end_at_init)
 
def active_tour_init(model, r, z):
    return 1 if model.s_r[r] <= z < model.e_r[r] else 0
model.active_tour = pyo.Param(model.R, model.Z, initialize=active_tour_init)
 
# --- Diesel-LKW-Parameter ---
 
model.cap_d = pyo.Param(model.TD, initialize={'ActrosL': 24000})
model.opx_d = pyo.Param(model.TD, initialize={'ActrosL': 6000})
model.kfz_d = pyo.Param(model.TD, initialize={'ActrosL': 556})
model.avgDv_d = pyo.Param(model.TD, initialize={'ActrosL': 0.26})
model.c_diesel = pyo.Param(initialize=1.5)
model.c_m_d = pyo.Param(initialize=0.34)
 
# --- Elektro-LKW-Parameter ---
 
model.cap_e = pyo.Param(model.TE, initialize={'eActros600': 60000, 'eActros400': 50000})
model.opx_e = pyo.Param(model.TE, initialize={'eActros600': 6000, 'eActros400': 5000})
model.avgEv_e = pyo.Param(model.TE, initialize={'eActros600': 1.1, 'eActros400': 1.05})
model.soc_e = pyo.Param(model.TE, initialize={'eActros600': 621, 'eActros400': 414})
model.thg_e = pyo.Param(model.TE, initialize={'eActros600': 1000, 'eActros400': 1000})
 
max_p_e_data = {'eActros600': 400, 'eActros400': 400, 'ActrosL': 0}
model.max_p_e = pyo.Param(model.T, initialize=max_p_e_data)
 
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

model.z6 = pyo.Param(initialize=25)
 
def unplug_ok_init(model, z):
    if z in model.Z_day:
        return 1
    elif z + 1 == model.z6:
        return 1
    else:
        return 0
model.unplug_ok = pyo.Param(model.Z, initialize=unplug_ok_init)
 
# ============================================================================
# 3️⃣ ENTSCHEIDUNGSVARIABLEN
# ============================================================================
 
# --- LKW-Typ-Zuordnung ---
model.type_assignment = pyo.Var(model.K, model.T, domain=pyo.Binary)

# LKW wird benutzt (mindestens eine Tour)
model.truck_used = pyo.Var(model.K, domain=pyo.Binary)

# Hilfsvariable für Linearisierung: truck_type_used[k,t] = truck_used[k] * type_assignment[k,t]
model.truck_type_used = pyo.Var(model.K, model.T, domain=pyo.Binary)
 
# --- Hilfsvariable für Linearisierung: a_type[r,k,t] = a[r,k] * type_assignment[k,t] ---
model.a_type = pyo.Var(model.R, model.K, model.T, domain=pyo.Binary)
 
# --- Zuordnung & Bewegung ---
model.a = pyo.Var(model.R, model.K, domain=pyo.Binary)
model.depart = pyo.Var(model.K, model.Z, domain=pyo.Binary)

 
# --- Laden ---
model.assign = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.plug = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.real_p = pyo.Var(model.K, model.L, model.Z, domain=pyo.NonNegativeReals)
model.y_l = pyo.Var(model.L, domain=pyo.NonNegativeIntegers, bounds=(0, model.Nmax))
 
# --- Energiezustände ---
model.soc = pyo.Var(model.K, model.Z, domain=pyo.NonNegativeReals)
 
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
# 4️⃣ LINEARISIERUNG: a_type[r,k,t] = a[r,k] * type_assignment[k,t]
# ============================================================================
 
# Für ALLE Typen (TD und TE)
def a_type_lin1_rule(model, r, k, t):
    return model.a_type[r, k, t] <= model.a[r, k]
model.con_a_type_lin1 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin1_rule)
 
def a_type_lin2_rule(model, r, k, t):
    return model.a_type[r, k, t] <= model.type_assignment[k, t]
model.con_a_type_lin2 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin2_rule)
 
def a_type_lin3_rule(model, r, k, t):
    return model.a_type[r, k, t] >= model.a[r, k] + model.type_assignment[k, t] - 1
model.con_a_type_lin3 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin3_rule)
 
# ============================================================================
# 5️⃣ NEBENBEDINGUNGEN
# ============================================================================
 
# --- 5.0 LKW-TYP-ZUORDNUNG ---
 
def one_type_per_truck_rule(model, k):
    return sum(model.type_assignment[k, t] for t in model.T) == 1
model.con_one_type_per_truck = pyo.Constraint(model.K, rule=one_type_per_truck_rule)

# --- 5.0b TRUCK_USED LOGIK ---

def truck_used_lower_rule(model, k):
    return sum(model.a[r, k] for r in model.R) <= len(model.R) * model.truck_used[k]
model.con_truck_used_lower = pyo.Constraint(model.K, rule=truck_used_lower_rule)

def truck_used_upper_rule(model, k):
    return model.truck_used[k] <= sum(model.a[r, k] for r in model.R)
model.con_truck_used_upper = pyo.Constraint(model.K, rule=truck_used_upper_rule)

# --- LINEARISIERUNG: truck_type_used[k,t] = truck_used[k] * type_assignment[k,t] ---

def ttu_lin1_rule(model, k, t):
    return model.truck_type_used[k, t] <= model.truck_used[k]
model.con_ttu_lin1 = pyo.Constraint(model.K, model.T, rule=ttu_lin1_rule)

def ttu_lin2_rule(model, k, t):
    return model.truck_type_used[k, t] <= model.type_assignment[k, t]
model.con_ttu_lin2 = pyo.Constraint(model.K, model.T, rule=ttu_lin2_rule)

def ttu_lin3_rule(model, k, t):
    return model.truck_type_used[k, t] >= model.truck_used[k] + model.type_assignment[k, t] - 1
model.con_ttu_lin3 = pyo.Constraint(model.K, model.T, rule=ttu_lin3_rule)

# --- 5.1 TOUR-ZUORDNUNG ---
 
def tour_assignment_rule(model, r):
    return sum(model.a[r, k] for k in model.K) == 1
model.con_tour_assignment = pyo.Constraint(model.R, rule=tour_assignment_rule)
 
# --- 5.2 LKW-BEWEGUNGSLOGIK ---
 
def no_concurrent_tours_rule(model, k, z):
    return sum(model.active_tour[r, z] * model.a[r, k] for r in model.R) <= 1
model.con_no_concurrent_tours = pyo.Constraint(model.K, model.Z, rule=no_concurrent_tours_rule)
 
def no_concurrent_arrivals_rule(model, k, z):
    return sum(model.end_at[r, z] * model.a[r, k] for r in model.R) <= 1
model.con_no_concurrent_arrivals = pyo.Constraint(model.K, model.Z, rule=no_concurrent_arrivals_rule)
 
def depart_definition_rule(model, k, z):
    return model.depart[k, z] == sum(model.start_at[r, z] * model.a[r, k] for r in model.R)
model.con_depart_definition = pyo.Constraint(model.K, model.Z, rule=depart_definition_rule)
 

 
# --- 5.4 ENERGIE-DYNAMIK ---
 
# Energieverbrauch als Expression (JETZT LINEAR mit a_type)
def cons_expr_rule(model, k, z):
    return sum(
        sum(
            model.a_type[r, k, t] * model.active_tour[r, z] *
            (model.dist[r] * model.avgEv_e[t] / model.dur_z[r])
            for r in model.R
        )
        for t in model.TE
    )
model.cons = pyo.Expression(model.K, model.Z, rule=cons_expr_rule)
 
# SOC-Dynamik
def soc_dynamics_rule(model, k, z):
    if z == 96:
        return pyo.Constraint.Skip
    return (model.soc[k, z+1] == model.soc[k, z] - model.cons[k, z] +
            sum(model.real_p[k, l, z] for l in model.L) * 0.25)
model.con_soc_dynamics = pyo.Constraint(model.K, model.Z, rule=soc_dynamics_rule)
 
# SOC-Obergrenze
def soc_upper_rule(model, k, z):
    return model.soc[k, z] <= sum(model.type_assignment[k, t] * model.soc_e[t] for t in model.TE) + \
                               sum(model.type_assignment[k, t] * 1000 for t in model.TD)
model.con_soc_upper = pyo.Constraint(model.K, model.Z, rule=soc_upper_rule)
 
# KREISLAUF: Start = Ende
def soc_cycle_rule(model, k):
    return model.soc[k, 1] == model.soc[k, 96]
model.con_soc_cycle = pyo.Constraint(model.K, rule=soc_cycle_rule)

#Gesamtbegrenzung Ladesäulen: maximal 3 Säulen insgesamt
def total_charger_limit_rule(model):
    return sum(model.y_l[l] for l in model.L) <= model.Nmax
model.con_total_charger_limit = pyo.Constraint(rule=total_charger_limit_rule) 
# Neuer Code
# --- 5.5 LADE-LOGIK ---
# 1. NEU: Nur laden wenn angesteckt
def charging_requires_assign_rule(model, k, l, z):
    return model.real_p[k, l, z] <= model.assign[k, l, z] * 10000
model.con_charging_requires_assign = pyo.Constraint(model.K, model.L, model.Z, rule=charging_requires_assign_rule)


def charging_power_limit_rule(model, k, l, z):
    return model.real_p[k, l, z] <= sum(model.type_assignment[k, t] * model.max_p_e[t] for t in model.T)
model.con_charging_power_limit = pyo.Constraint(model.K, model.L, model.Z, rule=charging_power_limit_rule)
# ---
def assign_requires_plug_rule(model, k, l, z):
    return model.assign[k, l, z] <= model.plug[k, l, z]
model.con_assign_requires_plug = pyo.Constraint(model.K, model.L, model.Z, rule=assign_requires_plug_rule)
 
def one_charger_per_truck_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1
model.con_one_charger_per_truck = pyo.Constraint(model.K, model.Z, rule=one_charger_per_truck_rule)
 
def diesel_no_charging_rule(model, k, l, z):
    return model.assign[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)
model.con_diesel_no_charging = pyo.Constraint(model.K, model.L, model.Z, rule=diesel_no_charging_rule)
 
def diesel_no_plug_rule(model, k, l, z):
    return model.plug[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)
model.con_diesel_no_plug = pyo.Constraint(model.K, model.L, model.Z, rule=diesel_no_plug_rule)
 
def no_charge_while_driving_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1 - sum(model.active_tour[r, z] * model.a[r, k] for r in model.R)
model.con_no_charge_while_driving = pyo.Constraint(model.K, model.Z, rule=no_charge_while_driving_rule)
 
def unplug_before_departure_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] <= 1 - model.depart[k, z+1]
model.con_unplug_before_departure = pyo.Constraint(model.K, model.L, model.Z, rule=unplug_before_departure_rule)
 
def unplug_timing_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] - model.plug[k, l, z+1] <= model.unplug_ok[z]
model.con_unplug_timing = pyo.Constraint(model.K, model.L, model.Z, rule=unplug_timing_rule)
 
# --- 5.6 LADESÄULEN-KAPAZITÄTEN ---
 
def charger_assign_capacity_rule(model, l, z):
    return sum(model.assign[k, l, z] for k in model.K) <= model.y_l[l] * model.cs_l[l]
model.con_charger_assign_capacity = pyo.Constraint(model.L, model.Z, rule=charger_assign_capacity_rule)
 
def charger_plug_capacity_rule(model, l, z):
    return sum(model.plug[k, l, z] for k in model.K) <= model.y_l[l] * model.cs_l[l]
model.con_charger_plug_capacity = pyo.Constraint(model.L, model.Z, rule=charger_plug_capacity_rule)
 
def charger_power_capacity_rule(model, l, z):
    return sum(model.real_p[k, l, z] for k in model.K) <= model.y_l[l] * model.max_p_l[l]
model.con_charger_power_capacity = pyo.Constraint(model.L, model.Z, rule=charger_power_capacity_rule)
 
# --- 5.8 NETZ UND SPEICHER ---
 
def grid_balance_rule(model, z):
    return (model.p_grid[z] == sum(model.real_p[k, l, z] for k in model.K for l in model.L) +
            model.p_l_s[z] - model.p_e_s[z])
model.con_grid_balance = pyo.Constraint(model.Z, rule=grid_balance_rule)
 
def grid_limit_rule(model, z):
    return model.p_grid[z] <= model.p_grid_max + 500 * model.u
model.con_grid_limit = pyo.Constraint(model.Z, rule=grid_limit_rule)
 
def peak_power_rule(model, z):
    return model.p_grid[z] <= model.p_peak
model.con_peak_power = pyo.Constraint(model.Z, rule=peak_power_rule)
 
def storage_dynamics_rule(model, z):
    if z == 96:
        return pyo.Constraint.Skip
    return (model.soc_s[z+1] == model.soc_s[z] + model.p_l_s[z] * model.delta_t -
            (1/model.nrt) * model.p_e_s[z] * model.delta_t)
model.con_storage_dynamics = pyo.Constraint(model.Z, rule=storage_dynamics_rule)
 
def storage_neutral_rule(model):
    return model.soc_s[1] == model.soc_s[96]
model.con_storage_neutral = pyo.Constraint(rule=storage_neutral_rule)
 
def storage_capacity_rule(model, z):
    return model.soc_s[z] <= model.q_s
model.con_storage_capacity = pyo.Constraint(model.Z, rule=storage_capacity_rule)
 
def storage_reserve_rule(model, z):
    return model.soc_s[z] >= model.dod * model.q_s
model.con_storage_reserve = pyo.Constraint(model.Z, rule=storage_reserve_rule)
 
def storage_charge_mode_rule(model, z):
    return model.p_l_s[z] <= model.p_s
model.con_storage_charge_mode = pyo.Constraint(model.Z, rule=storage_charge_mode_rule)
 
def storage_charge_mode_binary_rule(model, z):
    return model.p_l_s[z] <= 10000 * model.mode_s[z]
model.con_storage_charge_mode_binary = pyo.Constraint(model.Z, rule=storage_charge_mode_binary_rule)
 
def storage_discharge_mode_rule(model, z):
    return model.p_e_s[z] <= model.p_s
model.con_storage_discharge_mode = pyo.Constraint(model.Z, rule=storage_discharge_mode_rule)
 
def storage_discharge_mode_binary_rule(model, z):
    return model.p_e_s[z] <= 10000 * (1 - model.mode_s[z])
model.con_storage_discharge_mode_binary = pyo.Constraint(model.Z, rule=storage_discharge_mode_binary_rule)
 
# ============================================================================
# 6️⃣ ZIELFUNKTION (LINEARISIERT)
# ============================================================================
 
def objective_rule(model):
    # C_trucks: NUR für benutzte LKWs
    C_trucks = sum(
        sum(model.truck_type_used[k, t] * (model.cap_d[t] + model.opx_d[t] + model.kfz_d[t]) for t in model.TD) +
        sum(model.truck_type_used[k, t] * (model.cap_e[t] + model.opx_e[t]) for t in model.TE)
        for k in model.K
    )
    
    C_chargers = sum(model.y_l[l] * (model.cap_l[l] + model.opx_l[l]) for l in model.L)
    
    C_grid_trafo = 10000 * model.u
    
    C_storage = (1 + model.opx_s) * (model.capP_s * model.p_s + model.capQ_s * model.q_s)
    
    C_diesel_var = 260 * sum(
        model.a_type[r, k, t] * (model.c_m_d * model.mDist[r] +
                                  model.c_diesel * (model.dist[r]) * model.avgDv_d[t])
        for r in model.R for k in model.K for t in model.TD
    )
    
    C_electricity = model.c_gr + model.cPeak * model.p_peak + \
                    260 * model.c_e * sum(model.p_grid[z] * model.delta_t for z in model.Z)
    
    C_revenue = sum(
        sum(model.truck_type_used[k, t] * model.thg_e[t] for t in model.TE)
        for k in model.K
    )
    
    return C_trucks + C_chargers + C_grid_trafo + C_storage + C_diesel_var + C_electricity - C_revenue

model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
# ============================================================================
# SOLVER INSTALLATION UND SETUP
# ============================================================================
 
# Solver installieren
print("Installiere Solver...")
!apt-get install -y -qq glpk-utils
!apt-get install -y -qq coinor-cbc
print("Solver-Installation abgeschlossen.\n")
 
# ============================================================================
# 7️⃣ SOLVER
# ============================================================================
 
print("=" * 80)
print("MODELL WIRD GELÖST...")
print("=" * 80)
 
# CBC bevorzugen (bessere Heuristiken als GLPK)
solver = None
solver_name = None
 
# Solver auswählen
solver = None
solver_name = None

# Versuche zuerst HiGHS (beste Ausgabe)
try:
    solver = SolverFactory('appsi_highs')
    if solver.available():
        solver_name = 'HiGHS'
        print(f"Verwende Solver: {solver_name}")
except:
    pass

# Falls HiGHS nicht verfügbar, CBC
if solver is None or not solver.available():
    try:
        solver = SolverFactory('cbc')
        if solver.available():
            solver_name = 'CBC'
            print(f"Verwende Solver: {solver_name}")
    except:
        pass

# Falls CBC nicht verfügbar, GLPK
if solver is None or not solver.available():
    try:
        solver = SolverFactory('glpk')
        if solver.available():
            solver_name = 'GLPK'
            print(f"Verwende Solver: {solver_name}")
    except:
        pass
 
# Solver-Optionen
    if solver_name == 'HiGHS':
        solver.options['time_limit'] = 3600
        solver.options['log_to_console'] = True
    elif solver_name == 'CBC':
        solver.options['seconds'] = 3600
        solver.options['heuristics'] = 'on'
        solver.options['round'] = 'on'
        solver.options['feas'] = 'on'
        solver.options['cuts'] = 'on'
    elif solver_name == 'GLPK':
        solver.options['tmlim'] = 3600
    
    print(f"\nStarte Optimierung (Zeitlimit: 1 Stunde)...\n")
    results = solver.solve(model, tee=True)
 
# Modell lösen
print(f"\nStarte Optimierung mit {solver_name} (Zeitlimit: 2 Stunden)...\n")
results = solver.solve(model, tee=True)
 
# ============================================================================
# ERGEBNIS-AUSWERTUNG (auch bei TimeLimit)
# ============================================================================
 
print("\n" + "=" * 80)
print("OPTIMIERUNGSERGEBNISSE")
print("=" * 80)
 
# Prüfe ob eine Lösung gefunden wurde (optimal ODER feasible bei TimeLimit)
solution_found = False
 
if results.solver.status == pyo.SolverStatus.ok:
    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
        print("\n✅ OPTIMALE LÖSUNG GEFUNDEN\n")
        solution_found = True
    elif results.solver.termination_condition == pyo.TerminationCondition.feasible:
        print("\n⚠️ ZULÄSSIGE LÖSUNG GEFUNDEN (nicht bewiesen optimal)\n")
        solution_found = True
       
elif results.solver.status == pyo.SolverStatus.aborted:
    # TimeLimit erreicht - prüfe ob trotzdem eine Lösung existiert
    if results.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit:
        print("\n⏱️ ZEITLIMIT ERREICHT\n")
        # Prüfe ob eine feasible Lösung gefunden wurde
        try:
            obj_value = pyo.value(model.obj)
            if obj_value is not None:
                print("✅ Beste gefundene Lösung wird verwendet.\n")
                solution_found = True
        except:
            pass
 
# Falls Lösung gefunden, Ergebnisse ausgeben
if solution_found:
    # ========================================================================
    # BASIS-INFORMATIONEN (aus Original-Ausgabe)
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("OPTIMIERUNGSERGEBNISSE - ÜBERSICHT")
    print("=" * 100)
    
    # --- ZIELFUNKTIONSWERT ---
    print("\n" + "-" * 100)
    print("📊 ZIELFUNKTIONSWERT")
    print("-" * 100)
    print(f"Gesamtkosten (jährlich): {pyo.value(model.obj):,.2f} €")
    
    # --- MIP-GAP ---
    try:
        if hasattr(results.problem, 'lower_bound') and hasattr(results.problem, 'upper_bound'):
            lower_bound = results.problem.lower_bound
            upper_bound = results.problem.upper_bound
            if lower_bound is not None and upper_bound is not None and upper_bound > 0:
                gap = 100 * (upper_bound - lower_bound) / upper_bound
                print(f"Untere Schranke:         {lower_bound:,.2f} €")
                print(f"Obere Schranke:          {upper_bound:,.2f} €")
                print(f"MIP-Gap:                 {gap:.4f} %")
        elif hasattr(results.solver, 'gap'):
            print(f"MIP-Gap:                 {results.solver.gap:.4f} %")
    except:
        pass
    
    # --- TOUR-ZUORDNUNG PRÜFUNG ---
    print("\n" + "-" * 100)
    print("🔍 TOUR-ZUORDNUNG PRÜFUNG")
    print("-" * 100)
    
    alle_touren = list(model.R)
    zugeordnete_touren = []
    nicht_zugeordnet = []
    
    for r in model.R:
        zugeordnet = False
        for k in model.K:
            if pyo.value(model.a[r, k]) > 0.5:
                zugeordnete_touren.append(r)
                zugeordnet = True
                break
        if not zugeordnet:
            nicht_zugeordnet.append(r)
            print(f"⚠️ Tour {r}: NICHT ZUGEORDNET!")
    
    print(f"\nGesamt Touren:    {len(alle_touren)}")
    print(f"Zugeordnet:       {len(zugeordnete_touren)}")
    print(f"Fehlend:          {len(nicht_zugeordnet)}")
    
    if len(nicht_zugeordnet) == 0:
        print("✅ Alle Touren sind zugeordnet.")
    
    # --- FLOTTEN-ZUSAMMENFASSUNG ---
    print("\n" + "-" * 100)
    print("🚗 FLOTTEN-ZUSAMMENFASSUNG")
    print("-" * 100)
    
    n_elektro = 0
    n_diesel = 0
    aktive_lkw = 0
    elektro_typen = {}
    diesel_typen = {}
    
    for k in model.K:
        hat_tour = any(pyo.value(model.a[r, k]) > 0.5 for r in model.R)
        if hat_tour:
            aktive_lkw += 1
            for t in model.TE:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    n_elektro += 1
                    elektro_typen[t] = elektro_typen.get(t, 0) + 1
                    break
            for t in model.TD:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    n_diesel += 1
                    diesel_typen[t] = diesel_typen.get(t, 0) + 1
                    break
    
    print(f"\nAktive LKWs gesamt:  {aktive_lkw}")
    print(f"  davon Elektro:     {n_elektro} ({100*n_elektro/aktive_lkw:.1f} %)" if aktive_lkw > 0 else "")
    for t, count in elektro_typen.items():
        print(f"    - {t}: {count}")
    print(f"  davon Diesel:      {n_diesel} ({100*n_diesel/aktive_lkw:.1f} %)" if aktive_lkw > 0 else "")
    for t, count in diesel_typen.items():
        print(f"    - {t}: {count}")
    
    # --- LKW-TYPEN UND TOUR-ZUORDNUNG (KOMPAKT) ---
    print("\n" + "-" * 100)
    print("🚛 LKW-TYPEN UND TOUR-ZUORDNUNG")
    print("-" * 100)
    
    print(f"\n{'LKW':<6} {'Typ':<15} {'Kat.':<6} {'Touren':<8} {'km/Tag':<10} {'Touren-Details'}")
    print("=" * 100)
    
    for k in sorted(model.K):
        # Finde Typ
        truck_type = None
        typ_kat = None
        for t in model.T:
            if pyo.value(model.type_assignment[k, t]) > 0.5:
                truck_type = t
                typ_kat = "E" if t in model.TE else "D"
                break
        
        # Finde ALLE Touren
        tours = [r for r in model.R if pyo.value(model.a[r, k]) > 0.5]
        
        if tours:
            total_km = sum(model.dist[r] for r in tours)
            sorted_tours = sorted(tours, key=lambda x: model.s_r[x])
            
            # Touren-Details formatieren
            tour_details = []
            for r in sorted_tours:
                start_h = (model.s_r[r]-1)*0.25
                end_h = (model.e_r[r]-1)*0.25
                tour_details.append(f"{r}({start_h:.1f}h-{end_h:.1f}h)")
            
            print(f"{k:<6} {truck_type:<15} [{typ_kat}]   {len(tours):<8} {total_km:<10} {', '.join(tour_details)}")
    
    # --- LADEINFRASTRUKTUR ---
    print("\n" + "-" * 100)
    print("⚡ LADEINFRASTRUKTUR")
    print("-" * 100)
    
    total_chargers = 0
    total_ladepunkte = 0
    max_ladeleistung = 0
    
    print(f"\n{'Typ':<20} {'Anzahl':<10} {'Ladepunkte':<12} {'Max. Leistung':<15} {'Kosten/Jahr'}")
    print("-" * 80)
    
    for l in model.L:
        n = int(round(pyo.value(model.y_l[l])))
        if n > 0:
            total_chargers += n
            punkte = n * model.cs_l[l]
            leistung = n * model.max_p_l[l]
            kosten = n * (model.cap_l[l] + model.opx_l[l])
            total_ladepunkte += punkte
            max_ladeleistung += leistung
            print(f"{l:<20} {n:<10} {punkte:<12} {leistung:<12} kW  {kosten:>10,.0f} €")
    
    if total_chargers == 0:
        print("Keine Ladesäulen installiert (reine Diesel-Flotte)")
    else:
        print("-" * 80)
        print(f"{'GESAMT':<20} {total_chargers:<10} {total_ladepunkte:<12} {max_ladeleistung:<12} kW")
    
    # --- NETZ & SPEICHER ---
    print("\n" + "-" * 100)
    print("🔌 NETZ & SPEICHER")
    print("-" * 100)
    
    trafo = pyo.value(model.u) > 0.5
    peak = pyo.value(model.p_peak)
    storage_p = pyo.value(model.p_s)
    storage_q = pyo.value(model.q_s)
    
    basis_netz = pyo.value(model.p_grid_max)
    erweiterung = 500 if trafo else 0
    max_netz = basis_netz + erweiterung
    
    print(f"\nNetzanschluss:")
    print(f"  Basis-Kapazität:           {basis_netz:.0f} kW")
    print(f"  Trafo-Erweiterung:         {'JA (+500 kW, 10.000 €/Jahr)' if trafo else 'NEIN'}")
    print(f"  MAX. NETZKAPAZITÄT:        {max_netz:.0f} kW")
    print(f"  Tatsächliche Spitzenlast:  {peak:.2f} kW")
    print(f"  Auslastung:                {100*peak/max_netz:.1f} %")
    
    print(f"\nSpeicher:")
    if storage_p > 0.01 or storage_q > 0.01:
        print(f"  Leistung:   {storage_p:.1f} kW")
        print(f"  Kapazität:  {storage_q:.1f} kWh")
    else:
        print(f"  NICHT INSTALLIERT")
    
    # --- ZUSAMMENFASSUNG OPTIONEN ---
    print("\n" + "-" * 100)
    print("📋 ZUSAMMENFASSUNG INVESTITIONSENTSCHEIDUNGEN")
    print("-" * 100)
    
    print(f"\n{'Option':<40} {'Entscheidung':<15} {'Jährliche Kosten'}")
    print("=" * 80)
    print(f"{'Trafo-Erweiterung (+500 kW)':<40} {'✅ JA' if trafo else '❌ NEIN':<15} {10000 if trafo else 0:>15,.0f} €")
    
    if storage_p > 0.01 or storage_q > 0.01:
        storage_cost = (1 + pyo.value(model.opx_s)) * (pyo.value(model.capP_s) * storage_p + pyo.value(model.capQ_s) * storage_q)
        print(f"{'Stationärer Speicher':<40} {'✅ JA':<15} {storage_cost:>15,.0f} €")
    else:
        print(f"{'Stationärer Speicher':<40} {'❌ NEIN':<15} {0:>15,.0f} €")
    
    if total_chargers > 0:
        charger_cost = sum(pyo.value(model.y_l[l]) * (model.cap_l[l] + model.opx_l[l]) for l in model.L)
        print(f"{'Ladeinfrastruktur':<40} {'✅ JA':<15} {charger_cost:>15,.0f} €")
    else:
        print(f"{'Ladeinfrastruktur':<40} {'❌ NEIN':<15} {0:>15,.0f} €")
    
    # ========================================================================
    # AB HIER: DETAILLIERTE ANALYSE FÜR TEILAUFGABE 3
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("DETAILLIERTE KOSTENANALYSE FÜR TEILAUFGABE 3")
    print("=" * 100)
    
    # ========================================================================
    # TEIL A: DETAILLIERTE KOSTENAUFSCHLÜSSELUNG
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("TEIL A: KOSTENAUFSCHLÜSSELUNG")
    print("=" * 100)
    
    # --- A1: DIESEL-LKW KOSTEN ---
    print("\n" + "-" * 100)
    print("A1: DIESEL-LKW KOSTEN (DETAILLIERT)")
    print("-" * 100)
    
    diesel_lkw_liste = []
    total_diesel_fix = 0
    total_diesel_var = 0
    
    for k in sorted(model.K):
        for t in model.TD:
            if pyo.value(model.truck_type_used[k, t]) > 0.5:
                # Fixkosten
                cap = model.cap_d[t]
                opx = model.opx_d[t]
                kfz = model.kfz_d[t]
                fix_gesamt = cap + opx + kfz
                
                # Variable Kosten (Touren dieses LKW)
                touren_km = 0
                touren_maut_km = 0
                tour_liste = []
                
                for r in model.R:
                    if pyo.value(model.a[r, k]) > 0.5:
                        touren_km += model.dist[r]
                        touren_maut_km += model.mDist[r]
                        tour_liste.append(r)
                
                # Variable Kosten berechnen
                kraftstoff_kosten = 260 * touren_km * model.avgDv_d[t] * model.c_diesel
                maut_kosten = 260 * touren_maut_km * model.c_m_d
                var_gesamt = kraftstoff_kosten + maut_kosten
                
                diesel_lkw_liste.append({
                    'k': k, 't': t, 'touren': tour_liste,
                    'km': touren_km, 'maut_km': touren_maut_km,
                    'cap': cap, 'opx': opx, 'kfz': kfz, 'fix': fix_gesamt,
                    'kraftstoff': kraftstoff_kosten, 'maut': maut_kosten, 'var': var_gesamt
                })
                
                total_diesel_fix += fix_gesamt
                total_diesel_var += var_gesamt
    
    if diesel_lkw_liste:
        print(f"\n{'LKW':<6} {'Typ':<12} {'Touren':<25} {'km/Tag':<10} {'Maut-km':<10}")
        print(f"{'':6} {'CAPEX':<12} {'OPEX':<12} {'Kfz-St.':<12} {'Fix ges.':<12}")
        print(f"{'':6} {'Kraftstoff':<15} {'Maut':<15} {'Var. ges.':<15}")
        print("=" * 100)
        
        for d in diesel_lkw_liste:
            print(f"\nLKW {d['k']:<3} {d['t']:<12} {str(d['touren']):<25} {d['km']:<10} {d['maut_km']:<10}")
            print(f"{'':6} {d['cap']:>10,.0f} € {d['opx']:>10,.0f} € {d['kfz']:>10,.0f} € {d['fix']:>10,.0f} €")
            print(f"{'':6} {d['kraftstoff']:>13,.2f} € {d['maut']:>13,.2f} € {d['var']:>13,.2f} €")
        
        print("\n" + "-" * 50)
        print(f"SUMME DIESEL-LKW FIXKOSTEN:      {total_diesel_fix:>15,.2f} €/Jahr")
        print(f"SUMME DIESEL-LKW VARIABLE:       {total_diesel_var:>15,.2f} €/Jahr")
        print(f"SUMME DIESEL-LKW GESAMT:         {total_diesel_fix + total_diesel_var:>15,.2f} €/Jahr")
    else:
        print("Keine Diesel-LKW in der Lösung.")
    
    # --- A2: ELEKTRO-LKW KOSTEN ---
    print("\n" + "-" * 100)
    print("A2: ELEKTRO-LKW KOSTEN (DETAILLIERT)")
    print("-" * 100)
    
    elektro_lkw_liste = []
    total_elektro_fix = 0
    total_thg_erloes = 0
    
    for k in sorted(model.K):
        for t in model.TE:
            if pyo.value(model.truck_type_used[k, t]) > 0.5:
                # Fixkosten
                cap = model.cap_e[t]
                opx = model.opx_e[t]
                thg = model.thg_e[t]
                fix_gesamt = cap + opx
                
                # Touren dieses LKW
                touren_km = 0
                tour_liste = []
                energie_verbrauch_tag = 0
                
                for r in model.R:
                    if pyo.value(model.a[r, k]) > 0.5:
                        touren_km += model.dist[r]
                        tour_liste.append(r)
                        energie_verbrauch_tag += model.dist[r] * model.avgEv_e[t]
                
                # Energieverbrauch pro Jahr
                energie_jahr = 260 * energie_verbrauch_tag
                
                elektro_lkw_liste.append({
                    'k': k, 't': t, 'touren': tour_liste,
                    'km': touren_km, 'cap': cap, 'opx': opx, 
                    'fix': fix_gesamt, 'thg': thg,
                    'energie_tag': energie_verbrauch_tag,
                    'energie_jahr': energie_jahr,
                    'batterie': model.soc_e[t]
                })
                
                total_elektro_fix += fix_gesamt
                total_thg_erloes += thg
    
    if elektro_lkw_liste:
        print(f"\n{'LKW':<6} {'Typ':<15} {'Batterie':<12} {'Touren':<25} {'km/Tag':<10}")
        print(f"{'':6} {'CAPEX':<15} {'OPEX':<15} {'Fix ges.':<15} {'THG-Erlös':<12}")
        print(f"{'':6} {'kWh/Tag':<15} {'kWh/Jahr':<15}")
        print("=" * 100)
        
        for e in elektro_lkw_liste:
            print(f"\nLKW {e['k']:<3} {e['t']:<15} {e['batterie']:<10} kWh {str(e['touren']):<25} {e['km']:<10}")
            print(f"{'':6} {e['cap']:>13,.0f} € {e['opx']:>13,.0f} € {e['fix']:>13,.0f} € {e['thg']:>10,.0f} €")
            print(f"{'':6} {e['energie_tag']:>13,.1f}    {e['energie_jahr']:>13,.1f}")
        
        print("\n" + "-" * 50)
        print(f"SUMME E-LKW FIXKOSTEN:           {total_elektro_fix:>15,.2f} €/Jahr")
        print(f"SUMME THG-ERLÖSE:               -{total_thg_erloes:>15,.2f} €/Jahr")
        print(f"SUMME E-LKW NETTO:               {total_elektro_fix - total_thg_erloes:>15,.2f} €/Jahr")
    else:
        print("Keine Elektro-LKW in der Lösung.")
    
    # --- A3: LADEINFRASTRUKTUR KOSTEN ---
    print("\n" + "-" * 100)
    print("A3: LADEINFRASTRUKTUR KOSTEN")
    print("-" * 100)
    
    total_lade_kosten = 0
    
    print(f"\n{'Ladesäulentyp':<20} {'Anzahl':<10} {'CAPEX/Stk':<12} {'OPEX/Stk':<12} {'Gesamt':<15}")
    print("=" * 80)
    
    for l in model.L:
        n = int(round(pyo.value(model.y_l[l])))
        if n > 0:
            cap_l = model.cap_l[l]
            opx_l = model.opx_l[l]
            gesamt = n * (cap_l + opx_l)
            total_lade_kosten += gesamt
            print(f"{l:<20} {n:<10} {cap_l:>10,.0f} € {opx_l:>10,.0f} € {gesamt:>13,.0f} €")
    
    if total_lade_kosten == 0:
        print("Keine Ladesäulen installiert.")
    else:
        print("-" * 80)
        print(f"{'SUMME LADEINFRASTRUKTUR:':<54} {total_lade_kosten:>13,.0f} €/Jahr")
    
    # --- A4: NETZ- UND STROMKOSTEN ---
    print("\n" + "-" * 100)
    print("A4: NETZ- UND STROMKOSTEN")
    print("-" * 100)
    
    # Grundgebühr
    grundgebuehr = pyo.value(model.c_gr)
    
    # Leistungspreis
    peak = pyo.value(model.p_peak)
    leistungskosten = pyo.value(model.cPeak) * peak
    
    # Arbeitspreis (Energiekosten)
    energie_bezug_tag = sum(pyo.value(model.p_grid[z]) * model.delta_t for z in model.Z)
    energie_bezug_jahr = 260 * energie_bezug_tag
    arbeitskosten = energie_bezug_jahr * pyo.value(model.c_e)
    
    # Trafo-Erweiterung
    trafo = pyo.value(model.u) > 0.5
    trafo_kosten = 10000 if trafo else 0
    
    total_strom = grundgebuehr + leistungskosten + arbeitskosten + trafo_kosten
    
    print(f"\n{'Komponente':<40} {'Wert':<20} {'Kosten':<15}")
    print("=" * 80)
    print(f"{'Grundgebühr':<40} {'-':<20} {grundgebuehr:>13,.2f} €")
    print(f"{'Leistungspreis':<40} {peak:>10,.2f} kW × 150 €/kW {leistungskosten:>13,.2f} €")
    print(f"{'Arbeitspreis':<40} {energie_bezug_jahr:>10,.1f} kWh × 0.25 € {arbeitskosten:>13,.2f} €")
    print(f"{'Trafo-Erweiterung':<40} {'JA' if trafo else 'NEIN':<20} {trafo_kosten:>13,.2f} €")
    print("-" * 80)
    print(f"{'SUMME STROMKOSTEN:':<60} {total_strom:>13,.2f} €/Jahr")
    
    print(f"\n  Energiebezug pro Tag:  {energie_bezug_tag:>10,.2f} kWh")
    print(f"  Energiebezug pro Jahr: {energie_bezug_jahr:>10,.2f} kWh")
    print(f"  Spitzenlast:           {peak:>10,.2f} kW")
    
    # --- A5: SPEICHERKOSTEN ---
    print("\n" + "-" * 100)
    print("A5: SPEICHERKOSTEN")
    print("-" * 100)
    
    storage_p = pyo.value(model.p_s)
    storage_q = pyo.value(model.q_s)
    
    if storage_p > 0.01 or storage_q > 0.01:
        capex_p = model.capP_s * storage_p
        capex_q = model.capQ_s * storage_q
        opex_s = model.opx_s * (capex_p + capex_q)
        total_speicher = capex_p + capex_q + opex_s
        
        print(f"\n{'Komponente':<40} {'Wert':<20} {'Kosten':<15}")
        print("=" * 80)
        print(f"{'Leistung (CAPEX)':<40} {storage_p:>10,.1f} kW × 30 €/kW {capex_p:>13,.2f} €")
        print(f"{'Kapazität (CAPEX)':<40} {storage_q:>10,.1f} kWh × 350 €/kWh {capex_q:>13,.2f} €")
        print(f"{'OPEX (2%)':<40} {'-':<20} {opex_s:>13,.2f} €")
        print("-" * 80)
        print(f"{'SUMME SPEICHER:':<60} {total_speicher:>13,.2f} €/Jahr")
    else:
        total_speicher = 0
        print("\nKein Speicher installiert.")
        print(f"{'SUMME SPEICHER:':<60} {total_speicher:>13,.2f} €/Jahr")
    
    # --- A6: GESAMTKOSTENÜBERSICHT ---
    print("\n" + "=" * 100)
    print("A6: GESAMTKOSTENÜBERSICHT")
    print("=" * 100)
    
    print(f"\n{'KOSTENPOSITION':<50} {'BETRAG':<20}")
    print("=" * 70)
    print(f"{'Diesel-LKW Fixkosten':<50} {total_diesel_fix:>18,.2f} €")
    print(f"{'Diesel-LKW Variable Kosten':<50} {total_diesel_var:>18,.2f} €")
    print(f"{'Elektro-LKW Fixkosten':<50} {total_elektro_fix:>18,.2f} €")
    print(f"{'THG-Quotenerlöse':<50} {-total_thg_erloes:>18,.2f} €")
    print(f"{'Ladeinfrastruktur':<50} {total_lade_kosten:>18,.2f} €")
    print(f"{'Stromkosten (Grund+Arbeit+Leistung)':<50} {total_strom - trafo_kosten:>18,.2f} €")
    print(f"{'Trafo-Erweiterung':<50} {trafo_kosten:>18,.2f} €")
    print(f"{'Speicher':<50} {total_speicher:>18,.2f} €")
    print("-" * 70)
    
    berechnete_summe = (total_diesel_fix + total_diesel_var + total_elektro_fix 
                        - total_thg_erloes + total_lade_kosten + total_strom + total_speicher)
    
    print(f"{'BERECHNETE GESAMTKOSTEN':<50} {berechnete_summe:>18,.2f} €")
    print(f"{'ZIELFUNKTIONSWERT (SOLVER)':<50} {pyo.value(model.obj):>18,.2f} €")
    print(f"{'DIFFERENZ':<50} {berechnete_summe - pyo.value(model.obj):>18,.2f} €")
    
    # Prozentuale Aufteilung
    print("\n" + "-" * 70)
    print("PROZENTUALE KOSTENAUFTEILUNG:")
    print("-" * 70)
    
    gesamt = pyo.value(model.obj)
    
    print(f"  Diesel-LKW (Fix + Var):    {100*(total_diesel_fix + total_diesel_var)/gesamt:>6.1f} %")
    print(f"  Elektro-LKW (Fix - THG):   {100*(total_elektro_fix - total_thg_erloes)/gesamt:>6.1f} %")
    print(f"  Ladeinfrastruktur:         {100*total_lade_kosten/gesamt:>6.1f} %")
    print(f"  Stromkosten:               {100*total_strom/gesamt:>6.1f} %")
    print(f"  Speicher:                  {100*total_speicher/gesamt:>6.1f} %")
    
    # ========================================================================
    # TEIL B: DETAILLIERTE LADEPLANUNG
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("TEIL B: DETAILLIERTE LADEPLANUNG PRO ELEKTRO-LKW")
    print("=" * 100)
    
    def zeit_format(z):
        """Konvertiert Zeitintervall z (1-96) in Uhrzeit HH:MM"""
        minuten = (z - 1) * 15
        stunden = minuten // 60
        mins = minuten % 60
        return f"{stunden:02d}:{mins:02d}"
    
    for e_data in elektro_lkw_liste:
        k = e_data['k']
        t = e_data['t']
        
        print("\n" + "=" * 100)
        print(f"ELEKTRO-LKW {k} | Typ: {t} | Batterie: {e_data['batterie']} kWh")
        print("=" * 100)
        
        # Touren dieses LKW
        print(f"\n--- TOUREN ---")
        touren_details = []
        for r in model.R:
            if pyo.value(model.a[r, k]) > 0.5:
                start_z = model.s_r[r]
                end_z = model.e_r[r]
                dist = model.dist[r]
                verbrauch = dist * model.avgEv_e[t]
                touren_details.append({
                    'r': r, 'start_z': start_z, 'end_z': end_z,
                    'start_zeit': zeit_format(start_z), 'end_zeit': zeit_format(end_z),
                    'dist': dist, 'verbrauch': verbrauch
                })
        
        touren_details.sort(key=lambda x: x['start_z'])
        
        print(f"{'Tour':<10} {'Abfahrt':<10} {'Ankunft':<10} {'Distanz':<12} {'Verbrauch':<15}")
        print("-" * 60)
        total_verbrauch = 0
        for td in touren_details:
            print(f"{td['r']:<10} {td['start_zeit']:<10} {td['end_zeit']:<10} {td['dist']:>8} km   {td['verbrauch']:>10.1f} kWh")
            total_verbrauch += td['verbrauch']
        print("-" * 60)
        print(f"{'GESAMT':<10} {'':<10} {'':<10} {e_data['km']:>8} km   {total_verbrauch:>10.1f} kWh")
        
        # SOC-Verlauf
        print(f"\n--- SOC-VERLAUF (LADEZUSTAND) ---")
        
        # Sammle relevante SOC-Werte (Änderungen)
        soc_events = []
        prev_soc = None
        
        for z in model.Z:
            current_soc = pyo.value(model.soc[k, z])
            
            # Prüfe ob Tour startet oder endet
            tour_start = None
            tour_end = None
            for r in model.R:
                if pyo.value(model.a[r, k]) > 0.5:
                    if model.s_r[r] == z:
                        tour_start = r
                    if model.e_r[r] == z:
                        tour_end = r
            
            # Prüfe ob geladen wird
            lade_leistung = sum(pyo.value(model.real_p[k, l, z]) for l in model.L)
            
            # Event aufzeichnen wenn etwas passiert
            if tour_start or tour_end or lade_leistung > 0.1 or prev_soc is None or abs(current_soc - prev_soc) > 0.5:
                event = {
                    'z': z, 'zeit': zeit_format(z), 'soc': current_soc,
                    'tour_start': tour_start, 'tour_end': tour_end,
                    'lade_leistung': lade_leistung
                }
                soc_events.append(event)
            
            prev_soc = current_soc
        
        # Ausgabe SOC-Verlauf (nur wichtige Events)
        print(f"{'Zeit':<8} {'SOC (kWh)':<12} {'SOC %':<10} {'Ereignis':<40}")
        print("-" * 80)
        
        batterie_kap = e_data['batterie']
        
        for ev in soc_events:
            soc_pct = 100 * ev['soc'] / batterie_kap if batterie_kap > 0 else 0
            
            ereignis = ""
            if ev['tour_start']:
                ereignis = f"🚚 ABFAHRT Tour {ev['tour_start']}"
            elif ev['tour_end']:
                ereignis = f"🏁 ANKUNFT von Tour {ev['tour_end']}"
            elif ev['lade_leistung'] > 0.1:
                ereignis = f"⚡ Laden mit {ev['lade_leistung']:.1f} kW"
            
            if ereignis or ev == soc_events[0] or ev == soc_events[-1]:
                print(f"{ev['zeit']:<8} {ev['soc']:>10.1f}    {soc_pct:>6.1f} %   {ereignis}")
        
        # Ladevorgänge detailliert
        print(f"\n--- LADEVORGÄNGE DETAILLIERT ---")
        
        lade_sessions = []
        aktuelle_session = None
        
        for z in model.Z:
            lade_leistung = sum(pyo.value(model.real_p[k, l, z]) for l in model.L)
            ladesaeule = None
            for l in model.L:
                if pyo.value(model.real_p[k, l, z]) > 0.1:
                    ladesaeule = l
                    break
            
            if lade_leistung > 0.1:
                if aktuelle_session is None:
                    aktuelle_session = {
                        'start_z': z, 'end_z': z,
                        'ladesaeule': ladesaeule,
                        'leistungen': [lade_leistung],
                        'energie': lade_leistung * 0.25,
                        'soc_start': pyo.value(model.soc[k, z])
                    }
                else:
                    aktuelle_session['end_z'] = z
                    aktuelle_session['leistungen'].append(lade_leistung)
                    aktuelle_session['energie'] += lade_leistung * 0.25
            else:
                if aktuelle_session is not None:
                    aktuelle_session['soc_end'] = pyo.value(model.soc[k, aktuelle_session['end_z']])
                    lade_sessions.append(aktuelle_session)
                    aktuelle_session = None
        
        # Letzte Session abschließen
        if aktuelle_session is not None:
            aktuelle_session['soc_end'] = pyo.value(model.soc[k, aktuelle_session['end_z']])
            lade_sessions.append(aktuelle_session)
        
        if lade_sessions:
            print(f"{'#':<4} {'Start':<8} {'Ende':<8} {'Dauer':<10} {'Säule':<18} {'Ø kW':<10} {'kWh':<10} {'SOC vorher':<12} {'SOC nachher':<12}")
            print("-" * 110)
            
            total_energie_geladen = 0
            for i, session in enumerate(lade_sessions, 1):
                dauer_intervalle = session['end_z'] - session['start_z'] + 1
                dauer_minuten = dauer_intervalle * 15
                dauer_str = f"{dauer_minuten} min"
                avg_leistung = sum(session['leistungen']) / len(session['leistungen'])
                
                soc_vorher_pct = 100 * session['soc_start'] / batterie_kap
                soc_nachher_pct = 100 * session['soc_end'] / batterie_kap
                
                print(f"{i:<4} {zeit_format(session['start_z']):<8} {zeit_format(session['end_z']):<8} "
                      f"{dauer_str:<10} {session['ladesaeule'] or 'N/A':<18} "
                      f"{avg_leistung:>8.1f}  {session['energie']:>8.1f}  "
                      f"{soc_vorher_pct:>8.1f} %   {soc_nachher_pct:>8.1f} %")
                
                total_energie_geladen += session['energie']
            
            print("-" * 110)
            print(f"GESAMT GELADEN: {total_energie_geladen:.1f} kWh | VERBRAUCHT: {total_verbrauch:.1f} kWh | DIFFERENZ: {total_energie_geladen - total_verbrauch:.1f} kWh")
        else:
            print("Keine Ladevorgänge für diesen LKW.")
        
        # Zusammenfassung für diesen LKW
        print(f"\n--- ZUSAMMENFASSUNG LKW {k} ---")
        
        soc_start = pyo.value(model.soc[k, 1])
        soc_min = min(pyo.value(model.soc[k, z]) for z in model.Z)
        soc_max = max(pyo.value(model.soc[k, z]) for z in model.Z)
        
        print(f"  SOC zu Tagesbeginn:    {soc_start:>8.1f} kWh ({100*soc_start/batterie_kap:>5.1f} %)")
        print(f"  SOC Minimum (Tag):     {soc_min:>8.1f} kWh ({100*soc_min/batterie_kap:>5.1f} %)")
        print(f"  SOC Maximum (Tag):     {soc_max:>8.1f} kWh ({100*soc_max/batterie_kap:>5.1f} %)")
        print(f"  Tagesverbrauch:        {total_verbrauch:>8.1f} kWh")
        print(f"  Reichweite Batterie:   {batterie_kap / model.avgEv_e[t]:>8.0f} km")
        print(f"  Gefahrene km:          {e_data['km']:>8} km")
        print(f"  Reichweiten-Reserve:   {100 - 100*e_data['km']/(batterie_kap / model.avgEv_e[t]):>8.1f} %")
    
    # ========================================================================
    # TEIL C: GLOBALE LADEÜBERSICHT
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("TEIL C: GLOBALE LADEÜBERSICHT (ALLE E-LKW)")
    print("=" * 100)
    
    # Stündliche Zusammenfassung
    print(f"\n--- STÜNDLICHE NETZLAST UND LADUNG ---")
    print(f"{'Stunde':<10} {'Netzlast (kW)':<15} {'Ladende LKW':<15} {'Aktive Säulen':<15}")
    print("-" * 60)
    
    for h in range(24):
        z_start = h * 4 + 1
        z_end = z_start + 3
        
        # Durchschnittliche Netzlast in dieser Stunde
        netzlast_avg = sum(pyo.value(model.p_grid[z]) for z in range(z_start, min(z_end+1, 97))) / 4
        
        # Ladende LKW zählen
        ladende_lkw = set()
        aktive_saeulen = set()
        
        for z in range(z_start, min(z_end+1, 97)):
            for k in model.K:
                for l in model.L:
                    if pyo.value(model.real_p[k, l, z]) > 0.1:
                        ladende_lkw.add(k)
                        aktive_saeulen.add(l)
        
        if netzlast_avg > 0.1 or ladende_lkw:
            print(f"{h:02d}:00     {netzlast_avg:>12.1f}     {len(ladende_lkw):>10}        {len(aktive_saeulen):>10}")
    
    # Spitzenlast-Analyse
    print(f"\n--- SPITZENLAST-ANALYSE ---")
    
    peak_z = None
    peak_val = 0
    for z in model.Z:
        val = pyo.value(model.p_grid[z])
        if val > peak_val:
            peak_val = val
            peak_z = z
    
    if peak_z:
        print(f"\nSpitzenlast tritt auf um: {zeit_format(peak_z)} mit {peak_val:.2f} kW")
        print(f"\nZu diesem Zeitpunkt laden:")
        
        for k in model.K:
            for l in model.L:
                p = pyo.value(model.real_p[k, l, peak_z])
                if p > 0.1:
                    print(f"  - LKW {k} an {l}: {p:.1f} kW")
    
    # ========================================================================
    # TEIL D: DIESEL-LKW BETRIEBSDETAILS
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("TEIL D: DIESEL-LKW BETRIEBSDETAILS")
    print("=" * 100)
    
    for d_data in diesel_lkw_liste:
        k = d_data['k']
        print(f"\n--- DIESEL-LKW {k} | Typ: {d_data['t']} ---")
        
        print(f"{'Tour':<10} {'Abfahrt':<10} {'Ankunft':<10} {'Distanz':<12} {'Maut-km':<12} {'Diesel (l)':<12}")
        print("-" * 70)
        
        total_diesel_l = 0
        for r in model.R:
            if pyo.value(model.a[r, k]) > 0.5:
                start_zeit = zeit_format(model.s_r[r])
                end_zeit = zeit_format(model.e_r[r])
                dist = model.dist[r]
                maut_dist = model.mDist[r]
                diesel_l = dist * model.avgDv_d[d_data['t']]
                total_diesel_l += diesel_l
                
                print(f"{r:<10} {start_zeit:<10} {end_zeit:<10} {dist:>8} km   {maut_dist:>8} km   {diesel_l:>10.1f}")
        
        print("-" * 70)
        print(f"{'GESAMT':<10} {'':<10} {'':<10} {d_data['km']:>8} km   {d_data['maut_km']:>8} km   {total_diesel_l:>10.1f}")
        print(f"\nJährlicher Dieselverbrauch: {260 * total_diesel_l:,.0f} Liter")
        print(f"Jährliche Dieselkosten:     {260 * total_diesel_l * model.c_diesel:,.2f} €")
        print(f"Jährliche Mautkosten:       {260 * d_data['maut_km'] * model.c_m_d:,.2f} €")
    
    # ========================================================================
    # TEIL E: VERGLEICHSANALYSE E-LKW vs DIESEL
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("TEIL E: VERGLEICHSANALYSE ELEKTRO vs. DIESEL")
    print("=" * 100)
    
    # Kosten pro km Vergleich
    print(f"\n--- KOSTEN PRO KILOMETER ---")
    print(f"{'LKW':<8} {'Typ':<15} {'km/Jahr':<12} {'Fixkosten':<15} {'Var.kosten':<15} {'Gesamt':<15} {'€/km':<10}")
    print("=" * 100)
    
    alle_lkw_analyse = []
    
    for d_data in diesel_lkw_liste:
        km_jahr = 260 * d_data['km']
        fix = d_data['fix']
        var = d_data['var']
        gesamt = fix + var
        pro_km = gesamt / km_jahr if km_jahr > 0 else 0
        
        alle_lkw_analyse.append({
            'k': d_data['k'], 'typ': d_data['t'], 'kategorie': 'Diesel',
            'km_jahr': km_jahr, 'fix': fix, 'var': var, 'gesamt': gesamt, 'pro_km': pro_km
        })
        
        print(f"LKW {d_data['k']:<4} {d_data['t']:<15} {km_jahr:>10,}   {fix:>13,.0f} € {var:>13,.0f} € {gesamt:>13,.0f} € {pro_km:>8.2f}")
    
    for e_data in elektro_lkw_liste:
        km_jahr = 260 * e_data['km']
        fix = e_data['fix'] - e_data['thg']  # Netto (minus THG)
        
        # Variable Kosten = anteiliger Strom (approximiert)
        energie_anteil = e_data['energie_jahr']
        var = energie_anteil * pyo.value(model.c_e)  # Nur Arbeitspreis
        
        gesamt = fix + var
        pro_km = gesamt / km_jahr if km_jahr > 0 else 0
        
        alle_lkw_analyse.append({
            'k': e_data['k'], 'typ': e_data['t'], 'kategorie': 'Elektro',
            'km_jahr': km_jahr, 'fix': fix, 'var': var, 'gesamt': gesamt, 'pro_km': pro_km
        })
        
        print(f"LKW {e_data['k']:<4} {e_data['t']:<15} {km_jahr:>10,}   {fix:>13,.0f} € {var:>13,.0f} € {gesamt:>13,.0f} € {pro_km:>8.2f}")
    
    # Durchschnitte
    print("\n" + "-" * 100)
    
    diesel_lkws = [a for a in alle_lkw_analyse if a['kategorie'] == 'Diesel']
    elektro_lkws = [a for a in alle_lkw_analyse if a['kategorie'] == 'Elektro']
    
    if diesel_lkws:
        avg_diesel = sum(a['pro_km'] for a in diesel_lkws) / len(diesel_lkws)
        print(f"Ø Diesel-LKW:        {avg_diesel:.2f} €/km")
    
    if elektro_lkws:
        avg_elektro = sum(a['pro_km'] for a in elektro_lkws) / len(elektro_lkws)
        print(f"Ø Elektro-LKW:       {avg_elektro:.2f} €/km (ohne anteilige Infrastruktur)")
    
    print("\n" + "=" * 100)
    print("ANALYSE ABGESCHLOSSEN")
    print("=" * 100)
    # ZIELFUNKTIONSWERT
    print("-" * 80)
    print("📊 ZIELFUNKTIONSWERT")
    print("-" * 80)
    print(f"Gesamtkosten (jährlich): {pyo.value(model.obj):,.2f} €")
    
    # DIAGNOSE: Alle Touren prüfen
    print("\n" + "-" * 80)
    print("🔍 TOUR-ZUORDNUNG PRÜFUNG")
    print("-" * 80)
    
    alle_touren = list(model.R)
    zugeordnete_touren = []
    
    for r in model.R:
        zugeordnet = False
        for k in model.K:
            if pyo.value(model.a[r, k]) > 0.5:
                zugeordnete_touren.append(r)
                zugeordnet = True
                break
        if not zugeordnet:
            print(f"⚠️ Tour {r}: NICHT ZUGEORDNET!")
    
    print(f"\nGesamt Touren: {len(alle_touren)}")
    print(f"Zugeordnet: {len(zugeordnete_touren)}")
    print(f"Fehlend: {len(alle_touren) - len(zugeordnete_touren)}")
    
    # LKW-TYPEN UND TOUR-ZUORDNUNG
    print("\n" + "-" * 80)
    print("🚛 LKW-TYPEN UND TOUR-ZUORDNUNG")
    print("-" * 80)
    
    for k in sorted(model.K):
        # Finde Typ
        truck_type = None
        for t in model.T:
            if pyo.value(model.type_assignment[k, t]) > 0.5:
                truck_type = t
                break
        
        # Finde ALLE Touren
        tours = [r for r in model.R if pyo.value(model.a[r, k]) > 0.5]
        
        if tours:
            typ_kat = "E" if truck_type in model.TE else "D"
            total_km = sum(model.dist[r] for r in tours)
            sorted_tours = sorted(tours, key=lambda x: model.s_r[x])
            
            print(f"\nLKW {k} | Typ: {truck_type} [{typ_kat}] | {len(tours)} Tour(en) | {total_km} km")
            for r in sorted_tours:
                start_h = (model.s_r[r]-1)*0.25
                end_h = (model.e_r[r]-1)*0.25
                print(f"    → {r}: {start_h:.2f}h - {end_h:.2f}h, {model.dist[r]} km")
    
    # LADEINFRASTRUKTUR
    print("\n" + "-" * 80)
    print("⚡ LADEINFRASTRUKTUR")
    print("-" * 80)
    
    total_chargers = 0
    total_ladepunkte = 0
    max_ladeleistung = 0
    
    for l in model.L:
        n = int(round(pyo.value(model.y_l[l])))
        if n > 0:
            total_chargers += n
            punkte = n * model.cs_l[l]
            leistung = n * model.max_p_l[l]
            total_ladepunkte += punkte
            max_ladeleistung += leistung
            print(f"{l}: {n} Säule(n), {punkte} Ladepunkte, max {leistung} kW")
    
    if total_chargers == 0:
        print("Keine Ladesäulen (reine Diesel-Flotte)")
    else:
        print(f"\n{'─'*40}")
        print(f"GESAMT LADESÄULEN:    {total_chargers}")
        print(f"GESAMT LADEPUNKTE:    {total_ladepunkte}")
        print(f"MAX. LADELEISTUNG:    {max_ladeleistung} kW")
    
    # NETZ & ERWEITERUNGEN
    print("\n" + "-" * 80)
    print("🔌 NETZ & ERWEITERUNGEN")
    print("-" * 80)
    
    trafo = pyo.value(model.u) > 0.5
    peak = pyo.value(model.p_peak)
    storage_p = pyo.value(model.p_s)
    storage_q = pyo.value(model.q_s)
    
    basis_netz = model.p_grid_max
    erweiterung = 500 if trafo else 0
    max_netz = basis_netz + erweiterung
    
    print(f"\nNetzanschluss:")
    print(f"  Basis-Kapazität:           {basis_netz} kW")
    print(f"  Trafo-Erweiterung:         {'+500 kW' if trafo else 'NEIN'}")
    print(f"  ─────────────────────────────────")
    print(f"  MAX. NETZKAPAZITÄT:        {max_netz} kW")
    print(f"  Tatsächliche Spitzenlast:  {peak:.2f} kW")
    print(f"  Auslastung:                {100*peak/max_netz:.1f}%")
    
    # ZUSATZOPTIONEN ZUSAMMENFASSUNG
    print("\n" + "-" * 80)
    print("📋 ZUSAMMENFASSUNG ZUSATZOPTIONEN")
    print("-" * 80)
    
    print(f"\n{'Option':<35} {'Status':<10} {'Details'}")
    print("=" * 70)
    print(f"{'Trafo-Erweiterung (+500 kW)':<35} {'✅ JA' if trafo else '❌ NEIN':<10} {'Kosten: 10.000 €/Jahr' if trafo else ''}")
    
    if storage_p > 0.01 or storage_q > 0.01:
        storage_cost = (1 + model.opx_s) * (model.capP_s * storage_p + model.capQ_s * storage_q)
        print(f"{'Stationärer Speicher':<35} {'✅ JA':<10} {storage_p:.1f} kW / {storage_q:.1f} kWh")
        print(f"{'':<35} {'':<10} Kosten: {storage_cost:,.0f} €/Jahr")
    else:
        print(f"{'Stationärer Speicher':<35} {'❌ NEIN':<10}")
    
    # Ladesäulen als "Option"
    if total_chargers > 0:
        charger_cost = sum(pyo.value(model.y_l[l]) * (model.cap_l[l] + model.opx_l[l]) for l in model.L)
        print(f"{'Ladeinfrastruktur':<35} {'✅ JA':<10} {total_chargers} Säulen, {total_ladepunkte} Punkte")
        print(f"{'':<35} {'':<10} Kosten: {charger_cost:,.0f} €/Jahr")
    else:
        print(f"{'Ladeinfrastruktur':<35} {'❌ NEIN':<10}")
    
    # FLOTTEN-ZUSAMMENFASSUNG
    print("\n" + "-" * 80)
    print("🚗 FLOTTEN-ZUSAMMENFASSUNG")
    print("-" * 80)
    
    n_elektro = 0
    n_diesel = 0
    aktive_lkw = 0
    
    for k in model.K:
        hat_tour = any(pyo.value(model.a[r, k]) > 0.5 for r in model.R)
        if hat_tour:
            aktive_lkw += 1
            for t in model.TE:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    n_elektro += 1
                    break
            for t in model.TD:
                if pyo.value(model.type_assignment[k, t]) > 0.5:
                    n_diesel += 1
                    break
    
    print(f"\nAktive LKWs:     {aktive_lkw}")
    print(f"  davon Elektro: {n_elektro}")
    print(f"  davon Diesel:  {n_diesel}")
    print(f"Elektro-Anteil:  {100*n_elektro/aktive_lkw:.1f}%" if aktive_lkw > 0 else "")
    # MIP-Gap anzeigen (falls verfügbar)
    try:
        if hasattr(results.problem, 'lower_bound') and hasattr(results.problem, 'upper_bound'):
            lower_bound = results.problem.lower_bound
            upper_bound = results.problem.upper_bound
            if lower_bound is not None and upper_bound is not None and upper_bound > 0:
                gap = 100 * (upper_bound - lower_bound) / upper_bound
                print(f"Untere Schranke: {lower_bound:,.2f} €")
                print(f"MIP-Gap: {gap:.2f}%")
        elif hasattr(results.solver, 'gap'):
            print(f"MIP-Gap: {results.solver.gap:.2f}%")
    except:
        pass
else:
    print("\n❌ KEINE ZULÄSSIGE LÖSUNG GEFUNDEN")
    print(f"Solver-Status: {results.solver.status}")
    print(f"Termination Condition: {results.solver.termination_condition}")

print("\n" + "=" * 80)
print("FERTIG")
print("=" * 80)