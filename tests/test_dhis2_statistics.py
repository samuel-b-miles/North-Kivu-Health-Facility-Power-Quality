import numpy as np
import pytest
from scipy.stats import t
from drc_power.dhis2_statistics import facility_cluster_mean_interval


def test_unequal_clusters_match_direct_sandwich_and_preserve_row_weighted_mean():
    y=np.array([1.,3.,5.,7.,9.,11.]);cluster=np.array(['a','a','b','c','c','c'])
    r=facility_cluster_mean_interval(y,cluster)
    scores=np.array([sum(y[cluster==c]-y.mean()) for c in set(cluster)])
    se=np.sqrt(3/2 * sum(scores**2)/len(y)**2)
    assert r['mean']==y.mean()
    assert r['standard_error']==pytest.approx(se)
    assert r['lower']==pytest.approx(y.mean()-t.ppf(.975,2)*se)
    assert r['degrees_of_freedom']==2


def test_equal_cluster_sizes_reduce_to_standard_error_of_cluster_means():
    y=np.array([0.,2.,2.,4.,4.,6.]);cluster=['a','a','b','b','c','c']
    r=facility_cluster_mean_interval(y,cluster)
    assert r['standard_error']==pytest.approx(np.std([1,3,5],ddof=1)/np.sqrt(3))


def test_missing_values_are_not_zero_and_zero_variance_is_uninformative():
    r=facility_cluster_mean_interval([0.,0.,None],['a','b','c'])
    assert r['observations']==2 and r['clusters']==2
    assert np.isnan(r['lower']) and 'degenerate' in r['status']


def test_symmetric_negative_limit_is_not_silently_clipped():
    r=facility_cluster_mean_interval([0.,0.,1.],['a','b','c'])
    assert r['lower']<0


def test_single_cluster_is_rejected():
    with pytest.raises(ValueError, match='at least two'):
        facility_cluster_mean_interval([1,2],['a','a'])
