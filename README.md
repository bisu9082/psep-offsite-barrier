# psep-offsite-barrier

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24211474.svg)](https://doi.org/10.5281/zenodo.24211474)

Code and data for: Shin, M., Lee, G., Kang, K. *Off-site mitigation as a time-dependent barrier: lessons from the Fukushima Daiichi spent-fuel-pool injection and the Buncefield tank-farm fire* (submitted to Process Safety and Environmental Protection).

All inputs are transcribed from public records; sources are given per entry in `model/data.py` and in Table 2 of the paper.

## Reproduce
```
pip install numpy scipy matplotlib SALib
cd model
python analysis.py     # main Monte Carlo, results.json
python sens.py         # Spearman sensitivity (supplementary)
python sens2.py        # eta sweep, clock-time shift, Buncefield demand shape
python v3_extra.py     # Sobol indices, convergence, SDF dose-bin sensitivity
python v3_test.py      # stochastic critical-path T_est regimes
python figures.py      # all figures to ../fig
```
Seeds are fixed; runtime a few minutes on a laptop.

## Licence
Code: MIT. Data compilation: CC BY 4.0.
