# Stepsize schedule sweep, 2026-09-20

Runs: `results/2026-09-20_lr_schedules/<cell>_<sched>/` (7 new schedules) plus const and hyper1000 from `results/2026-09-14_severity_sweep/`. 4000 steps, 5 seeds, tail-500, same eta and flags as the paper cells; every rule in a cell shares the schedule (method-neutral). Selection rule: the schedule with the smallest full-coverage residual (measured full minus exact floor), i.e. the one that optimizes the reference best, chosen without looking at GAVOT or group-blind. t = Welch t (population std, 5 seeds) for gain = group-blind - GAVOT; |t| < 2.8 marked n.s.

### Adult infeasible (nu=.60)  (floors: GAVOT 0.2169, group-blind 0.2279, full 0.1993; sorted by full-coverage residual)

| schedule | lr_t | GAVOT | group-blind | full | resid full | resid GAVOT | resid grp | gain | t | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| const **<- pick** | eta | 0.2225 | 0.2381 | 0.2038 | 0.0045 | 0.0056 | 0.0101 | +0.0155 | 26.8 | GAVOT |
| hyper16000 | eta/(1+t/16000) | 0.2227 | 0.2388 | 0.2041 | 0.0048 | 0.0058 | 0.0109 | +0.0161 | 29.1 | GAVOT |
| hyper4000 | eta/(1+t/4000) | 0.2234 | 0.2410 | 0.2049 | 0.0056 | 0.0065 | 0.0131 | +0.0176 | 35.2 | GAVOT |
| sqrt1000 | eta/sqrt(1+t/1000) | 0.2240 | 0.2423 | 0.2054 | 0.0061 | 0.0071 | 0.0144 | +0.0183 | 38.1 | GAVOT |
| cosine | eta*(1+cos(pi t/R))/2 | 0.2251 | 0.2449 | 0.2061 | 0.0068 | 0.0083 | 0.0170 | +0.0197 | 35.2 | GAVOT |
| step1000 | eta*0.5^floor(t/1000) | 0.2255 | 0.2458 | 0.2064 | 0.0072 | 0.0087 | 0.0179 | +0.0202 | 40.0 | GAVOT |
| hyper1000 | eta/(1+t/1000) | 0.2269 | 0.2479 | 0.2073 | 0.0080 | 0.0100 | 0.0200 | +0.0210 | 44.7 | GAVOT |
| sqrt250 | eta/sqrt(1+t/250) | 0.2272 | 0.2483 | 0.2075 | 0.0082 | 0.0104 | 0.0204 | +0.0211 | 46.8 | GAVOT |
| hyper250 | eta/(1+t/250) | 0.2377 | 0.2606 | 0.2138 | 0.0145 | 0.0208 | 0.0327 | +0.0229 | 35.9 | GAVOT |

### Adult feasible (nu=0)  (floors: GAVOT 0.1993, group-blind 0.1996, full 0.1993; sorted by full-coverage residual)

| schedule | lr_t | GAVOT | group-blind | full | resid full | resid GAVOT | resid grp | gain | t | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| const **<- pick** | eta | 0.2045 | 0.2048 | 0.2038 | 0.0045 | 0.0052 | 0.0052 | +0.0002 | 6.3 | GAVOT |
| hyper16000 | eta/(1+t/16000) | 0.2047 | 0.2049 | 0.2041 | 0.0048 | 0.0054 | 0.0054 | +0.0002 | 6.0 | GAVOT |
| hyper4000 | eta/(1+t/4000) | 0.2053 | 0.2055 | 0.2049 | 0.0056 | 0.0060 | 0.0060 | +0.0002 | 6.1 | GAVOT |
| sqrt1000 | eta/sqrt(1+t/1000) | 0.2057 | 0.2059 | 0.2054 | 0.0061 | 0.0064 | 0.0064 | +0.0002 | 6.2 | GAVOT |
| cosine | eta*(1+cos(pi t/R))/2 | 0.2061 | 0.2063 | 0.2061 | 0.0068 | 0.0069 | 0.0067 | +0.0001 | 3.4 | GAVOT |
| step1000 | eta*0.5^floor(t/1000) | 0.2065 | 0.2067 | 0.2064 | 0.0072 | 0.0073 | 0.0072 | +0.0002 | 6.8 | GAVOT |
| hyper1000 | eta/(1+t/1000) | 0.2075 | 0.2077 | 0.2073 | 0.0080 | 0.0082 | 0.0081 | +0.0002 | 7.1 | GAVOT |
| sqrt250 | eta/sqrt(1+t/250) | 0.2077 | 0.2079 | 0.2075 | 0.0082 | 0.0084 | 0.0084 | +0.0002 | 6.8 | GAVOT |
| hyper250 | eta/(1+t/250) | 0.2139 | 0.2141 | 0.2138 | 0.0145 | 0.0146 | 0.0145 | +0.0002 | 5.1 | GAVOT |

### IMDb infeasible (nu=.31)  (floors: GAVOT 83.42, group-blind 90.42, full 82.94; sorted by full-coverage residual)

| schedule | lr_t | GAVOT | group-blind | full | resid full | resid GAVOT | resid grp | gain | t | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| hyper250 **<- pick** | eta/(1+t/250) | 84.21 | 90.82 | 82.94 | 0.00 | 0.79 | 0.40 | +6.61 | 31.3 | GAVOT |
| cosine | eta*(1+cos(pi t/R))/2 | 84.12 | 90.69 | 82.94 | 0.00 | 0.70 | 0.27 | +6.57 | 38.6 | GAVOT |
| step1000 | eta*0.5^floor(t/1000) | 84.96 | 91.18 | 82.94 | 0.00 | 1.53 | 0.76 | +6.22 | 24.5 | GAVOT |
| hyper1000 | eta/(1+t/1000) | 86.06 | 91.63 | 82.95 | 0.01 | 2.64 | 1.21 | +5.57 | 20.7 | GAVOT |
| sqrt250 | eta/sqrt(1+t/250) | 86.55 | 91.81 | 82.95 | 0.01 | 3.12 | 1.40 | +5.27 | 19.3 | GAVOT |
| sqrt1000 | eta/sqrt(1+t/1000) | 89.13 | 92.73 | 82.97 | 0.03 | 5.71 | 2.31 | +3.60 | 12.3 | GAVOT |
| hyper4000 | eta/(1+t/4000) | 89.83 | 92.96 | 82.98 | 0.04 | 6.41 | 2.54 | +3.13 | 10.4 | GAVOT |
| hyper16000 | eta/(1+t/16000) | 93.38 | 94.08 | 83.03 | 0.08 | 9.96 | 3.67 | +0.70 | 2.1 | GAVOT (n.s.) |
| const | eta | 95.63 | 94.76 | 83.07 | 0.13 | 12.21 | 4.34 | -0.87 | -2.5 | group-blind (n.s.) |

### IMDb feasible (nu=0)  (floors: GAVOT 82.94, group-blind 85.60, full 82.94; sorted by full-coverage residual)

| schedule | lr_t | GAVOT | group-blind | full | resid full | resid GAVOT | resid grp | gain | t | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| hyper250 **<- pick** | eta/(1+t/250) | 83.34 | 85.76 | 82.94 | 0.00 | 0.40 | 0.16 | +2.42 | 29.2 | GAVOT |
| cosine | eta*(1+cos(pi t/R))/2 | 83.28 | 85.74 | 82.94 | 0.00 | 0.34 | 0.14 | +2.46 | 47.8 | GAVOT |
| step1000 | eta*0.5^floor(t/1000) | 83.72 | 86.00 | 82.94 | 0.00 | 0.78 | 0.40 | +2.28 | 18.3 | GAVOT |
| hyper1000 | eta/(1+t/1000) | 84.28 | 86.37 | 82.95 | 0.01 | 1.34 | 0.77 | +2.09 | 12.8 | GAVOT |
| sqrt250 | eta/sqrt(1+t/250) | 84.53 | 86.54 | 82.95 | 0.01 | 1.59 | 0.94 | +2.01 | 11.3 | GAVOT |
| sqrt1000 | eta/sqrt(1+t/1000) | 85.86 | 87.44 | 82.97 | 0.03 | 2.92 | 1.83 | +1.57 | 6.6 | GAVOT |
| hyper4000 | eta/(1+t/4000) | 86.23 | 87.67 | 82.98 | 0.04 | 3.28 | 2.07 | +1.45 | 5.7 | GAVOT |
| hyper16000 | eta/(1+t/16000) | 88.00 | 88.82 | 83.03 | 0.08 | 5.06 | 3.21 | +0.82 | 2.6 | GAVOT (n.s.) |
| const | eta | 89.08 | 89.51 | 83.07 | 0.13 | 6.14 | 3.90 | +0.42 | 1.2 | GAVOT (n.s.) |
