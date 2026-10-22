"""Descriptive uncertainty for an intercept-only mean with facility clustering.

Each observed facility-month has weight one. CR1 uses G/(G-1); the usual
(N-1)/(N-k) factor equals one because k=1. A t(G-1) critical value is used.
This adjustment does not establish reliable coverage with only six clusters.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm, t


def facility_cluster_mean_interval(values, facilities, alpha=0.05):
    if not 0 < alpha < 1:
        raise ValueError('alpha must be between zero and one')
    frame = pd.DataFrame({'value': np.asarray(values, dtype=float),
                          'facility': np.asarray(facilities)}).dropna()
    if not np.isfinite(frame.value).all():
        raise ValueError('values must be finite')
    n = len(frame)
    g = frame.facility.nunique()
    if g < 2:
        raise ValueError('at least two facility clusters are required')
    mean = frame.value.mean()
    scores = (frame.value - mean).groupby(frame.facility).sum()
    variance = (g / (g - 1)) * np.square(scores).sum() / n**2
    se = float(np.sqrt(variance))
    critical = float(t.ppf(1 - alpha / 2, df=g - 1))
    z = float(norm.ppf(1 - alpha / 2))
    estimable = se > 0
    status = 'approximate; few facility clusters' if estimable else 'degenerate empirical variance; interval not informative'
    return {'status': status, 'mean': float(mean), 'standard_error': se, 'lower': float(mean - critical * se) if estimable else float('nan'),
            'upper': float(mean + critical * se) if estimable else float('nan'), 'observations': n, 'clusters': g,
            'degrees_of_freedom': g - 1, 't_critical': critical,
            'normal_wald_lower_sensitivity': float(mean - z * se) if estimable else float('nan'),
            'normal_wald_upper_sensitivity': float(mean + z * se) if estimable else float('nan'),
            'method': 'Intercept-only CR1 facility-cluster-adjusted t/Wald-type interval'}
