# Vollständige Dokumentation: MILP-Modell zur LKW-Flottenoptimierung

## Inhaltsverzeichnis
1. [Das Problem in einfachen Worten](#1-das-problem-in-einfachen-worten)
2. [Mathematische Grundlagen](#2-mathematische-grundlagen)
3. [Indexmengen (Sets)](#3-indexmengen-sets)
4. [Parameter](#4-parameter)
5. [Entscheidungsvariablen](#5-entscheidungsvariablen)
6. [Linearisierung - Warum und Wie](#6-linearisierung---warum-und-wie)
7. [Nebenbedingungen (Constraints)](#7-nebenbedingungen-constraints)
8. [Zielfunktion](#8-zielfunktion)
9. [Speicher, DoD und Round-Trip-Efficiency](#9-speicher-dod-und-round-trip-efficiency)

---

# 1. Das Problem in einfachen Worten

## Die Ausgangssituation

Ein Logistikunternehmen betreibt ein Depot, von dem täglich **20 Touren** gefahren werden müssen. Aktuell werden **Diesel-LKWs** eingesetzt. Die Frage ist:

> **Lohnt es sich, auf Elektro-LKWs umzusteigen?**

## Die Entscheidungen, die getroffen werden müssen

1. **Welcher LKW fährt welche Tour?**
2. **Welcher LKW soll Diesel sein, welcher Elektro?**
3. **Wie viele Ladesäulen welchen Typs brauchen wir?**
4. **Wann und wie viel soll jeder E-LKW laden?**
5. **Brauchen wir einen Transformator für mehr Netzleistung?**
6. **Brauchen wir einen Batteriespeicher?**

## Das Ziel

**Minimiere die jährlichen Gesamtkosten** unter Einhaltung aller Randbedingungen.

## Warum MILP?

**MILP = Mixed Integer Linear Programming**

- **Mixed Integer**: Mischung aus ganzzahligen Variablen (z.B. "Wie viele Ladesäulen?") und kontinuierlichen Variablen (z.B. "Mit wie viel kW laden?")
- **Linear**: Alle Gleichungen und Ungleichungen sind linear (keine x², keine x·y)
- **Programming**: Mathematisches Optimierungsproblem

---

# 2. Mathematische Grundlagen

## 2.1 Das Summenzeichen Σ

```
Σ     = "Summiere"
i∈M

Bedeutet: Addiere den Ausdruck für alle i aus der Menge M
```

**Beispiel:**
```
Menge K = {1, 2, 3}

Σ x[k] = x[1] + x[2] + x[3]
k∈K
```

**Doppelte Summe:**
```
Σ   Σ   x[k,l] = x[1,A] + x[1,B] + x[2,A] + x[2,B]
k∈K l∈L

(für K={1,2} und L={A,B})
```

## 2.2 Der Allquantor ∀

```
∀ = "Für alle" / "Für jeden"

x[k] ≥ 0  ∀k ∈ K

Bedeutet: Diese Bedingung gilt für JEDEN LKW k
```

## 2.3 Das Element-Zeichen ∈

```
∈ = "ist Element von" / "gehört zu"

k ∈ K bedeutet: k ist einer der LKWs aus der Menge K
```

## 2.4 Mengenoperationen

```
∪ = Vereinigung (ODER)
    A ∪ B = Alle Elemente die in A ODER in B sind

\ = Differenz (OHNE)
    A \ B = Alle Elemente aus A, die NICHT in B sind
```

## 2.5 Variablentypen

| Notation | Bedeutung | Beispiel |
|----------|-----------|----------|
| `∈ {0,1}` | Binär (Ja/Nein) | Fährt LKW k Tour r? |
| `∈ ℤ≥0` | Ganzzahl ≥ 0 | Anzahl Ladesäulen |
| `≥ 0` | Kontinuierlich ≥ 0 | Ladeleistung in kW |

---

# 3. Indexmengen (Sets)

Indexmengen definieren die **Dimensionen** des Problems - worüber wird optimiert?

## 3.1 R - Menge der Touren

| Mathematik | Code |
|------------|------|
| R = {t-4, t-5, ..., k1} | `model.R = pyo.Set(initialize=['t-4', 't-5', ...])` |

**20 Touren** die täglich gefahren werden müssen.

```python
model.R = pyo.Set(initialize=[
    't-4', 't-5', 't-6', 's-1', 's-2', 's-3', 's-4',
    'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7',
    'r1', 'r2', 'r3', 'h3', 'h4', 'k1'
])
```

**Verwendung:** Jedes Mal wenn `∀r ∈ R` steht, wird über alle 20 Touren iteriert.

---

## 3.2 K - Menge der LKWs

| Mathematik | Code |
|------------|------|
| K = {1, 2, ..., 14} | `model.K = pyo.Set(initialize=range(1,15))` |

**14 LKWs** stehen zur Verfügung.

```python
model.K = pyo.Set(initialize=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
```

**Wichtig:** Das Modell entscheidet, welcher LKW welchen TYP bekommt und ob er überhaupt benutzt wird.

---

## 3.3 TD - Diesel-LKW-Typen

| Mathematik | Code |
|------------|------|
| TD = {ActrosL} | `model.TD = pyo.Set(initialize=['ActrosL'])` |

Nur **ein Diesel-Typ** verfügbar: Mercedes Actros L

```python
model.TD = pyo.Set(initialize=['ActrosL'])
```

---

## 3.4 TE - Elektro-LKW-Typen

| Mathematik | Code |
|------------|------|
| TE = {eActros600, eActros400} | `model.TE = pyo.Set(initialize=['eActros600', 'eActros400'])` |

**Zwei E-LKW-Typen:**
- eActros600: Große Batterie (621 kWh)
- eActros400: Kleine Batterie (414 kWh)

```python
model.TE = pyo.Set(initialize=['eActros600', 'eActros400'])
```

---

## 3.5 T - Alle LKW-Typen

| Mathematik | Code |
|------------|------|
| T = TD ∪ TE | `model.T = model.TD \| model.TE` |

Vereinigung aller Typen.

```python
model.T = model.TD | model.TE  # = {'ActrosL', 'eActros600', 'eActros400'}
```

---

## 3.6 L - Ladesäulentypen

| Mathematik | Code |
|------------|------|
| L = {Alpitronic-50, -200, -400} | `model.L = pyo.Set(initialize=[...])` |

**Drei Säulentypen** mit unterschiedlicher Leistung:

```python
model.L = pyo.Set(initialize=['Alpitronic-50', 'Alpitronic-200', 'Alpitronic-400'])
```

| Typ | Leistung | Kosten/Jahr |
|-----|----------|-------------|
| Alpitronic-50 | 50 kW | 4.000€ |
| Alpitronic-200 | 200 kW | 11.500€ |
| Alpitronic-400 | 400 kW | 18.000€ |

---

## 3.7 Z - Zeitintervalle

| Mathematik | Code |
|------------|------|
| Z = {1, 2, ..., 96} | `model.Z = pyo.Set(initialize=range(1, 97))` |

Der Tag wird in **96 Intervalle à 15 Minuten** unterteilt.

```python
model.Z = pyo.Set(initialize=range(1, 97))  # 1 bis 96
```

**Umrechnung Intervall → Uhrzeit:**
```
Uhrzeit = (Intervall - 1) × 0.25 Stunden

Intervall 1  → 00:00 Uhr
Intervall 25 → 06:00 Uhr
Intervall 49 → 12:00 Uhr
Intervall 73 → 18:00 Uhr
Intervall 96 → 23:45 Uhr
```

---

## 3.8 Z_day und Z_night - Tag/Nacht

| Mathematik | Code |
|------------|------|
| Z_day = {25, ..., 72} | `model.Z_day = pyo.Set(initialize=range(25, 73))` |
| Z_night = Z \ Z_day | `model.Z_night = ...` |

```python
model.Z_day = pyo.Set(initialize=range(25, 73))    # 06:00 - 17:45
model.Z_night = pyo.Set(initialize=[z for z in range(1, 97) if z not in range(25, 73)])
```

**Wichtig für:** Nacht-Bewegungseinschränkung (LKWs dürfen nachts nicht umgeparkt werden)

---

# 4. Parameter

Parameter sind **feste Eingabewerte** - sie werden NICHT optimiert.

## 4.1 Tourenparameter

### dist[r] - Gesamtdistanz

| Mathematik | Code |
|------------|------|
| dist: R → ℝ₊ | `model.dist = pyo.Param(model.R, initialize=dist_data)` |

```python
dist_data = {
    't-4': 250, 't-5': 250, 't-6': 250,    # Lange Touren
    's-1': 120, 's-2': 120, ...             # Mittlere Touren
    'w1': 100, 'w2': 100, ...               # Kurze Touren
}
model.dist = pyo.Param(model.R, initialize=dist_data)
```

**Verwendung:** Berechnung Energieverbrauch, Dieselverbrauch, Mautkosten

---

### mDist[r] - Mautpflichtige Distanz

| Mathematik | Code |
|------------|------|
| mDist: R → ℝ₊ | `model.mDist = pyo.Param(model.R, initialize=mDist_data)` |

```python
mDist_data = {
    't-4': 150,  # Von 250 km sind 150 km Autobahn
    's-1': 32,   # Von 120 km sind 32 km Autobahn
    ...
}
```

**Verwendung:** Berechnung Mautkosten (nur für Diesel-LKWs)

---

### s_r[r] und e_r[r] - Start- und Endintervall

| Mathematik | Code |
|------------|------|
| s_r: R → Z | `model.s_r = pyo.Param(model.R, initialize=s_r_data)` |
| e_r: R → Z | `model.e_r = pyo.Param(model.R, initialize=e_r_data)` |

```python
s_r_data = {'t-4': 28, 't-5': 27, ...}  # Intervall 28 = 06:45 Uhr
e_r_data = {'t-4': 69, 't-5': 70, ...}  # Intervall 69 = 17:00 Uhr
```

**Umrechnung:** `Intervall = 4 × Stunde + 1`
- 06:45 Uhr = 6.75 Stunden → 4 × 6.75 + 1 = 28

---

### dur_z[r] - Tourdauer in Intervallen

| Mathematik | Code |
|------------|------|
| dur_z[r] = e_r[r] - s_r[r] | `model.dur_z = pyo.Param(model.R, initialize=dur_z_init)` |

```python
def dur_z_init(model, r):
    return model.e_r[r] - model.s_r[r]
model.dur_z = pyo.Param(model.R, initialize=dur_z_init)
```

**Beispiel:** Tour t-4: e_r=69, s_r=28 → dur_z = 41 Intervalle = 10.25 Stunden

---

### start_at[r,z], end_at[r,z], active_tour[r,z] - Zeitliche Marker

| Parameter | = 1 wenn... | Code |
|-----------|-------------|------|
| start_at[r,z] | Tour r startet in Intervall z | `1 if z == s_r[r] else 0` |
| end_at[r,z] | Tour r endet in Intervall z | `1 if z == e_r[r] else 0` |
| active_tour[r,z] | Tour r ist aktiv in z | `1 if s_r[r] <= z < e_r[r] else 0` |

```python
def active_tour_init(model, r, z):
    return 1 if model.s_r[r] <= z < model.e_r[r] else 0
model.active_tour = pyo.Param(model.R, model.Z, initialize=active_tour_init)
```

**Visualisierung für Tour t-4 (Intervall 28-69):**
```
Intervall:  ... 27  28  29  30  ... 68  69  70 ...
start_at:   ... 0   1   0   0   ... 0   0   0  ...
active:     ... 0   1   1   1   ... 1   0   0  ...
end_at:     ... 0   0   0   0   ... 0   1   0  ...
```

---

## 4.2 Diesel-LKW-Parameter

| Parameter | Wert | Bedeutung |
|-----------|------|-----------|
| cap_d['ActrosL'] | 24.000 €/Jahr | Leasingkosten |
| opx_d['ActrosL'] | 6.000 €/Jahr | Wartungskosten |
| kfz_d['ActrosL'] | 556 €/Jahr | KFZ-Steuer |
| avgDv_d['ActrosL'] | 0.26 L/km | Dieselverbrauch |
| c_diesel | 1.50 €/L | Dieselpreis |
| c_m_d | 0.34 €/km | Mautkosten |

```python
model.cap_d = pyo.Param(model.TD, initialize={'ActrosL': 24000})
model.opx_d = pyo.Param(model.TD, initialize={'ActrosL': 6000})
model.kfz_d = pyo.Param(model.TD, initialize={'ActrosL': 556})
model.avgDv_d = pyo.Param(model.TD, initialize={'ActrosL': 0.26})
model.c_diesel = pyo.Param(initialize=1.5)
model.c_m_d = pyo.Param(initialize=0.34)
```

---

## 4.3 Elektro-LKW-Parameter

| Parameter | eActros600 | eActros400 | Bedeutung |
|-----------|------------|------------|-----------|
| cap_e | 60.000 € | 50.000 € | Leasingkosten/Jahr |
| opx_e | 6.000 € | 5.000 € | Wartungskosten/Jahr |
| avgEv_e | 1.1 kWh/km | 1.05 kWh/km | Energieverbrauch |
| soc_e | 621 kWh | 414 kWh | Batteriekapazität |
| max_p_e | 400 kW | 400 kW | Max. Ladeleistung |
| thg_e | 1.000 € | 1.000 € | THG-Erlös/Jahr |

```python
model.cap_e = pyo.Param(model.TE, initialize={'eActros600': 60000, 'eActros400': 50000})
model.soc_e = pyo.Param(model.TE, initialize={'eActros600': 621, 'eActros400': 414})
# ... etc.
```

**Wichtiger Trick:** `max_p_e['ActrosL'] = 0` verhindert, dass Diesel-LKWs laden können!

```python
max_p_e_data = {'eActros600': 400, 'eActros400': 400, 'ActrosL': 0}
```

---

## 4.4 Ladesäulen-Parameter

| Parameter | Alpitronic-50 | Alpitronic-200 | Alpitronic-400 |
|-----------|---------------|----------------|----------------|
| cap_l | 3.000 € | 10.000 € | 16.000 € |
| opx_l | 1.000 € | 1.500 € | 2.000 € |
| max_p_l | 50 kW | 200 kW | 400 kW |
| cs_l | 2 | 2 | 2 |

```python
model.cap_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 3000, 'Alpitronic-200': 10000, 'Alpitronic-400': 16000
})
model.cs_l = pyo.Param(model.L, initialize={
    'Alpitronic-50': 2, 'Alpitronic-200': 2, 'Alpitronic-400': 2
})
```

**cs_l = Charging Spots** = Anzahl Ladepunkte pro Säule

---

## 4.5 Netz- und Speicherparameter

| Parameter | Wert | Bedeutung |
|-----------|------|-----------|
| p_grid_max | 500 kW | Max. Netzanschlussleistung |
| capP_s | 30 €/kW/Jahr | Speicher-Leistungskosten |
| capQ_s | 350 €/kWh/Jahr | Speicher-Kapazitätskosten |
| opx_s | 0.02 (2%) | Speicher-Wartungsfaktor |
| nrt | 0.98 (98%) | Round-Trip-Efficiency |
| dod | 0.025 (2.5%) | Depth of Discharge (Reserve) |
| c_e | 0.25 €/kWh | Arbeitspreis Strom |
| c_gr | 1.000 €/Jahr | Grundgebühr Strom |
| cPeak | 150 €/kW/Jahr | Leistungspreis |
| Nmax | 3 | Max. Anzahl Ladesäulen |
| delta_t | 0.25 h | Intervalldauer (15 min) |

```python
model.p_grid_max = pyo.Param(initialize=500)
model.nrt = pyo.Param(initialize=0.98)
model.dod = pyo.Param(initialize=0.025)
model.cPeak = pyo.Param(initialize=150)
# ... etc.
```

---

## 4.6 unplug_ok[z] - Darf abgesteckt werden?

| Mathematik | Code |
|------------|------|
| unplug_ok: Z → {0,1} | `model.unplug_ok = pyo.Param(model.Z, initialize=unplug_ok_init)` |

```python
def unplug_ok_init(model, z):
    if z in model.Z_day:       # Tagsüber (06:00-18:00)
        return 1               # Ja, darf abstecken
    elif z + 1 == model.z6:    # Kurz vor 06:00 (Intervall 24)
        return 1               # Ja, darf abstecken
    else:                      # Nachts
        return 0               # Nein, muss angesteckt bleiben
```

**Sinn:** Nachts ist kein Personal da zum Umparken der LKWs.

---

# 5. Entscheidungsvariablen

Variablen sind die **Werte, die der Solver optimiert** - die "Antworten" des Modells.

## 5.1 type_assignment[k,t] - LKW-Typ-Zuordnung

| Mathematik | Code |
|------------|------|
| type_assignment[k,t] ∈ {0,1} | `model.type_assignment = pyo.Var(model.K, model.T, domain=pyo.Binary)` |

**Bedeutung:**
- `type_assignment[k,t] = 1` → LKW k ist vom Typ t
- `type_assignment[k,t] = 0` → LKW k ist NICHT vom Typ t

**Beispiel:**
```
type_assignment[1, 'ActrosL'] = 0
type_assignment[1, 'eActros600'] = 1  ← LKW 1 ist ein eActros600
type_assignment[1, 'eActros400'] = 0
```

---

## 5.2 truck_used[k] - Wird LKW benutzt?

| Mathematik | Code |
|------------|------|
| truck_used[k] ∈ {0,1} | `model.truck_used = pyo.Var(model.K, domain=pyo.Binary)` |

**Bedeutung:**
- `truck_used[k] = 1` → LKW k fährt mindestens eine Tour
- `truck_used[k] = 0` → LKW k wird nicht benutzt

**Wichtig für:** Kostenberechnung - wir zahlen nur für benutzte LKWs!

---

## 5.3 a[r,k] - Tour-LKW-Zuordnung

| Mathematik | Code |
|------------|------|
| a[r,k] ∈ {0,1} | `model.a = pyo.Var(model.R, model.K, domain=pyo.Binary)` |

**Bedeutung:**
- `a[r,k] = 1` → Tour r wird von LKW k gefahren
- `a[r,k] = 0` → Tour r wird NICHT von LKW k gefahren

**Dimension:** 20 Touren × 14 LKWs = 280 Variablen

---

## 5.4 a_type[r,k,t] - Linearisierungshilfe

| Mathematik | Code |
|------------|------|
| a_type[r,k,t] ∈ {0,1} | `model.a_type = pyo.Var(model.R, model.K, model.T, domain=pyo.Binary)` |

**Bedeutung:** `a_type[r,k,t] = a[r,k] × type_assignment[k,t]`

= 1 genau dann, wenn Tour r von LKW k gefahren wird UND LKW k vom Typ t ist.

**Warum?** Siehe Abschnitt 6 (Linearisierung)

---

## 5.5 depart[k,z] - Abfahrt-Indikator

| Mathematik | Code |
|------------|------|
| depart[k,z] ∈ {0,1} | `model.depart = pyo.Var(model.K, model.Z, domain=pyo.Binary)` |

**Bedeutung:** `depart[k,z] = 1` wenn LKW k in Intervall z zu einer Tour aufbricht.

---

## 5.6 Lade-Variablen

| Variable | Typ | Bedeutung |
|----------|-----|-----------|
| assign[k,l,z] | Binär | LKW k lädt AKTIV an Säulentyp l in z |
| plug[k,l,z] | Binär | LKW k ist ANGESTECKT an Säulentyp l in z |
| real_p[k,l,z] | ≥ 0 | Tatsächliche Ladeleistung in kW |
| y_l[l] | ∈ ℤ≥0 | Anzahl installierter Säulen vom Typ l |

```python
model.assign = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.plug = pyo.Var(model.K, model.L, model.Z, domain=pyo.Binary)
model.real_p = pyo.Var(model.K, model.L, model.Z, domain=pyo.NonNegativeReals)
model.y_l = pyo.Var(model.L, domain=pyo.NonNegativeIntegers, bounds=(0, model.Nmax))
```

**Unterschied plug vs. assign:**
- `plug = 1`: Physisch angesteckt (belegt den Ladepunkt)
- `assign = 1`: Lädt aktiv (Strom fließt)

Ein LKW kann angesteckt sein ohne zu laden (z.B. Akku ist voll, aber Ladepunkt noch belegt).

---

## 5.7 Energiezustands-Variablen

| Variable | Typ | Bedeutung |
|----------|-----|-----------|
| soc[k,z] | ≥ 0 | Batterieladezustand von LKW k in z (kWh) |

```python
model.soc = pyo.Var(model.K, model.Z, domain=pyo.NonNegativeReals)
```

---

## 5.8 Speicher-Variablen

| Variable | Typ | Bedeutung |
|----------|-----|-----------|
| p_s | ≥ 0 | Speicherleistung (kW) |
| q_s | ≥ 0 | Speicherkapazität (kWh) |
| p_l_s[z] | ≥ 0 | Speicher-Ladeleistung in z (kW) |
| p_e_s[z] | ≥ 0 | Speicher-Entladeleistung in z (kW) |
| soc_s[z] | ≥ 0 | Speicher-Füllstand in z (kWh) |
| mode_s[z] | Binär | Speichermodus: 1=Laden, 0=Entladen |

```python
model.p_s = pyo.Var(domain=pyo.NonNegativeReals)      # Leistung
model.q_s = pyo.Var(domain=pyo.NonNegativeReals)      # Kapazität
model.p_l_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)  # Laden
model.p_e_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)  # Entladen
model.soc_s = pyo.Var(model.Z, domain=pyo.NonNegativeReals)  # Füllstand
model.mode_s = pyo.Var(model.Z, domain=pyo.Binary)    # Modus
```

---

## 5.9 Netz-Variablen

| Variable | Typ | Bedeutung |
|----------|-----|-----------|
| p_grid[z] | ≥ 0 | Netzbezugsleistung in z (kW) |
| p_peak | ≥ 0 | Maximale Netzbezugsleistung (kW) |
| u | Binär | Trafo-Upgrade (1=Ja, 0=Nein) |

```python
model.p_grid = pyo.Var(model.Z, domain=pyo.NonNegativeReals)
model.p_peak = pyo.Var(domain=pyo.NonNegativeReals)
model.u = pyo.Var(domain=pyo.Binary)
```

---

# 6. Linearisierung - Warum und Wie

## 6.1 Das Problem

In der Zielfunktion und einigen Constraints brauchen wir Ausdrücke wie:

```
Dieselkosten = Σ a[r,k] × type_assignment[k,'ActrosL'] × (Maut + Diesel)
                    ↑              ↑
               Variable       Variable
```

**Das ist ein PRODUKT zweier Variablen → NICHT LINEAR!**

MILP-Solver können nur lineare Ausdrücke verarbeiten:
- ✓ `3 × x + 2 × y` (linear)
- ✗ `x × y` (nicht linear!)

## 6.2 Die Lösung: Neue Hilfsvariable

Wir führen eine neue Variable ein, die das Produkt DARSTELLT:

```
a_type[r,k,t] := a[r,k] × type_assignment[k,t]
```

Diese neue Variable wird durch **drei Constraints** so eingeschränkt, dass sie sich wie das Produkt verhält:

## 6.3 Die drei Linearisierungs-Constraints

### Constraint 1: a_type ≤ a

| Mathematik | Code |
|------------|------|
| a_type[r,k,t] ≤ a[r,k] | `return model.a_type[r, k, t] <= model.a[r, k]` |

**Bedeutung:** Wenn `a[r,k] = 0`, dann muss auch `a_type = 0` sein.

---

### Constraint 2: a_type ≤ type_assignment

| Mathematik | Code |
|------------|------|
| a_type[r,k,t] ≤ type_assignment[k,t] | `return model.a_type[r, k, t] <= model.type_assignment[k, t]` |

**Bedeutung:** Wenn `type_assignment[k,t] = 0`, dann muss auch `a_type = 0` sein.

---

### Constraint 3: a_type ≥ a + type_assignment - 1

| Mathematik | Code |
|------------|------|
| a_type[r,k,t] ≥ a[r,k] + type_assignment[k,t] - 1 | `return model.a_type[r, k, t] >= model.a[r, k] + model.type_assignment[k, t] - 1` |

**Bedeutung:** Wenn BEIDE = 1 sind, dann muss `a_type = 1` sein.

---

## 6.4 Warum funktioniert das?

| a[r,k] | type_assignment[k,t] | Constraint 1 | Constraint 2 | Constraint 3 | → a_type |
|--------|---------------------|--------------|--------------|--------------|----------|
| 0 | 0 | ≤ 0 | ≤ 0 | ≥ -1 | **= 0** |
| 0 | 1 | ≤ 0 | ≤ 1 | ≥ 0 | **= 0** |
| 1 | 0 | ≤ 1 | ≤ 0 | ≥ 0 | **= 0** |
| 1 | 1 | ≤ 1 | ≤ 1 | ≥ 1 | **= 1** |

**Ergebnis:** `a_type[r,k,t] = 1` genau dann, wenn `a[r,k] = 1` UND `type_assignment[k,t] = 1`

Das ist genau das Verhalten eines Produkts!

---

## 6.5 Code-Implementierung

```python
# Constraint 1
def a_type_lin1_rule(model, r, k, t):
    return model.a_type[r, k, t] <= model.a[r, k]
model.con_a_type_lin1 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin1_rule)

# Constraint 2
def a_type_lin2_rule(model, r, k, t):
    return model.a_type[r, k, t] <= model.type_assignment[k, t]
model.con_a_type_lin2 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin2_rule)

# Constraint 3
def a_type_lin3_rule(model, r, k, t):
    return model.a_type[r, k, t] >= model.a[r, k] + model.type_assignment[k, t] - 1
model.con_a_type_lin3 = pyo.Constraint(model.R, model.K, model.T, rule=a_type_lin3_rule)
```

---

## 6.6 Zweite Linearisierung: truck_type_used

Gleiches Prinzip für `truck_type_used[k,t] = truck_used[k] × type_assignment[k,t]`:

```python
# truck_type_used = truck_used × type_assignment
def ttu_lin1_rule(model, k, t):
    return model.truck_type_used[k, t] <= model.truck_used[k]
def ttu_lin2_rule(model, k, t):
    return model.truck_type_used[k, t] <= model.type_assignment[k, t]
def ttu_lin3_rule(model, k, t):
    return model.truck_type_used[k, t] >= model.truck_used[k] + model.type_assignment[k, t] - 1
```

**Verwendung:** Berechnung der LKW-Fixkosten (nur für benutzte LKWs des jeweiligen Typs)

---

# 7. Nebenbedingungen (Constraints)

## 7.1 LKW-Typ-Zuordnung

### con_one_type_per_truck - Genau ein Typ pro LKW

| Mathematik | Code |
|------------|------|
| Σ type_assignment[k,t] = 1  ∀k∈K | `sum(model.type_assignment[k, t] for t in model.T) == 1` |

```python
def one_type_per_truck_rule(model, k):
    return sum(model.type_assignment[k, t] for t in model.T) == 1
model.con_one_type_per_truck = pyo.Constraint(model.K, rule=one_type_per_truck_rule)
```

**In Worten:** Jeder LKW ist entweder Diesel ODER eActros600 ODER eActros400 - genau einer!

---

### con_truck_used_lower/upper - Wird LKW benutzt?

| Mathematik | Code |
|------------|------|
| Σ a[r,k] ≤ \|R\| × truck_used[k] | Wenn Touren → truck_used=1 |
| truck_used[k] ≤ Σ a[r,k] | Wenn truck_used=1 → mind. 1 Tour |

```python
def truck_used_lower_rule(model, k):
    return sum(model.a[r, k] for r in model.R) <= len(model.R) * model.truck_used[k]

def truck_used_upper_rule(model, k):
    return model.truck_used[k] <= sum(model.a[r, k] for r in model.R)
```

**Zusammen:** `truck_used[k] = 1` ⟺ LKW k fährt mindestens eine Tour

---

## 7.2 Tour-Zuordnung

### con_tour_assignment - Jede Tour genau einem LKW

| Mathematik | Code |
|------------|------|
| Σ a[r,k] = 1  ∀r∈R | `sum(model.a[r, k] for k in model.K) == 1` |

```python
def tour_assignment_rule(model, r):
    return sum(model.a[r, k] for k in model.K) == 1
model.con_tour_assignment = pyo.Constraint(model.R, rule=tour_assignment_rule)
```

**In Worten:** Jede der 20 Touren wird von genau einem LKW gefahren.

**Beispiel für Tour 't-4':**
```
a['t-4',1] + a['t-4',2] + ... + a['t-4',14] = 1
     0     +     1      + ... +      0      = 1  ✓
                 ↑
          LKW 2 fährt Tour t-4
```

---

## 7.3 LKW-Bewegungslogik

### con_no_concurrent_tours - Keine zwei Touren gleichzeitig

| Mathematik | Code |
|------------|------|
| Σ active_tour[r,z] × a[r,k] ≤ 1  ∀k,z | `sum(model.active_tour[r, z] * model.a[r, k] for r in model.R) <= 1` |

```python
def no_concurrent_tours_rule(model, k, z):
    return sum(model.active_tour[r, z] * model.a[r, k] for r in model.R) <= 1
model.con_no_concurrent_tours = pyo.Constraint(model.K, model.Z, rule=no_concurrent_tours_rule)
```

**In Worten:** Ein LKW kann nicht zwei Touren gleichzeitig fahren.

**Beispiel:**
```
Zeit z = 40 (10:00 Uhr)
Tour t-4: aktiv    → active_tour['t-4', 40] = 1
Tour s-1: aktiv    → active_tour['s-1', 40] = 1

Wenn LKW 2 BEIDE Touren hätte:
  1 × a['t-4',2] + 1 × a['s-1',2] = 1 + 1 = 2 > 1  ✗ VERBOTEN!
```

---

### con_depart_definition - Definition der Abfahrt

| Mathematik | Code |
|------------|------|
| depart[k,z] = Σ start_at[r,z] × a[r,k] | `model.depart[k, z] == sum(...)` |

```python
def depart_definition_rule(model, k, z):
    return model.depart[k, z] == sum(model.start_at[r, z] * model.a[r, k] for r in model.R)
model.con_depart_definition = pyo.Constraint(model.K, model.Z, rule=depart_definition_rule)
```

**In Worten:** `depart[k,z] = 1` genau dann, wenn LKW k eine Tour hat, die in z startet.

---

## 7.4 Energie-Dynamik

### cons (Expression) - Energieverbrauch während Fahrt

| Mathematik | Code |
|------------|------|
| cons[k,z] = ΣΣ a_type[r,k,t] × active[r,z] × (dist[r] × avgEv_e[t] / dur_z[r]) | Expression |

```python
def cons_expr_rule(model, k, z):
    return sum(
        sum(
            model.a_type[r, k, t] * model.active_tour[r, z] *
            (model.dist[r] * model.avgEv_e[t] / model.dur_z[r])
            for r in model.R
        )
        for t in model.TE  # Nur E-LKWs verbrauchen Strom!
    )
model.cons = pyo.Expression(model.K, model.Z, rule=cons_expr_rule)
```

**Aufschlüsselung:**
```
cons[k,z] = Energieverbrauch von LKW k in Intervall z

          = Σ  Σ  (Fährt k als Typ t gerade Tour r?) × (Energie pro Intervall)
            t  r

          = a_type[r,k,t] × active_tour[r,z] × (dist[r] × avgEv_e[t] / dur_z[r])
                                                    ↑           ↑          ↑
                                               Distanz    Verbrauch    Dauer
                                                          kWh/km     Intervalle
```

**Beispiel:**
- Tour t-4: 250 km, Typ eActros600 (1.1 kWh/km), Dauer 41 Intervalle
- Energie gesamt: 250 × 1.1 = 275 kWh
- Energie pro Intervall: 275 / 41 = 6.7 kWh

---

### con_soc_dynamics - SOC-Fortschreibung

| Mathematik | Code |
|------------|------|
| soc[k,z+1] = soc[k,z] - cons[k,z] + Σ real_p[k,l,z] × 0.25 | `model.soc[k, z+1] == ...` |

```python
def soc_dynamics_rule(model, k, z):
    if z == 96:
        return pyo.Constraint.Skip  # Kein z+1 für z=96
    return (model.soc[k, z+1] == model.soc[k, z] - model.cons[k, z] +
            sum(model.real_p[k, l, z] for l in model.L) * 0.25)
model.con_soc_dynamics = pyo.Constraint(model.K, model.Z, rule=soc_dynamics_rule)
```

**In Worten:**
```
Akku morgen = Akku heute - Verbrauch + Laden
                              ↓           ↓
                         cons[k,z]   Σ real_p × 0.25
                                          ↑
                                    kW × 0.25h = kWh
```

---

### con_soc_upper - SOC-Obergrenze

| Mathematik | Code |
|------------|------|
| soc[k,z] ≤ Batteriekapazität | `model.soc[k, z] <= ...` |

```python
def soc_upper_rule(model, k, z):
    return model.soc[k, z] <= sum(model.type_assignment[k, t] * model.soc_e[t] for t in model.TE) + \
                               sum(model.type_assignment[k, t] * 1000 for t in model.TD)
model.con_soc_upper = pyo.Constraint(model.K, model.Z, rule=soc_upper_rule)
```

**Erklärung:**
- Wenn E-LKW: Max = soc_e[t] (621 oder 414 kWh)
- Wenn Diesel: Max = 1000 (hoher Wert, SOC ist irrelevant für Diesel)

---

### con_soc_cycle - Zyklische Randbedingung

| Mathematik | Code |
|------------|------|
| soc[k,1] = soc[k,96] | `model.soc[k, 1] == model.soc[k, 96]` |

```python
def soc_cycle_rule(model, k):
    return model.soc[k, 1] == model.soc[k, 96]
model.con_soc_cycle = pyo.Constraint(model.K, rule=soc_cycle_rule)
```

**Warum?** Der nächste Tag beginnt genauso wie dieser endet. Verhindert "Schummeln" durch leere Akkus am Tagesende.

---

## 7.5 Lade-Logik

### con_charging_requires_assign - Laden nur wenn zugewiesen

| Mathematik | Code |
|------------|------|
| real_p[k,l,z] ≤ assign[k,l,z] × M | `model.real_p[k, l, z] <= model.assign[k, l, z] * 10000` |

```python
def charging_requires_assign_rule(model, k, l, z):
    return model.real_p[k, l, z] <= model.assign[k, l, z] * 10000
```

**Logik:**
- Wenn `assign = 0` → `real_p ≤ 0` → `real_p = 0`
- Wenn `assign = 1` → `real_p ≤ 10000` (praktisch unbeschränkt)

---

### con_charging_power_limit - Ladeleistung durch LKW begrenzt

| Mathematik | Code |
|------------|------|
| real_p[k,l,z] ≤ max_p_e[type_k[k]] | `model.real_p[k, l, z] <= sum(...)` |

```python
def charging_power_limit_rule(model, k, l, z):
    return model.real_p[k, l, z] <= sum(model.type_assignment[k, t] * model.max_p_e[t] for t in model.T)
```

**Trick:** `max_p_e['ActrosL'] = 0` → Diesel-LKWs können nicht laden!

---

### con_assign_requires_plug - Laden nur wenn angesteckt

| Mathematik | Code |
|------------|------|
| assign[k,l,z] ≤ plug[k,l,z] | `model.assign[k, l, z] <= model.plug[k, l, z]` |

```python
def assign_requires_plug_rule(model, k, l, z):
    return model.assign[k, l, z] <= model.plug[k, l, z]
```

---

### con_one_charger_per_truck - Ein LKW, eine Säule

| Mathematik | Code |
|------------|------|
| Σ plug[k,l,z] ≤ 1  ∀k,z | `sum(model.plug[k, l, z] for l in model.L) <= 1` |

```python
def one_charger_per_truck_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1
```

---

### con_diesel_no_charging/plug - Diesel darf nicht laden

| Mathematik | Code |
|------------|------|
| assign[k,l,z] ≤ Σ type_assignment[k,t] (t∈TE) | Nur E-LKWs dürfen laden |
| plug[k,l,z] ≤ Σ type_assignment[k,t] (t∈TE) | Nur E-LKWs dürfen angesteckt sein |

```python
def diesel_no_charging_rule(model, k, l, z):
    return model.assign[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)

def diesel_no_plug_rule(model, k, l, z):
    return model.plug[k, l, z] <= sum(model.type_assignment[k, t] for t in model.TE)
```

---

### con_no_charge_while_driving - Nicht fahren UND laden

| Mathematik | Code |
|------------|------|
| Σ plug[k,l,z] ≤ 1 - Σ active_tour[r,z] × a[r,k] | Entweder fahren ODER angesteckt |

```python
def no_charge_while_driving_rule(model, k, z):
    return sum(model.plug[k, l, z] for l in model.L) <= 1 - sum(model.active_tour[r, z] * model.a[r, k] for r in model.R)
```

**Logik:**
- Wenn Tour aktiv: rechte Seite = 1 - 1 = 0 → plug muss 0 sein
- Wenn keine Tour: rechte Seite = 1 - 0 = 1 → plug kann 1 sein

---

### con_unplug_before_departure - Vor Abfahrt abstecken

| Mathematik | Code |
|------------|------|
| plug[k,l,z] ≤ 1 - depart[k,z+1] | Wenn morgen Abfahrt → heute nicht angesteckt |

```python
def unplug_before_departure_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] <= 1 - model.depart[k, z+1]
```

---

### con_unplug_timing - Nachts nicht abstecken

| Mathematik | Code |
|------------|------|
| plug[k,l,z] - plug[k,l,z+1] ≤ unplug_ok[z] | Abstecken nur wenn erlaubt |

```python
def unplug_timing_rule(model, k, l, z):
    if z == 96:
        return pyo.Constraint.Skip
    return model.plug[k, l, z] - model.plug[k, l, z+1] <= model.unplug_ok[z]
```

**Logik:**
```
plug[z] - plug[z+1] = 1  → LKW wird abgesteckt (war 1, ist jetzt 0)
plug[z] - plug[z+1] = 0  → Zustand bleibt gleich
plug[z] - plug[z+1] = -1 → LKW wird angesteckt (war 0, ist jetzt 1)

Abstecken (=1) nur erlaubt wenn unplug_ok[z] = 1
```

---

## 7.6 Ladesäulen-Kapazitäten

### con_total_charger_limit - Max 3 Säulen insgesamt

| Mathematik | Code |
|------------|------|
| Σ y_l[l] ≤ 3 | `sum(model.y_l[l] for l in model.L) <= model.Nmax` |

```python
def total_charger_limit_rule(model):
    return sum(model.y_l[l] for l in model.L) <= model.Nmax
```

---

### con_charger_assign_capacity - Ladepunkte begrenzen Gleichzeitigkeit

| Mathematik | Code |
|------------|------|
| Σ assign[k,l,z] ≤ y_l[l] × cs_l[l] | Anzahl ladender LKWs ≤ Ladepunkte |

```python
def charger_assign_capacity_rule(model, l, z):
    return sum(model.assign[k, l, z] for k in model.K) <= model.y_l[l] * model.cs_l[l]
```

**Beispiel:** 2 Säulen × 2 Ladepunkte = max 4 LKWs gleichzeitig

---

### con_charger_power_capacity - Gesamtleistung begrenzt

| Mathematik | Code |
|------------|------|
| Σ real_p[k,l,z] ≤ y_l[l] × max_p_l[l] | Gesamtleistung ≤ Säulenleistung |

```python
def charger_power_capacity_rule(model, l, z):
    return sum(model.real_p[k, l, z] for k in model.K) <= model.y_l[l] * model.max_p_l[l]
```

---

## 7.7 Netz und Speicher

### con_grid_balance - Netzlastbilanz

| Mathematik | Code |
|------------|------|
| p_grid[z] = Σ real_p[k,l,z] + p_l_s[z] - p_e_s[z] | Netzbezug = LKW-Laden + Speicher-Laden - Speicher-Entladen |

```python
def grid_balance_rule(model, z):
    return (model.p_grid[z] == sum(model.real_p[k, l, z] for k in model.K for l in model.L) +
            model.p_l_s[z] - model.p_e_s[z])
```

**Visualisierung:**
```
Stromnetz ═══╦═══════════════════════════════════►  LKW-Laden (Σ real_p)
             ║
             ╠═══► Speicher laden (p_l_s)
             ║
             ◄═══ Speicher entladen (p_e_s)

p_grid = Σ real_p + p_l_s - p_e_s
```

---

### con_grid_limit - Netzanschlussgrenze

| Mathematik | Code |
|------------|------|
| p_grid[z] ≤ 500 + 500 × u | Max 500kW ohne Trafo, 1000kW mit Trafo |

```python
def grid_limit_rule(model, z):
    return model.p_grid[z] <= model.p_grid_max + 500 * model.u
```

---

### con_peak_power - Leistungsspitze erfassen

| Mathematik | Code |
|------------|------|
| p_grid[z] ≤ p_peak  ∀z | p_peak ist Maximum aller p_grid[z] |

```python
def peak_power_rule(model, z):
    return model.p_grid[z] <= model.p_peak
```

**Wichtig:** p_peak wird in der Zielfunktion mit dem Leistungspreis bestraft!

---

### con_storage_dynamics - Speicher-Fortschreibung

| Mathematik | Code |
|------------|------|
| soc_s[z+1] = soc_s[z] + p_l_s[z]×Δt - (1/nrt)×p_e_s[z]×Δt | Mit Round-Trip-Verlust! |

```python
def storage_dynamics_rule(model, z):
    if z == 96:
        return pyo.Constraint.Skip
    return (model.soc_s[z+1] == model.soc_s[z] + model.p_l_s[z] * model.delta_t -
            (1/model.nrt) * model.p_e_s[z] * model.delta_t)
```

**Wichtig:** Beim Entladen wird durch nrt geteilt → Verlust berücksichtigt!

---

### con_storage_reserve - Mindestreserve (DoD)

| Mathematik | Code |
|------------|------|
| soc_s[z] ≥ dod × q_s | Mindestens 2.5% müssen im Speicher bleiben |

```python
def storage_reserve_rule(model, z):
    return model.soc_s[z] >= model.dod * model.q_s
```

---

### con_storage_charge/discharge_mode_binary - Nicht gleichzeitig laden UND entladen

| Mathematik | Code |
|------------|------|
| p_l_s[z] ≤ M × mode_s[z] | Laden nur wenn mode_s = 1 |
| p_e_s[z] ≤ M × (1 - mode_s[z]) | Entladen nur wenn mode_s = 0 |

```python
def storage_charge_mode_binary_rule(model, z):
    return model.p_l_s[z] <= 10000 * model.mode_s[z]

def storage_discharge_mode_binary_rule(model, z):
    return model.p_e_s[z] <= 10000 * (1 - model.mode_s[z])
```

---

# 8. Zielfunktion

## 8.1 Überblick

```
min C_total = C_trucks + C_chargers + C_grid_trafo + C_storage + C_diesel_var + C_electricity - C_revenue
```

| Komponente | Beschreibung |
|------------|--------------|
| C_trucks | LKW-Fixkosten (Leasing, Wartung, KFZ-Steuer) |
| C_chargers | Ladesäulen-Kosten |
| C_grid_trafo | Trafo-Upgrade (10.000€ wenn u=1) |
| C_storage | Speicherkosten |
| C_diesel_var | Variable Dieselkosten (Treibstoff + Maut) |
| C_electricity | Stromkosten (Arbeit + Leistung + Grundgebühr) |
| C_revenue | THG-Erlöse (wird ABGEZOGEN) |

---

## 8.2 C_trucks - LKW-Fixkosten

| Mathematik |
|------------|
| C_trucks = Σ Σ truck_type_used[k,t] × (cap + opx + kfz) |

```python
C_trucks = sum(
    sum(model.truck_type_used[k, t] * (model.cap_d[t] + model.opx_d[t] + model.kfz_d[t]) for t in model.TD) +
    sum(model.truck_type_used[k, t] * (model.cap_e[t] + model.opx_e[t]) for t in model.TE)
    for k in model.K
)
```

**Erklärung:**
- `truck_type_used[k,t] = 1` nur wenn LKW k benutzt wird UND vom Typ t ist
- Diesel: Leasing + Wartung + KFZ-Steuer
- E-LKW: Leasing + Wartung (keine KFZ-Steuer!)

---

## 8.3 C_chargers - Ladesäulen-Kosten

| Mathematik |
|------------|
| C_chargers = Σ y_l[l] × (cap_l[l] + opx_l[l]) |

```python
C_chargers = sum(model.y_l[l] * (model.cap_l[l] + model.opx_l[l]) for l in model.L)
```

---

## 8.4 C_grid_trafo - Trafo-Kosten

| Mathematik |
|------------|
| C_grid_trafo = 10.000 × u |

```python
C_grid_trafo = 10000 * model.u
```

---

## 8.5 C_storage - Speicherkosten

| Mathematik |
|------------|
| C_storage = (1 + opx_s) × (capP_s × p_s + capQ_s × q_s) |

```python
C_storage = (1 + model.opx_s) * (model.capP_s * model.p_s + model.capQ_s * model.q_s)
```

**Komponenten:**
- Leistungskosten: 30 €/kW × p_s
- Kapazitätskosten: 350 €/kWh × q_s
- Plus 2% Wartung

---

## 8.6 C_diesel_var - Variable Dieselkosten

| Mathematik |
|------------|
| C_diesel_var = 260 × Σ a_type[r,k,t] × (Maut + Diesel) |

```python
C_diesel_var = 260 * sum(
    model.a_type[r, k, t] * (model.c_m_d * model.mDist[r] +
                              model.c_diesel * model.dist[r] * model.avgDv_d[t])
    for r in model.R for k in model.K for t in model.TD
)
```

**Komponenten:**
- 260 = Arbeitstage pro Jahr
- Maut: 0.34 €/km × mautpflichtige km
- Diesel: 1.50 €/L × Distanz × Verbrauch (L/km)

---

## 8.7 C_electricity - Stromkosten

| Mathematik |
|------------|
| C_electricity = c_gr + cPeak × p_peak + 260 × c_e × Σ p_grid[z] × Δt |

```python
C_electricity = model.c_gr + model.cPeak * model.p_peak + \
                260 * model.c_e * sum(model.p_grid[z] * model.delta_t for z in model.Z)
```

**Komponenten:**
- Grundgebühr: 1.000 €/Jahr
- Leistungspreis: 150 €/kW × Jahresspitze (p_peak)
- Arbeitspreis: 260 Tage × 0.25 €/kWh × Σ(p_grid × 0.25h)

---

## 8.8 C_revenue - THG-Erlöse

| Mathematik |
|------------|
| C_revenue = Σ truck_type_used[k,t] × thg_e[t]  (nur t∈TE) |

```python
C_revenue = sum(
    sum(model.truck_type_used[k, t] * model.thg_e[t] for t in model.TE)
    for k in model.K
)
```

**Wichtig:** Wird ABGEZOGEN (Einnahme, nicht Kosten!)

---

# 9. Speicher, DoD und Round-Trip-Efficiency

## 9.1 Wozu ein Speicher?

**Problem:** Netzanschluss begrenzt auf 500kW, aber 3 LKWs wollen gleichzeitig mit 200kW laden = 600kW

**Lösung:**
```
Nachts (niemand lädt):     Netz → Speicher (lädt sich auf)
Tagsüber (Lastspitze):     Netz + Speicher → LKWs
```

---

## 9.2 Round-Trip-Efficiency (nrt = 98%)

**Was geht rein ≠ Was rauskommt**

```
100 kWh reinladen → 100 kWh im Speicher → 98 kWh rausbekommen
                                               ↑
                                          2 kWh Verlust
```

**Im Code:**
```python
soc_s[z+1] = soc_s[z] + p_l_s[z] * 0.25 - (1/0.98) * p_e_s[z] * 0.25
                        ↑                  ↑
                   Laden: 1:1         Entladen: muss mehr "bezahlen"
```

Wenn du 100 kWh entladen willst, werden dem Speicher 100/0.98 = 102.04 kWh abgezogen.

---

## 9.3 Depth of Discharge (dod = 2.5%)

**Mindestreserve im Speicher**

```
100 kWh Speicher:

100% ┃████████████████████┃ Voll
     ┃████████████████████┃
     ┃████████████████████┃ Nutzbar: 97.5 kWh
     ┃░░░░░░░░░░░░░░░░░░░░┃
2.5% ┃░░░░░░░░░░░░░░░░░░░░┃ Reserve: 2.5 kWh (TABU!)
```

**Im Code:**
```python
soc_s[z] >= 0.025 * q_s  # Mindestens 2.5% müssen drin bleiben
```

**Warum?** Tiefentladung schadet der Batterielebensdauer.

---

## 9.4 Beispielrechnung

Speicher: q_s = 200 kWh, nrt = 98%, dod = 2.5%

**Nutzbare Kapazität:**
```
200 kWh × (1 - 0.025) = 195 kWh
```

**Bei Volllast entladen (195 kWh effektiv):**
```
Dem Speicher werden entnommen: 195 / 0.98 = 199 kWh
Es bleiben übrig: 200 - 199 = 1 kWh... ABER:
Minimum wegen DoD: 200 × 0.025 = 5 kWh

→ Tatsächlich nutzbar: 200 - 5 = 195 kWh
→ Nach Entladeverlusten: 195 × 0.98 = 191 kWh effektiv
```

---

# Zusammenfassung

## Das Modell auf einen Blick

| Kategorie | Anzahl | Beispiele |
|-----------|--------|-----------|
| Indexmengen | 8 | R, K, T, L, Z, ... |
| Parameter | ~30 | dist, soc_e, c_diesel, ... |
| Variablen | ~15 Typen | a, type_assignment, real_p, soc, ... |
| Constraints | ~25 Typen | Tour-Zuordnung, SOC-Dynamik, Netzlimit, ... |
| Zielfunktion | 7 Komponenten | Trucks, Chargers, Strom, ... |

## Die wichtigsten Entscheidungen

1. **Welcher LKW fährt welche Tour?** → a[r,k]
2. **Welcher LKW ist welcher Typ?** → type_assignment[k,t]
3. **Wie viele Ladesäulen?** → y_l[l]
4. **Wann/wie viel laden?** → real_p[k,l,z]
5. **Trafo-Upgrade?** → u
6. **Speichergröße?** → p_s, q_s

## Der Optimierungsablauf

```
Eingabe: Touren, LKW-Daten, Kosten, ...
    ↓
MILP-Solver (GLPK/CBC/HiGHS)
    ↓
Ausgabe: Optimale Flottenkonfiguration + Ladeplan
    ↓
Minimale Jahreskosten
```

---

*Dokumentation erstellt für die Präsentation der OR-Fallstudie*
