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
model.K = pyo.Set(initialize=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
 
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
model.c_diesel = pyo.Param(initialize=1.68)
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
model.M = pyo.Param(initialize=10000)
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
 
# --- Hilfsvariable für Linearisierung: a_type[r,k,t] = a[r,k] * type_assignment[k,t] ---
model.a_type = pyo.Var(model.R, model.K, model.T, domain=pyo.Binary)
 
# --- Zuordnung & Bewegung ---
model.a = pyo.Var(model.R, model.K, domain=pyo.Binary)
model.depart = pyo.Var(model.K, model.Z, domain=pyo.Binary)
model.arrive = pyo.Var(model.K, model.Z, domain=pyo.Binary)
 
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
 
def arrive_definition_rule(model, k, z):
    return model.arrive[k, z] == sum(model.end_at[r, z] * model.a[r, k] for r in model.R)
model.con_arrive_definition = pyo.Constraint(model.K, model.Z, rule=arrive_definition_rule)
 
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
 
# --- 5.5 LADE-LOGIK ---
 
def charging_power_limit_rule(model, k, l, z):
    return model.real_p[k, l, z] <= sum(model.type_assignment[k, t] * model.max_p_e[t] for t in model.T)
model.con_charging_power_limit = pyo.Constraint(model.K, model.L, model.Z, rule=charging_power_limit_rule)
 
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
    # C_trucks: LKW-Fixkosten (linear)
    C_trucks = sum(
        sum(model.type_assignment[k, t] * (model.cap_d[t] + model.opx_d[t] + model.kfz_d[t]) for t in model.TD) +
        sum(model.type_assignment[k, t] * (model.cap_e[t] + model.opx_e[t]) for t in model.TE)
        for k in model.K
    )
   
    # C_chargers
    C_chargers = sum(model.y_l[l] * (model.cap_l[l] + model.opx_l[l]) for l in model.L)
   
    # C_grid_trafo
    C_grid_trafo = 10000 * model.u
   
    # C_storage
    C_storage = (1 + model.opx_s) * (model.capP_s * model.p_s + model.capQ_s * model.q_s)
   
    # C_diesel_var: LINEARISIERT mit a_type (nur für TD)
    C_diesel_var = 260 * sum(
        model.a_type[r, k, t] * (model.c_m_d * model.mDist[r] +
                                  model.c_diesel * (model.dist[r]/100) * model.avgDv_d[t])
        for r in model.R for k in model.K for t in model.TD
    )
   
    # C_electricity
    C_electricity = model.c_gr + model.cPeak * model.p_peak + \
                    260 * model.c_e * sum(model.p_grid[z] * model.delta_t for z in model.Z)
   
    # C_revenue
    C_revenue = sum(
        sum(model.type_assignment[k, t] * model.thg_e[t] for t in model.TE)
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
 
# Versuche zuerst CBC
try:
    solver = SolverFactory('cbc')
    if solver.available():
        solver_name = 'cbc'
        print(f"Verwende Solver: {solver_name}")
except:
    pass
 
# Falls CBC nicht verfügbar, GLPK
if solver is None or not solver.available():
    try:
        solver = SolverFactory('glpk')
        if solver.available():
            solver_name = 'glpk'
            print(f"Verwende Solver: {solver_name}")
    except:
        pass
 
# Solver-Optionen für frühe Feasible Solution und 2h Zeitlimit
if solver_name == 'cbc':
    solver.options['seconds'] = 7200          # 2 Stunden Zeitlimit
    solver.options['heuristics'] = 'on'       # Heuristiken aktivieren
    solver.options['round'] = 'on'            # Rounding Heuristik
    solver.options['feas'] = 'on'             # Feasibility Pump
    solver.options['passF'] = 100             # Feasibility Pump Passes
    solver.options['cuts'] = 'on'             # Schnittebenen aktivieren
    solver.options['preprocess'] = 'on'       # Preprocessing
    solver.options['printingOptions'] = 'all' # Vollständige Ausgabe
   
elif solver_name == 'glpk':
    solver.options['tmlim'] = 7200  # 2 Stunden Zeitlimit - das reicht!
 
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

else:
    print("\n❌ KEINE ZULÄSSIGE LÖSUNG GEFUNDEN")
    print(f"Solver-Status: {results.solver.status}")
    print(f"Termination Condition: {results.solver.termination_condition}")

print("\n" + "=" * 80)
print("FERTIG")
print("=" * 80)

    # 5) Beispiel: SOC von Truck 1 (nur wenige Zeitpunkte)
    k0 = 1
    print(f"\n--- SOC Truck {k0} (Auszug) ---")
    for z in [1, 25, 48, 72, 96]:
        print(f"z={z}: {pyo.value(model.soc[k0, z]):.2f}")

else:
    print("\n❌ KEINE ZULÄSSIGE LÖSUNG GEFUNDEN")
    print(f"Solver-Status: {results.solver.status}")
    print(f"Termination Condition: {results.solver.termination_condition}")
