# MILP-Modelldokumentation — Aktualisierte Fassung

> **MILP = Mixed Integer Linear Programming**
> - **Mixed Integer**: Mischung aus ganzzahligen Variablen (z.B. "Wie viele Ladesäulen?") und kontinuierlichen Variablen (z.B. "Mit wie viel kW laden?")
> - **Linear**: Alle Gleichungen und Ungleichungen sind linear (keine x², keine x·y)
> - **Programming**: Mathematisches Optimierungsproblem


---

## 1. Indexmengen (Sets)

| Name | Definition / Bedeutung |
|------|----------------------|
| **R** | = {'t-4', 't-5', 't-6', 's-1', 's-2', 's-3', 's-4', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7', 'r1', 'r2', 'r3', 'h3', 'h4', 'k1'} — Menge aller Touren (20 Stück). |
| **TD** | = {'ActrosL'} — Menge der Diesel-LKW-Typen. |
| **TE** | = {'eActros600', 'eActros400'} — Menge der Elektro-LKW-Typen. |
| **L** | = {'Alpitronic-50', 'Alpitronic-200', 'Alpitronic-400'} — Menge der Ladesäulentypen. |
| **Z** | = {1, …, 96} — Menge der Zeitintervalle (je 15 Minuten, 24-Stunden-Tag). |
| **Z_day** | = {25, …, 72} — Tageszeitintervalle (6:00 bis 17:45 Uhr). |
| **Z_night** | = Z \ Z_day — Nachtzeitintervalle (18:00 bis 5:45 Uhr). |
| **K** | = {1, 2, …, 14} — Menge der LKWs (14 Fahrzeuge). |

---

## 2. Parameter

### 2.1 Tourenparameter

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **dist[r]** (r∈R) | Gesamtdistanz der Tour r in km. |
| **mDist[r]** (r∈R) | Mautpflichtige Distanz der Tour r in km. |
| **start[r]** (r∈R) | Startuhrzeit der Tour r (als Uhrzeit, z. B. 06:45). |
| **end[r]** (r∈R) | Enduhrzeit der Tour r. |
| **s_r(r)** (r∈R, s_r: R→Z) | Startintervall-Index der Tour r. Formale Umrechnung: s_r(r) = 4 · start_h(r) + 1, wobei start_h(r) die Startzeit in Dezimalstunden ist (z. B. 06:45 → 6,75 → s_r = 28). |
| **e_r(r)** (r∈R, e_r: R→Z) | Endintervall-Index der Tour r. Formale Umrechnung: e_r(r) = 4 · end_h(r) + 1, wobei end_h(r) die Endzeit in Dezimalstunden ist (z. B. 17:00 → 17,0 → e_r = 69). |
| **dur_z[r]** (r∈R) | Dauer der Tour r in Zeitintervallen; dur_z[r] = e_r(r) − s_r(r). |

**Konkrete s_r / e_r – Werte:**

| Tour | s_r | e_r | | Tour | s_r | e_r |
|------|-----|-----|-|------|-----|-----|
| t-4 | 28 | 69 | | w4 | 25 | 65 |
| t-5 | 27 | 70 | | w5 | 29 | 69 |
| t-6 | 25 | 67 | | w6 | 23 | 63 |
| s-1 | 23 | 63 | | w7 | 30 | 70 |
| s-2 | 25 | 65 | | r1 | 73 | 91 |
| s-3 | 37 | 65 | | r2 | 67 | 88 |
| s-4 | 27 | 67 | | r3 | 72 | 87 |
| w1 | 23 | 63 | | h3 | 76 | 92 |
| w2 | 33 | 73 | | h4 | 75 | 91 |
| w3 | 28 | 69 | | k1 | 67 | 91 |

### 2.2 Abgeleitete Zeitparameter (binär)

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **start_at[r,z]** (r∈R, z∈Z, ∈{0,1}) | = 1 genau dann, wenn z = s_r(r), sonst 0. Markiert den Startzeitpunkt einer Tour. |
| **end_at[r,z]** (r∈R, z∈Z, ∈{0,1}) | = 1 genau dann, wenn z = e_r(r), sonst 0. Markiert den Endzeitpunkt einer Tour. |
| **active[r,z]** (r∈R, z∈Z, ∈{0,1}) | = 1 genau dann, wenn s_r(r) ≤ z < e_r(r), sonst 0. Gibt an, ob Tour r zum Zeitpunkt z aktiv ist. |
| **unplug_ok[z]** (z∈Z, ∈{0,1}) | Abstecken von Ladestation erlaubt. = 1 wenn z ∈ Z_day; = 0 wenn z ∈ Z_night; = 1 wenn z+1 = z6 (d. h. z = 24). |

### 2.3 Diesel-LKW-Parameter

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **cap_d[t]** (t∈TD) | Jährliche Leasingkosten für Diesel-LKW-Typ t. cap_d['ActrosL'] = 24.000. |
| **opx_d[t]** (t∈TD) | Jährliche Wartungskosten. opx_d['ActrosL'] = 6.000. |
| **avgDv_d[t]** (t∈TD) | Durchschnittlicher Dieselverbrauch in L/100km. avgDv_d['ActrosL'] = 0,26 (Einheit: L/100km bestätigt). |
| **kfz_d[t]** (t∈TD) | KFZ-Steuer. kfz_d['ActrosL'] = 556. |
| **c_diesel** | = 1,50 €/Liter — Dieselpreis. |

### 2.4 Elektro-LKW-Parameter

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **cap_e[t]** (t∈TE) | Jährliche Leasingkosten. cap_e['eActros600'] = 60.000; cap_e['eActros400'] = 50.000. |
| **opx_e[t]** (t∈TE) | Jährliche Wartungskosten. opx_e['eActros600'] = 6.000; opx_e['eActros400'] = 5.000. |
| **avgEv_e[t]** (t∈TE) | Durchschnittlicher Energieverbrauch (kWh/km). avgEv_e['eActros600'] = 1,1; avgEv_e['eActros400'] = 1,05. |
| **thg_e[t]** (t∈TE) | Treibhausgasquotenerlös pro E-LKW und Jahr. thg_e['eActros600'] = 1.000; thg_e['eActros400'] = 1.000. |
| **max_p_e[t]** (t∈TE) | Maximale Ladeleistung des E-LKW-Typs in kW. max_p_e['eActros600'] = 400; max_p_e['eActros400'] = 400. Nur für Elektro-Typen definiert. |
| **soc_e[t]** (t∈TE) | Batteriekapazität in kWh. soc_e['eActros600'] = 621; soc_e['eActros400'] = 414. |

### 2.5 Ladesäulen-Parameter

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **cap_l[l]** (l∈L) | Jährliche Leasingkosten. cap_l['Alpitronic-50'] = 3.000; cap_l['Alpitronic-200'] = 10.000; cap_l['Alpitronic-400'] = 16.000. |
| **opx_l[l]** (l∈L) | Jährliche Wartungskosten. opx_l['Alpitronic-50'] = 1.000; opx_l['Alpitronic-200'] = 1.500; opx_l['Alpitronic-400'] = 2.000. |
| **max_p_l[l]** (l∈L) | Maximale Ladeleistung in kW. max_p_l['Alpitronic-50'] = 50; max_p_l['Alpitronic-200'] = 200; max_p_l['Alpitronic-400'] = 400. |
| **cs_l[l]** (l∈L) | Anzahl Ladepunkte (Charging Spots) pro Ladesäule. Für alle l = 2. |

### 2.6 Netz-, Speicher- & Sonstige Parameter

| Name (Indizes) | Bedeutung |
|----------------|-----------|
| **delta_t** | = 0,25 — Dauer eines Zeitintervalls in Stunden. |
| **z6** | = 25 — Intervallindex für 6:00 Uhr. |
| **Nmax** | = 3 — Maximale Anzahl Ladesäulen pro Standort. |
| **p_grid_max** | = 500 kW — Maximale Netzanschlussleistung ohne Trafo-Upgrade. |
| **c_e** | = 0,25 €/kWh — Arbeitspreis Strom. |
| **c_gr** | = 1.000 € — Grundgebühr Strom (jährlich). |
| **c_m_d** | = 0,34 €/km — Mautkosten pro mautpflichtigem km. |
| **cPeak** | = 150 €/kW·a — Leistungspreis Netzanschluss. |
| **capP_s** | = 30 €/kW·a — Kapitalkosten Speicherleistung. |
| **capQ_s** | = 350 €/kWh·a — Kapitalkosten Speicherkapazität. |
| **opx_s** | = 0,02 — Betriebskosten-Faktor Speicher (2 % von Capex). |
| **nrt** | = 0,98 — Round-Trip-Effizienz des Speichers. |
| **dod** | = 0,025 — Depth of Discharge / Mindestreserve (2,5 %). |

 Parameter **M** = 10.000 wurde entfernt (laut Anwender nicht mehr benötigt).

---

## 3. Entscheidungsvariablen

| Name (Indizes, Wertebereich) | Bedeutung |
|------------------------------|-----------|
| **type_k[k]** (k∈K, ∈ TD ∪ TE) | Zuordnung eines LKW-Typs zu LKW k. Entscheidungsvariable (kategorial). |
| **truck_used[k]** (k∈K, ∈ {0,1}) | = 1, wenn LKW k eingesetzt wird. |
| **a[r,k]** (r∈R, k∈K, ∈ {0,1}) | = 1, wenn Tour r von LKW k gefahren wird. |
| **y_l[l]** (l∈L, ∈ ℤ≥0) | Anzahl installierter Ladesäulen des Typs l. Ganzzahlig, beschränkt durch Nmax (siehe C33). |
| **assign[k,l,z]** (k∈K, l∈L, z∈Z, ∈ {0,1}) | = 1, wenn LKW k an Ladesäule l zum Zeitpunkt z aktiv lädt. |
| **plug[k,l,z]** (k∈K, l∈L, z∈Z, ∈ {0,1}) | = 1, wenn LKW k einen Ladepunkt des Typs l im Intervall z belegt (angesteckt, auch ohne zu laden). |
| **real_p[k,l,z]** (k∈K mit type_k[k]∈TE, l∈L, z∈Z, ≥ 0) | Reale Ladeleistung von E-LKW k an Ladesäule l zum Zeitpunkt z (kW). Nur für Elektro-LKWs definiert. |
| **P_truck[z]** (z∈Z, ≥ 0) | Gesamte Ladeleistung aller LKWs im Zeitintervall z (kW). Formalisiert als Hilfsvariable (siehe C34). |
| **depart[k,z]** (k∈K, z∈Z, ∈ {0,1}) | Gibt an, ob LKW k zum Zeitpunkt z eine Tour startet. Wird per Constraint (C12) definiert. |
| **cons[k,z]** (k∈K, z∈Z, ≥ 0) | Energieverbrauch von LKW k im Zeitintervall z (kWh). Wird per Constraint (C6/C7) definiert. |
| **soc[k,z]** (k∈K mit type_k[k]∈TE, z=1,…,96, ≥ 0) | Ladezustand (State of Charge) von E-LKW k zum Zeitpunkt z (kWh). |
| **u** (∈ {0,1}) | Binärvariable für Transformator-Ausbau-Entscheidung. |
| **p_s** (≥ 0) | Leistung des stationären Speichers (kW). |
| **q_s** (≥ 0) | Kapazität des stationären Speichers (kWh). |
| **p_l_s[z]** (z∈Z, ≥ 0) | Ladeleistung des Speichers aus dem Netz zum Zeitpunkt z (kW). |
| **p_e_s[z]** (z∈Z, ≥ 0) | Entladeleistung des Speichers zum Zeitpunkt z (kW). |
| **soc_s[z]** (z∈Z, ≥ 0) | Füllstand des stationären Speichers zum Zeitpunkt z (kWh). |
| **p_grid[z]** (z∈Z, ≥ 0) | Netzbezugsleistung zum Zeitpunkt z (kW). |
| **p_peak** (≥ 0) | Maximale Netzbezugsleistung über alle z (kW). |
| **mode_s[z]** (z∈Z, ∈ {0,1}) | Speichermodus: 1 = Laden, 0 = Entladen. |

---

## 4. Nebenbedingungen (Constraints)

### 4.1 LKW-Einsatz und Tourenzuweisung

**(C1)** truck_used[k] ≤ Σ_{r∈R} a[r,k] ∀k∈K
— Wenn keine Tour von k gefahren wird, kann truck_used[k] nicht 1 sein.

**(C2)** Σ_{r∈R} a[r,k] ≤ |R| × truck_used[k] ∀k∈K
— Wenn LKW k Touren fährt, muss truck_used[k] = 1 sein.

**(C3)** Σ_{k∈K} a[r,k] = 1 ∀r∈R
— Jede Tour wird genau einem LKW zugeordnet.

**(C4)** Σ_{r∈R} active[r,z] · a[r,k] ≤ 1 ∀k∈K, z∈Z
— Ein LKW kann nicht zwei Touren gleichzeitig fahren.

**(C5)** Σ_{r∈R} end_at[r,z] · a[r,k] ≤ 1 ∀k∈K, z∈Z
— Kein LKW darf zwei Touren zum selben Zeitpunkt beenden.

### 4.2 Energieverbrauch und Ladezustand (E-LKWs)

**(C6)** cons[k,z] = Σ_{r∈R} active[r,z] · a[r,k] · (dist[r] · avgEv_e[type_k[k]] / dur_z[r]) ∀k∈K mit type_k[k]∈TE, ∀z∈Z
— Energieverbrauch von Elektro-LKW k im Zeitintervall z (gleichmäßig über Tourdauer verteilt).

**(C7)** cons[k,z] = 0 ∀k∈K mit type_k[k]∈TD, ∀z∈Z
— Diesel-LKWs haben keinen elektrischen Energieverbrauch.

**(C8)** soc[k,z+1] = soc[k,z] − cons[k,z] + Σ_{l∈L} real_p[k,l,z] · 0,25 ∀k∈K: type_k[k]∈TE, z=1,…,95
— SOC-Fortschreibung: aktueller Zustand − Verbrauch + Lademenge.

**(C9)** soc[k,z] ≥ 0 ∀k∈K mit type_k[k]∈TE, z=1,…,96
— Akku darf nicht negativ werden.

**(C10)** soc[k,z] ≤ soc_e[type_k[k]] ∀k∈K mit type_k[k]∈TE, z=1,…,96
— Akku darf nicht über Batteriekapazität geladen werden.

**(C11)** soc[k,1] = soc[k,96] ∀k∈K mit type_k[k]∈TE
— Alle E-LKWs beenden den Tag mit demselben Ladezustand wie zu Beginn.

### 4.3 Abfahrt-Indikator

**(C12)** depart[k,z] = Σ_{r∈R} start_at[r,z] · a[r,k] ∀k∈K, z∈Z
— Gibt an, ob LKW k zum Zeitpunkt z eine Tour startet.

### 4.4 Ladeinfrastruktur

**(C13)** Σ_{k∈K} assign[k,l,z] ≤ y_l[l] · cs_l[l] ∀l∈L, z∈Z
— Anzahl gleichzeitig ladender LKWs ≤ verfügbare Ladepunkte.

**(C14)** Σ_{k∈K} plug[k,l,z] ≤ y_l[l] · cs_l[l] ∀l∈L, z∈Z
— Anzahl gleichzeitig angesteckter LKWs ≤ verfügbare Ladepunkte.

**(C15)** Σ_{k∈K: type_k[k]∈TE} real_p[k,l,z] ≤ y_l[l] · max_p_l[l] ∀l∈L, z∈Z 
— Gesamtladeleistung der E-LKWs an Säulentyp l darf dessen maximale Leistung (× Anzahl) nicht überschreiten.

**(C16)** Σ_{l∈L} plug[k,l,z] ≤ 1 ∀k∈K, z∈Z
— Ein LKW darf zu einem Zeitpunkt nur an einem Ladesäulentyp angesteckt sein.

**(C17)** real_p[k,l,z] ≤ assign[k,l,z] · max_p_e[type_k[k]] ∀k∈K mit type_k[k]∈TE, l∈L, z∈Z 
— Ladeleistung ≤ max. Leistung des E-LKW-Typs. Gilt nur für Elektro-LKWs.

**(C18)** assign[k,l,z] = 0 ∀k∈K mit type_k[k]∈TD, ∀l∈L, z∈Z
— Nur E-LKWs dürfen laden.

**(C19)** plug[k,l,z] = 0 ∀k∈K mit type_k[k]∈TD, ∀l∈L, z∈Z
— Diesel-LKWs dürfen nicht angesteckt sein.

**(C20)** Σ_{l∈L} plug[k,l,z] ≤ 1 − Σ_{r∈R} active[r,z] · a[r,k] ∀k∈K, z∈Z
— Nicht gleichzeitig fahren und angesteckt sein.

**(C32)** assign[k,l,z] ≤ plug[k,l,z] ∀k∈K, l∈L, z∈Z
— Laden (assign=1) erfordert Anstecken (plug=1).

**(C33)** Σ_{l∈L} y_l[l] ≤ Nmax
— Gesamtanzahl installierter Ladesäulen über alle Typen hinweg darf Nmax nicht überschreiten.

### 4.5 Stecker-/Abfahrt-Logik

**(C30)** plug[k,l,z] − plug[k,l,z+1] ≤ unplug_ok[z] ∀k∈K, l∈L, z=1,…,95
— Stecker darf nur gezogen werden, wenn unplug_ok = 1 (nicht zwischen 18:00 und 5:45 Uhr).

**(C31)** plug[k,l,z] ≤ 1 − depart[k,z+1] ∀k∈K, l∈L, z=1,…,95
— Wenn LKW im nächsten Intervall eine Tour startet, darf er im aktuellen Intervall nicht angesteckt sein.

### 4.6 Netzanschluss und Leistung

**(C21)** p_grid[z] ≤ p_grid_max + 500 · u ∀z∈Z
— Netzbezugsleistung ≤ Netzanschlussgrenze (mit optionalem Trafo-Upgrade um 500 kW).

**(C22)** p_grid[z] = Σ_{k∈K: type_k[k]∈TE} Σ_{l∈L} real_p[k,l,z] + p_l_s[z] − p_e_s[z] ∀z∈Z 
— Netzbezug = E-LKW-Ladung + Speicher-Ladung − Speicher-Entladung.

**(C23)** p_grid[z] ≤ p_peak ∀z∈Z
— p_peak wird vom Solver als maximale Netzbezugsleistung über alle z bestimmt.

**(C34)** P_truck[z] = Σ_{k∈K: type_k[k]∈TE} Σ_{l∈L} real_p[k,l,z] ∀z∈Z
— Gesamte Ladeleistung aller E-LKWs im Zeitintervall z.

### 4.7 Stationärer Speicher

**(C24)** p_l_s[z] ≤ mode_s[z] · p_s ∀z∈Z
— Speicher darf nicht schneller laden als Nennleistung; nur wenn mode_s = 1.

**(C25)** p_e_s[z] ≤ (1 − mode_s[z]) · p_s ∀z∈Z
— Speicher darf nicht schneller entladen als Nennleistung; nur wenn mode_s = 0.

**(C26)** soc_s[z] ≤ q_s ∀z∈Z
— Speicherfüllstand ≤ Kapazität.

**(C27)** soc_s[z] ≥ dod · q_s ∀z∈Z
— Speicher muss Mindestreserve (2,5 %) halten.

**(C28)** soc_s[z+1] = soc_s[z] + p_l_s[z] · delta_t − (1/nrt) · p_e_s[z] · delta_t z=1,…,95
— SOC-Fortschreibung des Speichers mit Entladeverlusten.

**(C29)** soc_s[1] = soc_s[96]
— Speicher beendet den Tag mit demselben Stand wie zu Beginn.

---

## 5. Zielfunktion

 Cdiesel,var war in der Originaldatei nicht in der Gesamtkostensumme enthalten. Laut Anwender fehlt dieser Term.

### Gesamtkosten (Minimierung):

**min C_total = C_trucks + C_chargers + C_grid_trafo + C_storage + C_electricity + C_diesel,var − C_revenue**

### Teilkomponenten:

**C_trucks** — LKW-Fixkosten (jährlich):

 C_trucks = Σ_{k∈K} truck_used[k] × (
 𝟙_{type_k[k]∈TD} · (cap_d[type_k[k]] + opx_d[type_k[k]] + kfz_d[type_k[k]])
 + 𝟙_{type_k[k]∈TE} · (cap_e[type_k[k]] + opx_e[type_k[k]])
 )

**C_chargers** — Ladeinfrastruktur-Fixkosten (jährlich):

 C_chargers = Σ_{l∈L} y_l[l] · (cap_l[l] + opx_l[l])

**C_grid_trafo** — Netzanschluss / Transformator-Option:

 C_grid_trafo = 10.000 · u

**C_storage** — Stationärer Speicher (jährlich):

 C_storage = (capP_s · p_s + capQ_s · q_s) + opx_s · (capP_s · p_s + capQ_s · q_s)
 = (1 + opx_s) · (capP_s · p_s + capQ_s · q_s)

**C_diesel,var** — Variable Dieselkosten + Maut (jährlich):

 C_diesel,var = 260 · Σ_{r∈R} Σ_{k∈K: type_k[k]∈TD} a[r,k] · (
 c_m_d · mDist[r] + c_diesel · (dist[r] / 100) · avgDv_d[type_k[k]]
 )

Hinweis: Der Faktor 260 steht für Arbeitstage pro Jahr (nicht als benannter Parameter definiert, laut Anwender gewünscht). avgDv_d ist in L/100km angegeben, daher dist[r]/100.

**C_electricity** — Stromkosten (Arbeitspreis + Grundgebühr + Leistungspreis, jährlich):

 C_electricity = c_gr + cPeak · p_peak + 260 · c_e · Σ_{z∈Z} p_grid[z] · delta_t

**C_revenue** — Erlöse (THG-Quote, jährlich):

 C_revenue = Σ_{k∈K: type_k[k]∈TE} truck_used[k] × thg_e[type_k[k]]

**Optimierungsziel:** Minimierung der jährlichen Gesamtkosten (Fixkosten + variable Kosten − Erlöse).

---

*Dokument basiert ausschließlich auf den Inhalten der Datei „MatheCodeGEkürzt.docx" und den expliziten Klärungen des Anwenders. Alle offenen Fragen sind geklärt.*
