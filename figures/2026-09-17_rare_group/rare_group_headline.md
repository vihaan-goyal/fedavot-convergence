# Least-represented-group loss, decaying stepsize, tail-500 over 5 seeds (population std)

Adult: race = Other (smallest category; 1 group of 30). IMDb-Wiki: tier 1 = 20 highest-importance identities (least observed when beta > 0).

## adult: group Other, headline cells

| Instance | nu | FedAVOT | group-blind avg. | m/K | full |
|---|---|---|---|---|---|
| Adult, prevalence | 0.60 | 0.0732 +- 0.0027 | 0.1194 +- 0.0046 | 0.5804 +- 0.0150 | 0.0309 +- 0.0000 |
| Adult, aligned | 0.00 | 0.0318 +- 0.0005 | 0.0352 +- 0.0006 | div. | 0.0309 +- 0.0000 |

## adult: group Amer-Indian-Eskimo, headline cells

| Instance | nu | FedAVOT | group-blind avg. | m/K | full |
|---|---|---|---|---|---|
| Adult, prevalence | 0.60 | 0.1752 +- 0.0028 | 0.1888 +- 0.0019 | 0.6762 +- 0.0384 | 0.1227 +- 0.0000 |
| Adult, aligned | 0.00 | 0.1229 +- 0.0010 | 0.1302 +- 0.0012 | div. | 0.1227 +- 0.0000 |

## imdbwiki: group tier1, headline cells

| Instance | nu | FedAVOT | group-blind avg. | m/K | full |
|---|---|---|---|---|---|
| IMDb, skewed | 0.31 | 76.99 +- 0.73 | 86.42 +- 1.00 | 8662.10 +- 17044.52 | 72.23 +- 0.00 |
| IMDb, aligned | 0.00 | 73.63 +- 0.67 | 79.89 +- 0.66 | div. | 72.23 +- 0.00 |

## adult sweep, group Other

| beta | nu | stepsize | FedAVOT | group-blind avg. | full | gain (avg - FedAVOT) |
|---|---|---|---|---|---|---|
| 0.75 | 0.00 | const | 0.0278 | 0.0415 | 0.0278 | +0.0137 |
| 1.0 | 0.00 | const | 0.0287 | 0.0322 | 0.0278 | +0.0035 |
| 0.5 | 0.40 | const | 0.0328 | 0.0524 | 0.0278 | +0.0195 |
| 0.0 | 0.60 | const | 0.0645 | 0.0855 | 0.0278 | +0.0210 |
| 0.25 | 0.60 | const | 0.0490 | 0.0652 | 0.0278 | +0.0161 |
| 0.75 | 0.00 | decay1000 | 0.0309 | 0.0444 | 0.0309 | +0.0135 |
| 1.0 | 0.00 | decay1000 | 0.0318 | 0.0352 | 0.0309 | +0.0034 |
| 0.5 | 0.40 | decay1000 | 0.0353 | 0.0577 | 0.0309 | +0.0224 |
| 0.0 | 0.60 | decay1000 | 0.0732 | 0.1194 | 0.0309 | +0.0462 |
| 0.25 | 0.60 | decay1000 | 0.0525 | 0.0782 | 0.0309 | +0.0257 |

## adult sweep, group Amer-Indian-Eskimo

| beta | nu | stepsize | FedAVOT | group-blind avg. | full | gain (avg - FedAVOT) |
|---|---|---|---|---|---|---|
| 0.75 | 0.00 | const | 0.1199 | 0.1466 | 0.1183 | +0.0267 |
| 1.0 | 0.00 | const | 0.1195 | 0.1274 | 0.1183 | +0.0079 |
| 0.5 | 0.40 | const | 0.1285 | 0.1642 | 0.1183 | +0.0358 |
| 0.0 | 0.60 | const | 0.1723 | 0.1854 | 0.1183 | +0.0131 |
| 0.25 | 0.60 | const | 0.1535 | 0.1764 | 0.1183 | +0.0229 |
| 0.75 | 0.00 | decay1000 | 0.1231 | 0.1481 | 0.1227 | +0.0250 |
| 1.0 | 0.00 | decay1000 | 0.1229 | 0.1302 | 0.1227 | +0.0073 |
| 0.5 | 0.40 | decay1000 | 0.1319 | 0.1652 | 0.1227 | +0.0333 |
| 0.0 | 0.60 | decay1000 | 0.1752 | 0.1888 | 0.1227 | +0.0136 |
| 0.25 | 0.60 | decay1000 | 0.1562 | 0.1784 | 0.1227 | +0.0222 |

## imdbwiki sweep, group tier1

| beta | nu | stepsize | FedAVOT | group-blind avg. | full | gain (avg - FedAVOT) |
|---|---|---|---|---|---|---|
| 0.0 | 0.31 | const | 86.85 | 89.78 | 72.49 | +2.92 |
| 0.5 | 0.59 | const | 99.67 | 96.06 | 72.49 | -3.61 |
| 1.0 | 0.70 | const | 104.60 | 99.47 | 72.49 | -5.13 |
| 1.5 | 0.77 | const | 108.77 | 101.06 | 72.49 | -7.71 |
| 2.0 | 0.82 | const | 109.82 | 102.35 | 72.49 | -7.47 |
| 3.0 | 0.88 | const | 113.52 | 103.78 | 72.49 | -9.75 |
| 0.0 | 0.31 | decay1000 | 76.99 | 86.42 | 72.23 | +9.42 |
| 0.5 | 0.59 | decay1000 | 90.32 | 93.15 | 72.23 | +2.83 |
| 1.0 | 0.70 | decay1000 | 96.51 | 96.65 | 72.23 | +0.14 |
| 1.5 | 0.77 | decay1000 | 100.33 | 98.39 | 72.23 | -1.94 |
| 2.0 | 0.82 | decay1000 | 101.73 | 99.82 | 72.23 | -1.91 |
| 3.0 | 0.88 | decay1000 | 105.48 | 101.26 | 72.23 | -4.22 |
