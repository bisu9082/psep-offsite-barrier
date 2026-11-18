# psep-offsite-barrier

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24218123.svg)](https://doi.org/10.5281/zenodo.24218123)

Code and data for: Shin, M., Lee, K., Kang, K. *Establishment time of off-site mitigation as a barrier property in prolonged loss-of-function accidents: a supply-mode model applied to Buncefield, Arkema Crosby and Fukushima Daiichi* (submitted to Journal of Loss Prevention in the Process Industries).

All inputs are transcribed from public records; sources are given per entry in `model/data.py` (Arkema Crosby: paragraph numbers of the CSB investigation report 2017-08-I-TX) and in Table 2 of the paper. Planning-grade assumptions are marked as such.

## Reproduce
```
pip install numpy scipy matplotlib SALib
cd model
python analysis.py       # Case A Monte Carlo (Fukushima), results.json
python sens.py           # Spearman sensitivity (supplementary)
python sens2.py          # eta sweep, clock-time shift, Buncefield demand shape
python v3_extra.py       # Sobol indices, convergence, SDF dose-bin sensitivity
python v3_test.py        # stochastic critical-path T_est regimes
python arkema.py         # Case C: time to SADT of stranded reefer trailers, arkema.json
python crosscase.py      # three-case deadline-establishment summary, crosscase.json
python figures.py        # Figs 1-7, A1 to ../fig
python figures_jlppi.py  # Arkema figure, cross-case figure, graphical abstract
```
Seeds are fixed; runtime a few minutes on a laptop.

## Versions
- v1.1.1: Arkema Crosby case, general heat-balance deadline, cross-case comparison (JLPPI submission).
- v1.0.2: PSEP submission (two cases).

## Licence
Code: MIT. Data compilation: CC BY 4.0.
