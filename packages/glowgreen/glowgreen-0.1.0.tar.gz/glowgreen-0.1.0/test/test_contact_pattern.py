import pytest
from datetime import datetime
import numpy as np
from glowgreen.close_contact import _ContactPattern
from glowgreen import Clearance_1m, ContactPatternRepeating, ContactPatternOnceoff


def test_cpat_raises():
    with pytest.raises(TypeError):
        _ContactPattern([1, 2], [1, 2], 1)

    with pytest.raises(ValueError):
        _ContactPattern([1, 2], [1, 2], [1, 2, 3])

    with pytest.raises(TypeError):
        _ContactPattern([1, 2], [1, 2], ["1", 2])

    with pytest.raises(ValueError):
        _ContactPattern([1, 2], [-1, 2], [1, 2])

    with pytest.raises(ValueError):
        _ContactPattern([2, 1], [2, 1], [2, 1])

    with pytest.raises(ValueError):
        _ContactPattern([1, 2], [2, 2], [1, 2])

    with pytest.raises(TypeError):
        _ContactPattern(1, 1, [1, 2])

    with pytest.raises(ValueError):
        _ContactPattern(1, 1, -1)

    with pytest.raises(TypeError):
        _ContactPattern("1", 1, 1)


def test_plot():
    theta = np.array([0, 9.5])
    c = np.array([6.5, 2])
    d = [0.3, 1.5]
    cpat = ContactPatternOnceoff(theta, c, d)

    cpat.plot(test=True)
    cpat.plot(name="test", test=True)

    admin_datetime = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    model = "exponential"
    dose_rate_xm_init = 60.0
    effective_half_life = 11.0
    model_parameters = [dose_rate_xm_init, effective_half_life]
    measurement_distance = 2.0
    cfit = Clearance_1m(model, model_parameters, measurement_distance)

    dose_constraint = 0.01

    cpat.plot(cfit=cfit, test=True)
    cpat.plot(cfit=cfit, dose_constraint=dose_constraint, test=True)

    cpat = ContactPatternRepeating(theta, c, d)
    cpat.plot(test=True)
    cpat.plot(cfit=cfit, dose_constraint=dose_constraint, test=True)
    cpat.plot(
        cfit=cfit,
        dose_constraint=dose_constraint,
        admin_datetime=admin_datetime,
        test=True,
    )
