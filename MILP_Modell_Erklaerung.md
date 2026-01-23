# VOLLSTäNDIGE ERKLäRUNG DES MILP-OPTIMIERUNGSMODELLS

## Inhaltsverzeichnis
1. [Grundlagen: Mathematische Notation verstehen](#1-grundlagen-mathematische-notation-verstehen)
2. [Was ist MILP?](#2-was-ist-milp)
3. [Indexmengen im Detail](#3-indexmengen-im-detail)
4. [Parameter im Detail](#4-parameter-im-detail)
5. [Entscheidungsvariablen im Detail](#5-entscheidungsvariablen-im-detail)
6. [Berechnete Variablen](#6-berechnete-variablen)
7. [Nebenbedingungen im Detail](#7-nebenbedingungen-im-detail)
8. [Zielfunktion im Detail](#8-zielfunktion-im-detail)

---

# 1. GRUNDLAGEN: MATHEMATISCHE NOTATION VERSTEHEN

## 1.1 Das Summenzeichen (Sigma)

Das Symbol **Σ** (griechischer Buchstabe Sigma) bedeutet "Summe".

### Aufbau:
```
Σ_{i∈M} ausdruck[i]
```

**Bestandteile:**
- `Σ` = "Summiere"
- `i∈M` = "für alle i aus der Menge M" (Laufindex)
- `ausdruck[i]` = Was summiert wird

### Beispiel 1: Einfache Summe
```
Σ_{k∈K} a[r,k]   wobei K = {1, 2, 3, 4, 5}
```

**Gesprochen:** "Die Summe über alle k aus K von a[r,k]"

**Bedeutet konkret:**
```
a[r,1] + a[r,2] + a[r,3] + a[r,4] + a[r,5]
```

### Beispiel 2: Doppelte Summe
```
Σ_{k∈K} Σ_{l∈L} real_p[k,l,z]
```

**Gesprochen:** "Die Summe über alle k aus K, und für jedes k die Summe über alle l aus L, von real_p[k,l,z]"

**Bedeutet:** Summiere real_p für ALLE Kombinationen von k und l.

Wenn K = {1,2} und L = {A, B}:
```
real_p[1,A,z] + real_p[1,B,z] + real_p[2,A,z] + real_p[2,B,z]
```

---

## 1.2 Der Allquantor (Für alle)

Das Symbol **∀** bedeutet "für alle" oder "für jedes".

### Aufbau:
```
ausdruck  ∀x ∈ M
```

**Bedeutet:** Der Ausdruck muss für JEDES Element x aus der Menge M gelten.

### Beispiel:
```
Σ_{k∈K} a[r,k] = 1   ∀r ∈ R
```

**Gesprochen:** "Die Summe über alle k aus K von a[r,k] ist gleich 1, und das gilt für alle r aus R"

**Bedeutet konkret:** Diese Gleichung muss für JEDE Tour r einzeln erfüllt sein:
- Für Tour t-4: a[t-4,1] + a[t-4,2] + a[t-4,3] + a[t-4,4] + a[t-4,5] = 1
- Für Tour t-5: a[t-5,1] + a[t-5,2] + a[t-5,3] + a[t-5,4] + a[t-5,5] = 1
- Für Tour t-6: a[t-6,1] + a[t-6,2] + a[t-6,3] + a[t-6,4] + a[t-6,5] = 1
- ... und so weiter für alle 20 Touren

---

## 1.3 Das Element-Zeichen

**∈** bedeutet "ist Element von" oder "aus"

### Beispiele:
- `k ∈ K` = "k ist ein Element aus der Menge K" = "k ist einer der LKWs"
- `z ∈ Z` = "z ist ein Zeitintervall"
- `r ∈ R` = "r ist eine Tour"

---

## 1.4 Mengenoperationen

### Vereinigung: ∪
```
TD ∪ TE = {ActrosL} ∪ {eActros600, eActros400} = {ActrosL, eActros600, eActros400}
```
Alle Elemente aus beiden Mengen zusammen.

### Differenz: \
```
Z_night = Z \ Z_day
```
Alle Elemente aus Z, die NICHT in Z_day sind.

Wenn Z = {1,...,96} und Z_day = {25,...,72}, dann:
Z_night = {1,...,24, 73,...,96}

---

## 1.5 Bedingungen in Mengen

```
rAfter[z] = {r ∈ R | s_r(r) > z}
```

**Gesprochen:** "Die Menge aller r aus R, für die gilt: s_r(r) ist grösser als z"

**Der senkrechte Strich |** bedeutet "sodass" oder "für die gilt".

**Beispiel:** Wenn z = 50 und wir haben Touren mit verschiedenen Startzeiten:
- Tour t-4 startet bei Intervall 30 → NICHT in rAfter[50] (30 < 50)
- Tour s-1 startet bei Intervall 60 → IN rAfter[50] (60 > 50)
- Tour w1 startet bei Intervall 80 → IN rAfter[50] (80 > 50)

---

## 1.6 Variablentypen

### Binäre Variable: ∈ {0,1}
```
a[r,k] ∈ {0,1}
```
Kann NUR die Werte 0 oder 1 annehmen. Wie ein Schalter: AN oder AUS.

### Nicht-negative reelle Variable: ≥ 0
```
soc[k,z] ≥ 0
```
Kann jeden Wert ab 0 annehmen (0, 0.5, 1, 100.7, ...)

### Nicht-negative ganze Zahl: ∈ ℕ₀
```
y_l[l] ∈ ℕ₀
```
Kann 0, 1, 2, 3, ... sein (keine Nachkommastellen)

### Positive reelle Zahlen: ∈ ℝ₊
```
dist[r] ∈ ℝ₊
```
Positive reelle Zahlen (grösser als 0)

---

## 1.7 Das vollständige Beispiel lesen

### Die Nebenbedingung NB3:
```
Σ_{z∈Z} end_at[r,z] = 1   ∀r ∈ R
```

**Schritt-für-Schritt übersetzung:**

1. `Σ_{z∈Z}` = "Summiere über alle Zeitintervalle z von 1 bis 96"
2. `end_at[r,z]` = "den Wert von end_at für Tour r im Zeitintervall z"
3. `= 1` = "ergibt genau 1"
4. `∀r ∈ R` = "und das gilt für jede Tour r"

**In Worten:**
"Für jede Tour r muss die Summe aller end_at-Werte über alle Zeitintervalle genau 1 ergeben."

**Was bedeutet das praktisch?**
- end_at[r,z] ist 1, wenn Tour r im Intervall z endet, sonst 0
- Wenn die Summe = 1 sein muss, heisst das: genau EIN Zeitintervall hat den Wert 1
- Also: Jede Tour endet genau einmal (nicht null mal, nicht zweimal)

**Konkret für Tour "t-4":**
```
end_at[t-4,1] + end_at[t-4,2] + ... + end_at[t-4,96] = 1
```
Nur EINER dieser 96 Werte ist 1, alle anderen sind 0.

---

# 2. WAS IST MILP?

## 2.1 Definition

**MILP** = **M**ixed **I**nteger **L**inear **P**rogram (Gemischt-ganzzahlige lineare Optimierung)

### Bestandteile:
- **Mixed Integer**: Mischung aus ganzzahligen (0, 1, 2, ...) und kontinuierlichen (0.5, 1.7, ...) Variablen
- **Linear**: Alle Gleichungen und Ungleichungen sind linear (keine x², keine x·y)
- **Program**: Optimierungsproblem mit Zielfunktion

## 2.2 Struktur eines MILP

```
MINIMIERE:    Zielfunktion (z.B. Gesamtkosten)
UNTER:        Nebenbedingung 1
              Nebenbedingung 2
              ...
              Nebenbedingung n
```

## 2.3 Warum MILP für dieses Problem?

Dieses Modell optimiert eine **LKW-Flotte** mit:
- **Ganzzahlige Entscheidungen**: Welcher LKW fährt welche Tour? (Ja/Nein = 0/1)
- **Kontinuierliche Werte**: Wie viel kW wird geladen? Wie voll ist der Akku?
- **Lineare Kosten**: Dieselkosten = Preis × Menge (linear)

---

# 3. INDEXMENGEN IM DETAIL

Indexmengen definieren, WORüBER wir optimieren. Sie sind wie "Dimensionen" des Problems.

## 3.1 R - Menge der Touren

```
R = {t-4, t-5, t-6, s-1, s-2, s-3, s-4, w1, w2, w3, w4, w5, w6, w7, r1, r2, r3, h3, h4, k1}
```

**Was ist das?**
Eine Liste aller 20 Touren, die gefahren werden müssen.

**Namenskonvention (vermutlich):**
- `t-X` = Tagestouren
- `s-X` = Spätschicht-Touren
- `w-X` = Wochentouren oder bestimmte Routen
- `r-X` = Regelmässige Touren
- `h-X` = Spezielle Touren
- `k1` = Einzelne Tour

**Wie wird es verwendet?**
Jedes Mal wenn `∀r ∈ R` steht, wird die Bedingung für alle 20 Touren geprüft.

---

## 3.2 K - Menge der LKWs

```
K = {1, 2, 3, 4, 5}
```

**Was ist das?**
Die 5 verfügbaren LKWs, nummeriert von 1 bis 5.

**Wichtig:** Das Modell entscheidet, welcher LKW welchen TYP bekommt (Diesel oder Elektro).

---

## 3.3 TD - Menge der Diesel-LKW-Typen

```
TD = {ActrosL}
```

**Was ist das?**
Nur ein Diesel-Typ verfügbar: Mercedes Actros L

**Eigenschaften:**
- Verbraucht Diesel
- Zahlt Maut
- Zahlt KFZ-Steuer
- Kann NICHT geladen werden

---

## 3.4 TE - Menge der Elektro-LKW-Typen

```
TE = {eActros600, eActros400}
```

**Was ist das?**
Zwei E-LKW-Typen:
- **eActros600**: Grössere Batterie (600 kWh)
- **eActros400**: Kleinere Batterie (400 kWh)

**Eigenschaften:**
- Brauchen Strom statt Diesel
- Müssen geladen werden
- Bekommen THG-Prämie (Erlöse)
- Keine Maut, keine KFZ-Steuer

---

## 3.5 T - Alle LKW-Typen (abgeleitet)

```
T = TD ∪ TE = {ActrosL, eActros600, eActros400}
```

Alle drei Typen zusammen.

---

## 3.6 L - Menge der Ladesäulentypen

```
L = {Alpitronic-50, Alpitronic-200, Alpitronic-400}
```

**Was ist das?**
Drei verschiedene Ladesäulen-Modelle mit unterschiedlichen Leistungen:
- **Alpitronic-50**: 50 kW Ladeleistung (langsam, günstig)
- **Alpitronic-200**: 200 kW Ladeleistung (mittel)
- **Alpitronic-400**: 400 kW Ladeleistung (schnell, teuer)

---

## 3.7 Z - Zeitintervalle

```
Z = {1, 2, 3, ..., 96}
```

**Was ist das?**
Der Tag wird in 96 Intervalle zu je 15 Minuten unterteilt.

**Berechnung:**
- 24 Stunden × 4 Viertelstunden = 96 Intervalle
- Intervall 1 = 00:00 - 00:15 Uhr
- Intervall 2 = 00:15 - 00:30 Uhr
- ...
- Intervall 25 = 06:00 - 06:15 Uhr
- ...
- Intervall 96 = 23:45 - 24:00 Uhr

**Umrechnung Intervall → Uhrzeit:**
```
hour(z) = (z - 1) × 0.25 Stunden
```

**Beispiele:**
- z = 1: (1-1) × 0.25 = 0.00 Uhr = 00:00
- z = 25: (25-1) × 0.25 = 6.00 Uhr = 06:00
- z = 49: (49-1) × 0.25 = 12.00 Uhr = 12:00
- z = 73: (73-1) × 0.25 = 18.00 Uhr = 18:00

---

## 3.8 Z_day - Tagzeit-Intervalle

```
Z_day = {25, 26, 27, ..., 72}
```

**Was ist das?**
Die Intervalle während der Tagzeit (06:00 bis 17:45 Uhr).

**Berechnung:**
- Start: Intervall 25 = 06:00 Uhr
- Ende: Intervall 72 = 17:45 Uhr
- 72 - 25 + 1 = 48 Intervalle = 12 Stunden

---

## 3.9 Z_night - Nachtzeit-Intervalle

```
Z_night = Z \ Z_day = {1, ..., 24, 73, ..., 96}
```

**Was ist das?**
Alle Intervalle AUSSER der Tagzeit.

**Zeitraum:**
- 00:00 - 05:45 Uhr (Intervalle 1-24)
- 18:00 - 23:45 Uhr (Intervalle 73-96)

**Wichtig für:**
- Nacht-Ladelogik
- E-LKWs sollen nachts angesteckt bleiben

---

## 3.10 rAfter[z] - Touren nach Zeitpunkt z

```
rAfter[z] = {r ∈ R | s_r(r) > z}
```

**Was ist das?**
Eine DYNAMISCHE Menge: Alle Touren, die NACH dem Zeitpunkt z starten.

**Beispiel:**
Angenommen wir haben Touren mit diesen Startintervallen:
- Tour t-4: startet bei z = 28 (07:00)
- Tour s-1: startet bei z = 60 (15:00)
- Tour w1: startet bei z = 80 (20:00)

Dann ist:
- rAfter[25] = {t-4, s-1, w1} (alle starten nach 06:00)
- rAfter[30] = {s-1, w1} (nur s-1 und w1 starten nach 07:30)
- rAfter[70] = {w1} (nur w1 startet nach 17:30)
- rAfter[85] = {} (keine Tour startet nach 21:15)

**Verwendung:**
Wird benutzt um zu prüfen, ob ein LKW noch zukünftige Touren hat.

---

# 4. PARAMETER IM DETAIL

Parameter sind FESTE WERTE, die nicht vom Solver optimiert werden. Sie sind Eingabedaten.

## 4.1 Tourenparameter

### dist[r] - Gesamtdistanz
```
dist[r] ∈ ℝ₊   (positive reelle Zahl)
```

**Bedeutung:** Wie viele Kilometer ist Tour r lang?

**Beispiel:**
- dist[t-4] = 120 (Tour t-4 ist 120 km lang)
- dist[w1] = 250 (Tour w1 ist 250 km lang)

**Verwendet für:**
- Berechnung Energieverbrauch (km × kWh/km)
- Berechnung Dieselverbrauch (km × Liter/km)

---

### mDist[r] - Mautpflichtige Distanz
```
mDist[r] ∈ ℝ₊
```

**Bedeutung:** Wie viele Kilometer der Tour sind mautpflichtig (Autobahn)?

**Beispiel:**
- dist[t-4] = 120 km gesamt
- mDist[t-4] = 80 km davon auf der Autobahn

**Verwendet für:**
- Berechnung Mautkosten (nur für Diesel-LKWs)

---

### start[r] und end[r] - Uhrzeiten
```
start[r], end[r]   (nur Eingabedaten)
```

**Bedeutung:** Wann beginnt und endet die Tour (als Uhrzeit)?

**Beispiel:**
- start[t-4] = "07:15"
- end[t-4] = "12:30"

**Hinweis:** Diese werden in Intervalle umgerechnet (s_r, e_r).

---

### s_r(r) und e_r(r) - Start- und Endintervall
```
s_r(r) ∈ Z   (Zahl zwischen 1 und 96)
e_r(r) ∈ Z
```

**Bedeutung:** In welchem 15-Minuten-Intervall beginnt/endet die Tour?

**Beispiel:**
- Tour startet um 07:15 → s_r = 30 (weil (30-1)×0.25 = 7.25 Stunden = 07:15)
- Tour endet um 12:30 → e_r = 51 (weil (51-1)×0.25 = 12.5 Stunden = 12:30)

---

### dur_z[r] - Tourdauer in Intervallen
```
dur_z[r] = e_r(r) - s_r(r)
```

**Bedeutung:** Wie viele Zeitintervalle dauert die Tour?

**Beispiel:**
- s_r = 30, e_r = 51
- dur_z = 51 - 30 = 21 Intervalle = 21 × 15 min = 315 min = 5.25 Stunden

---

### start_at[r,z] - Startet Tour r im Intervall z?
```
start_at[r,z] ∈ {0, 1}
```

**Bedeutung:**
- start_at[r,z] = 1, wenn Tour r GENAU im Intervall z startet
- start_at[r,z] = 0, sonst

**Beispiel:** Tour t-4 startet in Intervall 30
```
start_at[t-4, 29] = 0  (startet nicht in 29)
start_at[t-4, 30] = 1  (startet in 30!)
start_at[t-4, 31] = 0  (startet nicht in 31)
```

**Eigenschaft:** Für jede Tour r ist genau EIN start_at-Wert = 1, alle anderen = 0.

---

### end_at[r,z] - Endet Tour r im Intervall z?
```
end_at[r,z] ∈ {0, 1}
```

**Bedeutung:** Analog zu start_at, aber für das Ende.

---

### active[r,z] - Ist Tour r im Intervall z aktiv?
```
active[r,z] ∈ {0, 1}
= 1 genau dann wenn s_r(r) ≤ z < e_r(r)
```

**Bedeutung:** Fährt der LKW gerade diese Tour?

**Beispiel:** Tour mit s_r = 30, e_r = 51
```
active[r, 29] = 0  (Tour hat noch nicht begonnen)
active[r, 30] = 1  (Tour läuft)
active[r, 40] = 1  (Tour läuft)
active[r, 50] = 1  (Tour läuft)
active[r, 51] = 0  (Tour ist beendet - beachte: z < e_r, nicht ≤)
active[r, 52] = 0  (Tour ist beendet)
```

**Wichtig:** Das Endintervall selbst ist NICHT mehr aktiv (z < e_r, nicht z ≤ e_r).

---

## 4.2 Diesel-LKW-Parameter

### cap_d[type] - Leasingkosten
```
cap_d[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Leasingkosten für einen Diesel-LKW des Typs.

**Beispiel:**
- cap_d[ActrosL] = 25000 (25.000 EUR/Jahr Leasing)

---

### opx_d[type] - Wartungskosten
```
opx_d[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Wartungs- und Instandhaltungskosten.

---

### kfz_d[type] - KFZ-Steuer
```
kfz_d[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche KFZ-Steuer (nur für Diesel!).

**Hinweis:** E-LKWs sind von der KFZ-Steuer befreit, daher gibt es kein kfz_e.

---

### avgDv_d[type] - Durchschnittsverbrauch Diesel
```
avgDv_d[type] ∈ ℝ₊   (Liter pro 100 km)
```

**Bedeutung:** Wie viel Diesel verbraucht der LKW auf 100 km?

**Beispiel:**
- avgDv_d[ActrosL] = 32 (32 Liter / 100 km)

**Verwendung:**
```
Dieselverbrauch für Tour r = dist[r] / 100 × avgDv_d[type]
```

---

### c_diesel - Dieselpreis
```
c_diesel = 1.68   (Euro pro Liter)
```

**Bedeutung:** Festgelegter Dieselpreis.

---

### c_m_d - Mautkosten
```
c_m_d = 0.34   (Euro pro km)
```

**Bedeutung:** Mautgebühr pro gefahrenem Autobahnkilometer.

**Hinweis:** Nur Diesel-LKWs zahlen Maut (E-LKWs sind befreit).

---

## 4.3 Elektro-LKW-Parameter

### cap_e[type] - Leasingkosten E-LKW
```
cap_e[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Leasingkosten.

**Typisch:** E-LKWs sind teurer als Diesel-LKWs.

---

### opx_e[type] - Wartungskosten E-LKW
```
opx_e[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Wartungskosten.

**Typisch:** Oft niedriger als bei Diesel (weniger bewegliche Teile).

---

### avgEv_e[type] - Energieverbrauch
```
avgEv_e[type] ∈ ℝ₊   (kWh pro km)
```

**Bedeutung:** Wie viel Strom verbraucht der E-LKW pro Kilometer?

**Beispiel:**
- avgEv_e[eActros600] = 1.2 (1.2 kWh/km)
- avgEv_e[eActros400] = 1.1 (1.1 kWh/km - leichter, effizienter)

---

### soc_e[type] - Batteriekapazität
```
soc_e[type] ∈ ℝ₊   (kWh)
```

**Bedeutung:** Maximale Batteriekapazität des E-LKW-Typs.

**Beispiel:**
- soc_e[eActros600] = 600 kWh
- soc_e[eActros400] = 400 kWh

**Verwendung:**
- Bestimmt maximale Reichweite
- Begrenzt, wie voll der Akku sein kann (SOC-Obergrenze)

---

### max_p_e[type] - Maximale Ladeleistung des LKW
```
max_p_e[type] ∈ ℝ₊   (kW)
```

**Bedeutung:** Mit wie viel kW kann der LKW maximal geladen werden?

**Beispiel:**
- max_p_e[eActros600] = 400 kW
- max_p_e[eActros400] = 300 kW
- max_p_e[ActrosL] = 0 kW (Diesel kann nicht laden!)

**Wichtiger Trick:** max_p_e[ActrosL] = 0 verhindert, dass Diesel-LKWs "versehentlich" laden.

---

### thg_e[type] - THG-Erlöse
```
thg_e[type] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Treibhausgasminderungs-Quote-Erlöse (Förderung für E-Fahrzeuge).

**Beispiel:**
- thg_e[eActros600] = 3500 EUR/Jahr
- thg_e[eActros400] = 2800 EUR/Jahr

**Verwendung:** Wird von den Gesamtkosten ABGEZOGEN (Einnahme!).

---

## 4.4 Ladesäulenparameter

### cap_l[l] - Leasingkosten Ladesäule
```
cap_l[l] ∈ ℝ₊   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Kosten für eine Ladesäule des Typs l.

**Beispiel:**
- cap_l[Alpitronic-50] = 2000 EUR/Jahr
- cap_l[Alpitronic-200] = 5000 EUR/Jahr
- cap_l[Alpitronic-400] = 10000 EUR/Jahr

---

### opx_l[l] - Wartungskosten Ladesäule
```
opx_l[l] ∈ ℝ₊   (Euro pro Jahr)
```

---

### max_p_l[l] - Maximale Ladeleistung der Säule
```
max_p_l[l] ∈ ℝ₊   (kW)
```

**Bedeutung:** Wie viel Leistung kann die Säule maximal abgeben?

**Beispiel:**
- max_p_l[Alpitronic-50] = 50 kW
- max_p_l[Alpitronic-200] = 200 kW
- max_p_l[Alpitronic-400] = 400 kW

---

### cs_l[l] - Ladepunkte pro Säule
```
cs_l[l] ∈ ℕ   (natürliche Zahl)
```

**Bedeutung:** Wie viele LKWs können gleichzeitig an einer Säule laden?

**Beispiel:**
- cs_l[Alpitronic-50] = 2 (zwei Ladepunkte)
- cs_l[Alpitronic-200] = 2
- cs_l[Alpitronic-400] = 1 (nur ein Ladepunkt)

**Hinweis:** Mehr Ladepunkte teilen sich die Gesamtleistung!

---

### Nmax - Maximale Anzahl Säulen
```
Nmax = 3
```

**Bedeutung:** Maximal 3 Ladesäulen pro Typ können installiert werden.

---

## 4.5 Netz- und Speicherparameter

### p_grid_max - Netzanschlussleistung
```
p_grid_max = 500   (kW)
```

**Bedeutung:** Maximale Leistung, die aus dem Netz bezogen werden kann OHNE Trafo.

**Mit Trafo:** p_grid_max + 500 = 1000 kW möglich.

---

### capP_s - Kosten Speicherleistung
```
capP_s = 30   (Euro pro kW pro Jahr)
```

**Bedeutung:** Was kostet 1 kW Speicherleistung pro Jahr?

**Beispiel:** 100 kW Speicher kosten 100 × 30 = 3000 EUR/Jahr (nur Leistungskomponente).

---

### capQ_s - Kosten Speicherkapazität
```
capQ_s = 350   (Euro pro kWh pro Jahr)
```

**Bedeutung:** Was kostet 1 kWh Speicherkapazität pro Jahr?

**Beispiel:** 200 kWh Speicher kosten 200 × 350 = 70.000 EUR/Jahr (nur Kapazitätskomponente).

---

### opx_s - OPEX-Faktor Speicher
```
opx_s = 0.02   (2%)
```

**Bedeutung:** Wartungskosten sind 2% der Investitionskosten.

---

### nrt - Round-Trip-Effizienz
```
nrt = 0.98   (98%)
```

**Bedeutung:** Beim Entladen gehen 2% Energie verloren.

**Berechnung:**
- Laden: 100 kWh rein
- Speichern: 100 kWh gespeichert
- Entladen: 100 × 0.98 = 98 kWh raus (2 kWh Verlust)

---

### dod - Depth of Discharge
```
dod = 0.025   (2.5%)
```

**Bedeutung:** Der Speicher muss immer mindestens 2.5% gefüllt sein.

**Beispiel:**
- 100 kWh Speicher
- Mindestfüllung: 100 × 0.025 = 2.5 kWh
- Nutzbare Kapazität: 100 - 2.5 = 97.5 kWh

---

### c_e - Arbeitspreis Strom
```
c_e = 0.25   (Euro pro kWh)
```

**Bedeutung:** Preis pro verbrauchter kWh Strom.

---

### c_gr - Grundgebühr Strom
```
c_gr = 1000   (Euro pro Jahr)
```

**Bedeutung:** Jährliche Grundgebühr für den Stromanschluss.

---

### cPeak - Leistungspreis
```
cPeak = 150   (Euro pro kW pro Jahr)
```

**Bedeutung:** Kosten für die maximale Leistungsspitze.

**Beispiel:** Wenn die höchste Leistungsaufnahme 200 kW ist:
200 × 150 = 30.000 EUR/Jahr Leistungskosten

**Wichtig:** Anreiz, Lastspitzen zu vermeiden!

---

### delta_t - Intervalldauer
```
delta_t = 0.25   (Stunden = 15 Minuten)
```

**Bedeutung:** Ein Zeitintervall dauert 0.25 Stunden.

**Verwendung:**
```
Energie = Leistung × Zeit
E = P × delta_t
E = 100 kW × 0.25 h = 25 kWh
```

---

### z6 - Intervall für 06:00 Uhr
```
z6 = 25
```

**Bedeutung:** Das Intervall 25 entspricht 06:00 Uhr.

**Verwendung:** Wichtig für die Nacht-Lade-Logik (darf erst um 06:00 ausstecken).

---

## 4.6 Big-M-Parameter

### M - Grosse Zahl
```
M = 10000
```

**Was ist Big-M?**
Eine Hilfszahl für logische Bedingungen in linearen Programmen.

**Warum braucht man das?**
MILP kann nur lineare Gleichungen. Für WENN-DANN-Logik braucht man einen Trick:

**Beispiel:** "Wenn x = 1, dann muss y ≤ 5"

Ohne Big-M: Nicht linear darstellbar.

Mit Big-M:
```
y ≤ 5 + M × (1 - x)
```

- Wenn x = 1: y ≤ 5 + 10000 × 0 = 5 ✓ (Bedingung aktiv)
- Wenn x = 0: y ≤ 5 + 10000 × 1 = 10005 (immer erfüllt, Bedingung "ausgeschaltet")

---

## 4.7 Abgeleitete Parameter

### e_bedarf_r[r,k] - Energiebedarf für Tour
```
e_bedarf_r[r,k] = dist[r] × avgEv_e[type_k[k]]
```

**Bedeutung:** Wie viel Energie braucht LKW k für Tour r?

**Beispiel:**
- dist[t-4] = 120 km
- LKW k ist ein eActros600 mit avgEv_e = 1.2 kWh/km
- e_bedarf_r[t-4, k] = 120 × 1.2 = 144 kWh

**Wichtig:** Nur für E-LKWs definiert!

---

### unplug_ok[z] - Darf abgesteckt werden?
```
unplug_ok[z] ∈ {0, 1}
```

**Regel:**
- unplug_ok[z] = 1, wenn z ∈ Z_day (Tagzeit: darf ausstecken)
- unplug_ok[z] = 1, wenn z+1 = z6 (kurz vor 06:00: darf ausstecken)
- unplug_ok[z] = 0, wenn z ∈ Z_night und z+1 ≠ z6 (Nacht: muss angesteckt bleiben)

**Sinn:** LKWs sollen nachts angesteckt bleiben (Netzstabilisierung, gleichmässiges Laden).

---

# 5. ENTSCHEIDUNGSVARIABLEN IM DETAIL

Entscheidungsvariablen sind die Werte, die der Solver OPTIMIERT. Sie sind die "Antworten" des Modells.

## 5.1 Zuordnung & Bewegung

### a[r,k] - Tour-LKW-Zuordnung
```
a[r,k] ∈ {0,1}   ∀r ∈ R, ∀k ∈ K
```

**Dimension:** 20 Touren × 5 LKWs = 100 Variablen

**Bedeutung:**
- a[r,k] = 1: Tour r wird von LKW k gefahren
- a[r,k] = 0: Tour r wird NICHT von LKW k gefahren

**Beispiel:**
```
a[t-4, 1] = 1  → LKW 1 fährt Tour t-4
a[t-4, 2] = 0  → LKW 2 fährt NICHT Tour t-4
a[t-4, 3] = 0
a[t-4, 4] = 0
a[t-4, 5] = 0
```

**Constraint:** Genau ein LKW pro Tour (Σ_k a[r,k] = 1).

---

### depart[k,z] - Abfahrt
```
depart[k,z] ∈ {0,1}   ∀k ∈ K, ∀z ∈ Z
```

**Dimension:** 5 LKWs × 96 Intervalle = 480 Variablen

**Bedeutung:**
- depart[k,z] = 1: LKW k fährt im Intervall z zu einer Tour los
- depart[k,z] = 0: LKW k fährt NICHT im Intervall z los

**Berechnung (NB6):**
```
depart[k,z] = Σ_{r∈R} start_at[r,z] × a[r,k]
```

Das heisst: depart ist 1, wenn irgendeine Tour, die diesem LKW zugeordnet ist, in diesem Intervall startet.

---

### arrive[k,z] - Ankunft
```
arrive[k,z] ∈ {0,1}   ∀k ∈ K, ∀z ∈ Z
```

**Bedeutung:** LKW k kommt im Intervall z von einer Tour zurück.

**Berechnung (NB7):**
```
arrive[k,z] = Σ_{r∈R} end_at[r,z] × a[r,k]
```

---

### has_future[k,z] - Hat zukünftige Touren
```
has_future[k,z] ∈ {0,1}   ∀k ∈ K, ∀z ∈ Z_night
```

**Dimension:** 5 LKWs × 48 Nacht-Intervalle = 240 Variablen

**Bedeutung:**
- has_future[k,z] = 1: LKW k hat noch mindestens eine Tour NACH Zeitpunkt z
- has_future[k,z] = 0: LKW k hat keine weiteren Touren mehr

**Verwendung:** Wichtig für die Nacht-Lade-Logik - wenn der LKW keine Touren mehr hat, muss er nicht mehr voll geladen werden.

---

### next[r,k,z] - Nächste Tour
```
next[r,k,z] ∈ {0,1}   ∀r ∈ R, ∀k ∈ K, ∀z ∈ Z_night
```

**Dimension:** 20 × 5 × 48 = 4800 Variablen

**Bedeutung:**
- next[r,k,z] = 1: Tour r ist die NäCHSTE Tour von LKW k nach Zeitpunkt z
- next[r,k,z] = 0: Tour r ist NICHT die nächste Tour

**Beispiel:** LKW 1 fährt Touren t-4 (startet 08:00), s-1 (startet 15:00), w1 (startet 22:00)

Im Intervall z = 20 (05:00 Uhr):
- next[t-4, 1, 20] = 1 (t-4 ist die nächste Tour)
- next[s-1, 1, 20] = 0
- next[w1, 1, 20] = 0

Im Intervall z = 50 (12:30 Uhr):
- next[t-4, 1, 50] = 0 (t-4 ist schon vorbei)
- next[s-1, 1, 50] = 1 (s-1 ist jetzt die nächste)
- next[w1, 1, 50] = 0

---

## 5.2 Lade-Variablen

### assign[k,l,z] - Aktives Laden
```
assign[k,l,z] ∈ {0,1}   ∀k ∈ K, ∀l ∈ L, ∀z ∈ Z
```

**Dimension:** 5 × 3 × 96 = 1440 Variablen

**Bedeutung:**
- assign[k,l,z] = 1: LKW k lädt AKTIV an Säulentyp l im Intervall z
- assign[k,l,z] = 0: LKW k lädt NICHT an Säulentyp l im Intervall z

**Unterschied zu plug:** assign = aktives Laden, plug = nur angesteckt.

---

### plug[k,l,z] - Angesteckt
```
plug[k,l,z] ∈ {0,1}   ∀k ∈ K, ∀l ∈ L, ∀z ∈ Z
```

**Bedeutung:**
- plug[k,l,z] = 1: LKW k ist an Säulentyp l angesteckt (physische Verbindung)
- plug[k,l,z] = 0: LKW k ist NICHT angesteckt

**Wichtig:**
- Ein LKW kann angesteckt sein, ohne aktiv zu laden (plug=1, assign=0)
- Ein LKW kann nur laden, wenn er angesteckt ist (assign ≤ plug)

**Anwendung:** Nachts sollen LKWs angesteckt bleiben, auch wenn der Akku voll ist.

---

### real_p[k,l,z] - Tatsächliche Ladeleistung
```
real_p[k,l,z] ≥ 0   ∀k ∈ K, ∀l ∈ L, ∀z ∈ Z
```

**Bedeutung:** Mit wie viel kW wird LKW k an Säule l im Intervall z tatsächlich geladen?

**Typ:** Kontinuierliche Variable (kann 0, 50.5, 123.7, ... sein)

**Grenzen:**
- Maximal: min(max_p_e[type], max_p_l[l]) - das Minimum von LKW und Säule
- Nur wenn assign = 1

**Beispiel:**
- LKW kann max 400 kW
- Säule kann max 200 kW
- → real_p kann maximal 200 kW sein

---

### y_l[l] - Anzahl Ladesäulen
```
y_l[l] ∈ ℕ₀   ∀l ∈ L
```

**Dimension:** 3 Variablen (eine pro Säulentyp)

**Bedeutung:** Wie viele Ladesäulen vom Typ l sollen installiert werden?

**Grenzen:** 0 ≤ y_l[l] ≤ Nmax = 3

**Beispiel optimales Ergebnis:**
- y_l[Alpitronic-50] = 0 (keine langsamen Säulen)
- y_l[Alpitronic-200] = 2 (zwei mittlere Säulen)
- y_l[Alpitronic-400] = 1 (eine schnelle Säule)

---

## 5.3 Energiezustände

### soc[k,z] - State of Charge (Batterieladezustand)
```
soc[k,z] ≥ 0   ∀k ∈ K mit type_k[k] ∈ TE, ∀z ∈ Z
```

**Bedeutung:** Wie voll ist der Akku von E-LKW k im Intervall z? (in kWh)

**Typ:** Kontinuierliche Variable

**Grenzen:**
- Minimum: 0 kWh (leer)
- Maximum: soc_e[type] (z.B. 600 kWh für eActros600)

**Wichtig:** Nur für E-LKWs definiert! Diesel-LKWs haben keinen SOC.

---

### need_charge[k,z] - Muss laden
```
need_charge[k,z] ∈ {0,1}   ∀k ∈ K mit type_k[k] ∈ TE, ∀z ∈ Z_night
```

**Bedeutung:**
- need_charge[k,z] = 1: LKW k MUSS im Intervall z geladen werden
- need_charge[k,z] = 0: Kein Ladebedarf

**Berechnung:** need_charge = 1 - enough (Gegenteil von "genug Energie")

---

### enough[k,z] - Genug Energie
```
enough[k,z] ∈ {0,1}   ∀k ∈ K mit type_k[k] ∈ TE, ∀z ∈ Z_night
```

**Bedeutung:**
- enough[k,z] = 1: Der aktuelle SOC reicht für die nächste Tour
- enough[k,z] = 0: Der SOC reicht NICHT für die nächste Tour

---

## 5.4 Speicherbetrieb

### p_s - Speicherleistung
```
p_s ≥ 0   (kW)
```

**Bedeutung:** Wie viel Leistung kann der stationäre Speicher aufnehmen/abgeben?

**Beispiel:** p_s = 100 bedeutet, der Speicher kann mit 100 kW laden und mit 100 kW entladen.

---

### q_s - Speicherkapazität
```
q_s ≥ 0   (kWh)
```

**Bedeutung:** Wie viel Energie kann der Speicher speichern?

**Beispiel:** q_s = 200 bedeutet 200 kWh Kapazität.

**Hinweis:** Nutzbare Kapazität = q_s × (1 - dod) = 200 × 0.975 = 195 kWh

---

### p_l_s[z] - Speicher lädt
```
p_l_s[z] ≥ 0   ∀z ∈ Z   (kW)
```

**Bedeutung:** Mit wie viel kW lädt der Speicher im Intervall z aus dem Netz?

---

### p_e_s[z] - Speicher entlädt
```
p_e_s[z] ≥ 0   ∀z ∈ Z   (kW)
```

**Bedeutung:** Mit wie viel kW entlädt der Speicher im Intervall z?

---

### soc_s[z] - Speicher-Füllstand
```
soc_s[z] ≥ 0   ∀z ∈ Z   (kWh)
```

**Bedeutung:** Wie voll ist der stationäre Speicher im Intervall z?

**Grenzen:**
- Minimum: dod × q_s (z.B. 2.5% von 200 = 5 kWh)
- Maximum: q_s (z.B. 200 kWh)

---

### mode_s[z] - Speichermodus
```
mode_s[z] ∈ {0,1}   ∀z ∈ Z
```

**Bedeutung:**
- mode_s[z] = 1: Speicher ist im LADEMODUS
- mode_s[z] = 0: Speicher ist im ENTLADEMODUS

**Sinn:** Der Speicher kann nicht gleichzeitig laden UND entladen.

---

## 5.5 Netz-Variablen

### p_grid[z] - Netzbezug
```
p_grid[z] ≥ 0   ∀z ∈ Z   (kW)
```

**Bedeutung:** Wie viel Leistung wird im Intervall z aus dem Stromnetz bezogen?

**Berechnung (NB37):**
```
p_grid[z] = (Summe aller Ladeloistungen) + (Speicher laden) - (Speicher entladen)
```

---

### p_peak - Leistungsspitze
```
p_peak ≥ 0   (kW)
```

**Bedeutung:** Die HöCHSTE Netzbezugsleistung über alle Intervalle.

**Constraint (NB39):** p_grid[z] ≤ p_peak für alle z

**Sinn:** Diese Variable bestimmt die Leistungskosten. Anreiz: Lastspitzen vermeiden!

---

### u - Trafo-Entscheidung
```
u ∈ {0,1}
```

**Bedeutung:**
- u = 1: Ein Transformator wird installiert (erlaubt mehr Leistung)
- u = 0: Kein Trafo (max 500 kW)

**Kosten:** 10.000 EUR/Jahr wenn u = 1

**Vorteil:** Mit Trafo: bis zu 1000 kW Netzbezug möglich.

---

# 6. BERECHNETE VARIABLEN

Diese Variablen werden aus anderen Variablen BERECHNET, nicht direkt optimiert.

## 6.1 cons[k,z] - Verbrauch während Fahrt

```
cons[k,z] = Σ_{r∈R} active[r,z] × a[r,k] × (dist[r] × avgEv_e[type_k[k]] / dur_z[r])
```

**Für Diesel-LKWs:** cons[k,z] = 0 (kein Stromverbrauch)

**Bedeutung:** Wie viel Strom verbraucht E-LKW k im Intervall z während der Fahrt?

**Aufschlüsselung:**
- `active[r,z]` = 1 wenn Tour r gerade läuft
- `a[r,k]` = 1 wenn LKW k die Tour fährt
- `dist[r] × avgEv_e[type]` = Gesamtenergiebedarf der Tour
- `/ dur_z[r]` = aufgeteilt auf die Anzahl Intervalle

**Beispiel:**
- Tour ist 120 km, Verbrauch 1.2 kWh/km → 144 kWh gesamt
- Tour dauert 20 Intervalle
- Verbrauch pro Intervall: 144 / 20 = 7.2 kW

---

## 6.2 e_next[k,z] - Energiebedarf nächste Tour

```
e_next[k,z] = Σ_{r∈rAfter[z]} next[r,k,z] × e_bedarf_r[r,k]
```

**Bedeutung:** Wie viel Energie braucht LKW k für seine NäCHSTE Tour nach Zeitpunkt z?

**Berechnung:**
- next[r,k,z] ist 1 für genau eine Tour (die nächste)
- e_bedarf_r[r,k] ist der Energiebedarf dieser Tour
- Die Summe ergibt genau diesen einen Wert

**Verwendung:** Entscheidet, ob der LKW genug Energie hat (enough-Variable).

---

# 7. NEBENBEDINGUNGEN IM DETAIL

Nebenbedingungen (NB) sind Regeln, die das Modell einhalten MUSS.

## 7.1 Tour-Zuordnung

### NB1: Jede Tour genau einem LKW

```
Σ_{k∈K} a[r,k] = 1   ∀r ∈ R
```

**Gesprochen:** "Die Summe über alle LKWs k von a[r,k] ist gleich 1, für jede Tour r"

**Bedeutung:** Jede Tour wird genau EINEM LKW zugeordnet - nicht null, nicht zwei.

**Beispiel für Tour t-4:**
```
a[t-4,1] + a[t-4,2] + a[t-4,3] + a[t-4,4] + a[t-4,5] = 1
```
Genau einer dieser fünf Werte ist 1, die anderen sind 0.

---

### NB2: Jede Tour startet genau einmal

```
Σ_{z∈Z} start_at[r,z] = 1   ∀r ∈ R
```

**Bedeutung:** Jede Tour hat genau EINEN Startzeitpunkt.

**Hinweis:** start_at ist ein Parameter (nicht Variable), daher ist das eine Datenkonsistenzprüfung.

---

### NB3: Jede Tour endet genau einmal

```
Σ_{z∈Z} end_at[r,z] = 1   ∀r ∈ R
```

**Analog zu NB2.**

---

## 7.2 LKW-Bewegungslogik

### NB4: Keine zwei Touren gleichzeitig

```
Σ_{r∈R} active[r,z] × a[r,k] ≤ 1   ∀k ∈ K, ∀z ∈ Z
```

**Gesprochen:** "Für jeden LKW k und jedes Zeitintervall z: Die Anzahl der aktiven Touren, die diesem LKW zugeordnet sind, ist höchstens 1"

**Bedeutung:** Ein LKW kann nicht zwei Touren GLEICHZEITIG fahren.

**Aufschlüsselung:**
- `active[r,z]` = 1 wenn Tour r gerade läuft
- `a[r,k]` = 1 wenn Tour r dem LKW k zugeordnet ist
- Das Produkt ist nur 1, wenn beides zutrifft
- Die Summe zählt, wie viele Touren LKW k gerade fährt
- ≤ 1 heisst: höchstens eine

---

### NB5: Kein gleichzeitiges Ankommen

```
Σ_{r∈R} end_at[r,z] × a[r,k] ≤ 1   ∀k ∈ K, ∀z ∈ Z
```

**Bedeutung:** Ein LKW kann nicht zwei Touren im selben Intervall beenden.

---

### NB6: Definition depart

```
depart[k,z] = Σ_{r∈R} start_at[r,z] × a[r,k]   ∀k ∈ K, ∀z ∈ Z
```

**Bedeutung:** depart[k,z] = 1 genau dann, wenn LKW k eine Tour hat, die in z startet.

**Beispiel:**
- start_at[t-4, 30] = 1 (Tour t-4 startet in Intervall 30)
- a[t-4, 1] = 1 (Tour t-4 ist LKW 1 zugeordnet)
- → depart[1, 30] = 1 × 1 = 1

---

### NB7: Definition arrive

```
arrive[k,z] = Σ_{r∈R} end_at[r,z] × a[r,k]   ∀k ∈ K, ∀z ∈ Z
```

**Analog zu NB6 für die Ankunft.**

---

## 7.3 Zukunftstouren-Logik

Diese Nebenbedingungen bestimmen, ob ein LKW noch Touren vor sich hat.

### NB8 & NB9: has_future korrekt setzen

```
has_future[k,z] ≤ Σ_{r∈rAfter[z]} a[r,k]   (NB8)
Σ_{r∈rAfter[z]} a[r,k] ≥ has_future[k,z]   (NB9)
```

**Kombinierte Bedeutung:**
- has_future = 1 genau dann, wenn mindestens eine Tour nach z existiert
- has_future = 0 genau dann, wenn keine Tour nach z existiert

---

### NB10: Obere Schranke

```
Σ_{r∈rAfter[z]} a[r,k] ≤ |rAfter[z]| × has_future[k,z]
```

**Bedeutung:** Wenn has_future = 0, dann darf keine Tour nach z zugeordnet sein.

**Erklärung:**
- |rAfter[z]| = Anzahl der Touren, die nach z starten könnten
- Wenn has_future = 0: rechte Seite = 0, also müssen alle a[r,k] = 0 sein
- Wenn has_future = 1: rechte Seite = |rAfter[z]|, Constraint ist immer erfüllt

---

### NB11: Genau eine nächste Tour

```
Σ_{r∈rAfter[z]} next[r,k,z] = arrive[k,z] × has_future[k,z]
```

**Bedeutung:**
- Wenn LKW k ankommt (arrive=1) UND noch Touren hat (has_future=1):
  → Genau eine Tour ist als "nächste" markiert
- Sonst: keine Tour ist als "nächste" markiert

---

### NB12: next nur wenn zugeordnet

```
next[r,k,z] ≤ a[r,k]   ∀r, k, z
```

**Bedeutung:** Eine Tour kann nur "nächste Tour" von LKW k sein, wenn sie auch LKW k zugeordnet ist.

---

### NB13: next=0 für vergangene Touren

```
next[r,k,z] = 0   ∀r ∉ rAfter[z]
```

**Bedeutung:** Touren, die VOR z starten, können nicht die "nächste Tour nach z" sein.

---

### NB14: next ist wirklich die nächste

```
next[r,k,z] ≤ 1 - Σ_{r'∈R: z < s_r(r') < s_r(r)} next[r',k,z]
```

**Bedeutung:** Wenn Tour r als "nächste" markiert ist, darf keine früherer startende Tour r' auch markiert sein.

**Erklärung:**
- Bedingung `z < s_r(r') < s_r(r)` wählt alle Touren r', die zwischen z und dem Start von r beginnen
- Wenn irgendeine davon next = 1 hat, muss next[r,k,z] = 0 sein
- So wird sichergestellt, dass wirklich die NäCHSTE Tour gewählt wird

---

## 7.4 Energie-Dynamik E-LKW

### NB15: SOC-Dynamik

```
soc[k,z+1] = soc[k,z] - cons[k,z] + Σ_{l∈L} real_p[k,l,z] × 0.25
```

**Bedeutung:** Der Akku im nächsten Intervall = Akku jetzt - Verbrauch + Laden

**Aufschlüsselung:**
- `soc[k,z]` = aktüller Ladezustand
- `cons[k,z]` = Verbrauch durch Fahren (in kW, aber bezogen auf das Intervall)
- `real_p[k,l,z] × 0.25` = geladene Energie (kW × 0.25h = kWh)

---

### NB16 & NB17: SOC-Grenzen

```
soc[k,z] ≥ 0        (NB16 - Untergrenze)
soc[k,z] ≤ soc_e[type_k[k]]   (NB17 - Obergrenze)
```

**Bedeutung:** Der Akku kann nicht negativ oder über 100% sein.

---

### NB18 & NB19: Start und Ende mit vollem Akku

```
soc[k,1] = soc_e[type_k[k]]    (NB18 - Start)
soc[k,96] = soc_e[type_k[k]]   (NB19 - Ende)
```

**Bedeutung:** Am Tagesanfang und -ende muss der Akku voll sein.

**Sinn:** Der nächste Tag beginnt mit vollem Akku.

---

### NB20: Genug Energie geladen

```
Σ_{l∈L} Σ_{z∈Z} real_p[k,l,z] × 0.25 ≥ Σ_{r∈R} a[r,k] × dist[r] × avgEv_e[type_k[k]]
```

**Bedeutung:** Die Gesamtladung über den Tag muss mindestens so gross sein wie der Gesamtverbrauch.

**Links:** Gesamte geladene Energie (kWh)
**Rechts:** Gesamter Energiebedarf aller Touren (kWh)

---

## 7.5 Lade-Logik

### NB21: Ladeleistung begrenzt

```
real_p[k,l,z] ≤ assign[k,l,z] × max_p_e[type_k[k]]
```

**Bedeutung:**
- Wenn assign = 0: real_p ≤ 0 (also real_p = 0, da ≥ 0)
- Wenn assign = 1: real_p ≤ max_p_e (begrenzt durch LKW)

---

### NB22: Nur angesteckte LKWs laden

```
assign[k,l,z] ≤ plug[k,l,z]
```

**Bedeutung:** Aktives Laden (assign=1) nur wenn angesteckt (plug=1).

---

### NB23: Nur eine Säule gleichzeitig

```
Σ_{l∈L} plug[k,l,z] ≤ 1
```

**Bedeutung:** Ein LKW kann nur an EINER Säule angesteckt sein.

---

### NB24 & NB25: Diesel-LKWs können nicht laden

```
assign[k,l,z] = 0   ∀k mit type_k[k] ∈ TD   (NB24)
plug[k,l,z] = 0     ∀k mit type_k[k] ∈ TD   (NB25)
```

**Bedeutung:** Diesel-LKWs dürfen weder laden noch angesteckt werden.

---

### NB26: Nicht laden während Fahrt

```
Σ_{l∈L} plug[k,l,z] ≤ 1 - Σ_{r∈R} active[r,z] × a[r,k]
```

**Bedeutung:**
- Wenn eine Tour aktiv ist (rechte Seite = 1-1 = 0): plug muss 0 sein
- Wenn keine Tour aktiv ist (rechte Seite = 1-0 = 1): plug kann 1 sein

---

### NB27: Bei Tourstart nicht angesteckt

```
plug[k,l,z] ≤ 1 - depart[k,z+1]
```

**Bedeutung:** Im Intervall VOR einer Abfahrt muss der LKW abgesteckt werden.

---

### NB28: Abstecken nur wenn erlaubt

```
plug[k,l,z] - plug[k,l,z+1] ≤ unplug_ok[z]
```

**Bedeutung:** Die Differenz plug[z] - plug[z+1] ist:
- = 1 wenn der LKW abgesteckt wird (war 1, ist jetzt 0)
- = 0 wenn der Zustand gleich bleibt
- = -1 wenn der LKW angesteckt wird

Die Bedingung sagt: Abstecken (Differenz = 1) nur wenn unplug_ok = 1.

**Effekt:** Nachts (unplug_ok = 0) kann nicht abgesteckt werden.

---

## 7.6 Ladesäulen-Kapazitäten

### NB29: Anzahl ladender LKWs begrenzt

```
Σ_{k∈K} assign[k,l,z] ≤ y_l[l] × cs_l[l]
```

**Bedeutung:** Die Anzahl gleichzeitig ladender LKWs ≤ (Anzahl Säulen) × (Ladepunkte pro Säule)

**Beispiel:**
- 2 Säulen mit je 2 Ladepunkten = 4 LKWs können gleichzeitig laden

---

### NB30: Anzahl angesteckter LKWs begrenzt

```
Σ_{k∈K} plug[k,l,z] ≤ y_l[l] × cs_l[l]
```

**Analog zu NB29, aber für physisch angesteckte LKWs.**

---

### NB31: Gesamtladeleistung begrenzt

```
Σ_{k∈K} real_p[k,l,z] ≤ y_l[l] × max_p_l[l]
```

**Bedeutung:** Die Summe aller Ladeleistungen an Säulentyp l ≤ (Anzahl Säulen) × (Leistung pro Säule)

**Beispiel:**
- 2 Säulen mit je 200 kW = maximal 400 kW Gesamtladeleistung

---

### NB32: Maximale Säulenanzahl

```
0 ≤ y_l[l] ≤ Nmax
```

**Bedeutung:** Maximal Nmax = 3 Säulen pro Typ.

---

## 7.7 Nacht-Ladelogik

### NB33: Definition need_charge

```
need_charge[k,z] = 1 - enough[k,z]
```

**Bedeutung:** need_charge ist das Gegenteil von enough.

---

### NB34 & NB35: Genug Energie (Big-M Formulierung)

```
soc[k,z] + M × (1 - enough[k,z]) ≥ e_next[k,z]   (NB34)
soc[k,z] ≤ e_next[k,z] + M × enough[k,z]          (NB35)
```

**Kombinierte Bedeutung:**
- Wenn soc[k,z] ≥ e_next[k,z]: enough = 1 (genug Energie)
- Wenn soc[k,z] < e_next[k,z]: enough = 0 (nicht genug)

**Erklärung von NB34:**
- Wenn enough = 1: soc[k,z] + 0 ≥ e_next[k,z] → SOC muss reichen
- Wenn enough = 0: soc[k,z] + 10000 ≥ e_next[k,z] → immer wahr

**Erklärung von NB35:**
- Wenn enough = 1: soc[k,z] ≤ e_next[k,z] + 10000 → immer wahr
- Wenn enough = 0: soc[k,z] ≤ e_next[k,z] + 0 → SOC muss unter Bedarf liegen

---

### NB36: Anstecken wenn Ladepflicht

```
Σ_{l∈L} plug[k,l,z] ≥ arrive[k,z] × need_charge[k,z]
```

**Bedeutung:** Wenn der LKW ankommt (arrive=1) UND laden muss (need_charge=1), dann muss er angesteckt werden (plug≥1).

---

## 7.8 Netz und Speicher

### NB37: Netzlastbilanz

```
p_grid[z] = Σ_{k∈K} Σ_{l∈L} real_p[k,l,z] + p_l_s[z] - p_e_s[z]
```

**Bedeutung:** Netzbezug = LKW-Laden + Speicher-Laden - Speicher-Entladen

---

### NB38: Netzanschlussgrenze

```
p_grid[z] ≤ p_grid_max + 500 × u
```

**Bedeutung:**
- Ohne Trafo (u=0): p_grid ≤ 500 kW
- Mit Trafo (u=1): p_grid ≤ 1000 kW

---

### NB39: Leistungsspitze

```
p_grid[z] ≤ p_peak
```

**Bedeutung:** p_peak ist das Maximum aller p_grid-Werte.

---

### NB40: Speicher-Dynamik

```
soc_s[z+1] = soc_s[z] + p_l_s[z] × delta_t - (1/nrt) × p_e_s[z] × delta_t
```

**Bedeutung:** Speicherfüllstand im nächsten Intervall = jetzt + Laden - Entladen×Verlust

**Beachte:** Beim Entladen wird durch nrt geteilt (Verlust berücksichtigt).

---

### NB41: Speicher tagesneutral

```
soc_s[1] = soc_s[96]
```

**Bedeutung:** Der Speicher endet mit dem gleichen Füllstand wie er begonnen hat.

---

### NB42 & NB43: Speicher-Grenzen

```
soc_s[z] ≤ q_s                (NB42 - Obergrenze)
soc_s[z] ≥ dod × q_s          (NB43 - Untergrenze)
```

---

### NB44 & NB45: Speicher-Modus

```
p_l_s[z] ≤ mode_s[z] × p_s      (NB44 - Laden)
p_e_s[z] ≤ (1 - mode_s[z]) × p_s   (NB45 - Entladen)
```

**Bedeutung:**
- mode_s = 1: Laden erlaubt (p_l_s ≤ p_s), Entladen = 0
- mode_s = 0: Entladen erlaubt (p_e_s ≤ p_s), Laden = 0

---

# 8. ZIELFUNKTION IM DETAIL

Die Zielfunktion ist das, was MINIMIERT wird - die jährlichen Gesamtkosten.

```
min C_total = C_trucks + C_chargers + C_grid/trafo + C_storage + C_diesel,var + C_electricity - C_revenue
```

## 8.1 C_trucks - LKW-Fixkosten

```
C_trucks = Σ_{k∈K} [
  𝟙_{type_k[k]∈TD} × (cap_d[type_k[k]] + opx_d[type_k[k]] + kfz_d[type_k[k]]) +
  𝟙_{type_k[k]∈TE} × (cap_e[type_k[k]] + opx_e[type_k[k]])
]
```

**Das Symbol 𝟙** (Indikatorfunktion):
- 𝟙_{Bedingung} = 1, wenn die Bedingung wahr ist
- 𝟙_{Bedingung} = 0, wenn die Bedingung falsch ist

**Bedeutung:**
- Für jeden LKW k:
  - Wenn Diesel: Leasing + Wartung + KFZ-Steuer
  - Wenn Elektro: Leasing + Wartung (keine KFZ-Steuer!)

---

## 8.2 C_chargers - Ladeinfrastrukturkosten

```
C_chargers = Σ_{l∈L} y_l[l] × (cap_l[l] + opx_l[l])
```

**Bedeutung:** Für jeden Säulentyp: (Anzahl Säulen) × (Leasing + Wartung)

---

## 8.3 C_grid/trafo - Netzanschlusskosten

```
C_grid/trafo = 10.000 × u
```

**Bedeutung:** 10.000 EUR wenn ein Trafo installiert wird (u=1), sonst 0.

---

## 8.4 C_storage - Speicherkosten

```
C_storage = (capP_s × p_s + capQ_s × q_s) × (1 + opx_s)
```

**Bedeutung:**
- Leistungskosten: 30 EUR/kW × Speicherleistung
- Kapazitätskosten: 350 EUR/kWh × Speicherkapazität
- Plus 2% Wartung

---

## 8.5 C_diesel,var - Variable Dieselkosten

```
C_diesel,var = 260 × Σ_{r∈R} Σ_{k∈K: type_k[k]∈TD} a[r,k] × (c_m_d × mDist[r] + c_diesel × (dist[r]/100) × avgDv_d[type_k[k]])
```

**Aufschlüsselung:**
- 260 = Arbeitstage pro Jahr
- Nur Diesel-LKWs (type_k[k] ∈ TD)
- Für jede Tour:
  - Mautkosten: 0.34 EUR/km × mautpflichtige km
  - Dieselkosten: 1.68 EUR/L × (km/100) × Verbrauch (L/100km)

---

## 8.6 C_electricity - Stromkosten

```
C_electricity = c_gr + cPeak × p_peak + 260 × c_e × Σ_{z∈Z} p_grid[z] × delta_t
```

**Bestandteile:**
- `c_gr` = Grundgebühr (1.000 EUR/Jahr)
- `cPeak × p_peak` = Leistungspreis (150 EUR/kW × Spitzenleistung)
- `260 × c_e × Σ p_grid × delta_t` = Arbeitspreis (260 Tage × 0.25 EUR/kWh × Verbrauch)

---

## 8.7 C_revenue - THG-Erlöse (ABZUG!)

```
C_revenue = Σ_{k∈K: type_k[k]∈TE} thg_e[type_k[k]]
```

**Bedeutung:** Für jeden E-LKW gibt es THG-Prämie.

**Wichtig:** Wird ABGEZOGEN (negatives Vorzeichen in Zielfunktion)!

---

# ZUSAMMENFASSUNG

Das Modell optimiert eine gemischte LKW-Flotte (Diesel + Elektro) mit:

**Entscheidungen:**
- Welcher LKW fährt welche Tour?
- Welcher LKW ist Diesel, welcher Elektro?
- Wie viele und welche Ladesäulen?
- Wann wird wie viel geladen?
- Wird ein Trafo installiert?
- Wie gross ist der stationäre Speicher?

**Ziel:** Minimierung der jährlichen Gesamtkosten

**Randbedingungen:**
- Alle Touren müssen gefahren werden
- E-LKWs müssen genug Energie haben
- Ladekapazitäten dürfen nicht überschritten werden
- Netzkapazität ist begrenzt
- Nachts müssen LKWs angesteckt bleiben

---

*Erstellt zur detaillierten Erklärung des MILP-Optimierungsmodells*
