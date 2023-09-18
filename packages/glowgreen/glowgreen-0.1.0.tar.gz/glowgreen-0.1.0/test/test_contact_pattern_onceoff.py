import pytest
import numpy as np
from datetime import datetime, timedelta
from glowgreen import ContactPatternOnceoff, Clearance_1m


def test_onceoff_init():
    theta = [0, 6]
    c = [1.5, 25]
    d = [0.1, 1]
    cpat = ContactPatternOnceoff(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0, 6]))
    assert np.allclose(cpat.c, np.array([1.5, 25]))
    assert isinstance(cpat.c, np.ndarray)
    assert np.array_equal(cpat.d, np.array([0.1, 1]))

    theta = 0
    c = 29
    d = 3
    cpat = ContactPatternOnceoff(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0]))
    assert np.array_equal(cpat.c, np.array([29]))
    assert np.array_equal(cpat.d, np.array([3]))

    theta = 1.6
    c = 29
    d = 3
    with pytest.raises(ValueError):
        cpat = ContactPatternOnceoff(theta, c, d)

    theta = 0
    c = 29
    d = 0
    with pytest.raises(ValueError):
        cpat = ContactPatternOnceoff(theta, c, d)


def test_get_dose_exp():
    """Test ContactPatternOnceoff.get_dose method with an exponential clearance function.

    Example problem:
      * Dose rate at 1 m is (50 uSv/h)*exp[-ln2 t / (40 h)], where t is time from admin.
      * Contact pattern is 6.5 hours at 0.3 m, 3 hour break, then 24 hours at 1.5 m.
    Caclulate the dose for a restriction period of 51 h.
    """
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau = 51  # h

    # dose calculation by hand
    lmbda = np.log(2) / effective_half_life
    factor1 = dose_rate_init_1m / lmbda * np.exp(-lmbda * tau)
    factor2 = 1 / (0.3) ** (1.5) * np.exp(-lmbda * 0) * (1 - np.exp(-lmbda * 6.5))
    factor2 += 1 / (1.5) ** (1.5) * np.exp(-lmbda * 9.5) * (1 - np.exp(-lmbda * 24))
    dose_hand = factor1 * factor2 / 1000.0  # uSv -> mSv

    # dose calculation by code
    theta = np.array([0, 9.5])
    c = np.array([6.5, 24])
    d = [0.3, 1.5]
    cpat = ContactPatternOnceoff(theta, c, d)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    dose_code = cpat.get_dose(cfit, tau)
    assert np.isclose(dose_code, dose_hand)

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, -0.1)

    assert cpat.get_dose(cfit, np.inf) == 0.0


def test_get_dose_biexp():
    """Test ContactPatternOnceoff.get_dose method with a biexponential clearance function.

    Example problem:
      * Dose rate at 1 m is (90 uSv/h)*[0.3*exp(-ln2 t / (5 h)) + 0.7*exp(-ln2 t / (50 h))],
        where t is time from admin.
      * Contact pattern is 6.5 hours at 0.3 m, 3 hour break, then 24 hours at 1.5 m.
    Caclulate the dose for a restriction period of 51 h.
    """
    dose_rate_init_1m = 90  # uSv/h
    fraction1 = 0.3
    half_life1 = 5  # h
    half_life2 = 50  # h
    tau = 51  # h

    # dose calculation by hand
    fraction2 = 1.0 - fraction1
    lmbda1 = np.log(2) / half_life1
    lmbda2 = np.log(2) / half_life2

    first_factor1 = dose_rate_init_1m * fraction1 / lmbda1 * np.exp(-lmbda1 * tau)
    first_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda1 * 0) * (1 - np.exp(-lmbda1 * 6.5))
    )
    first_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda1 * 9.5) * (1 - np.exp(-lmbda1 * 24))
    )

    second_factor1 = dose_rate_init_1m * fraction2 / lmbda2 * np.exp(-lmbda2 * tau)
    second_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda2 * 0) * (1 - np.exp(-lmbda2 * 6.5))
    )
    second_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda2 * 9.5) * (1 - np.exp(-lmbda2 * 24))
    )

    dose_hand = (
        (first_factor1 * first_factor2) + (second_factor1 * second_factor2)
    ) / 1000.0  # uSv -> mSv

    # dose calculation by code
    theta = np.array([0, 9.5])
    c = np.array([6.5, 24])
    d = [0.3, 1.5]
    cpat = ContactPatternOnceoff(theta, c, d)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    dose_code = cpat.get_dose(cfit, tau)
    assert np.isclose(dose_code, dose_hand)

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, -0.1)

    assert cpat.get_dose(cfit, np.inf) == 0.0


def test_get_restriction_exp():
    """Test ContactPatternOnceoff.get_restriction and ContactPatternOnceoff._get_restriction_arrays methods for
    exponential clearance function.

    * ContactPatternOnceoff.get_restriction returns true restriction period
    * ContactPatternOnceoff._get_restriction_arrays returns ceil(true restriction period)

    Example problem:
      * Dose rate at 1 m is (50 uSv/h)*exp[-ln2 t / (40 h)], where t is time from admin.
      * Contact pattern is once-off; 6.5 hours at 0.3 m, 3 hour break, then 24 hours at 1.5 m.
    Calculate the dose for a delay of 51.73 h, then use this dose as a dose constraint
    and calculate the restriction period.
    """
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau_original = 51.73  # h

    # dose calculation by hand
    lmbda = np.log(2) / effective_half_life
    factor1 = dose_rate_init_1m / lmbda * np.exp(-lmbda * tau_original)
    factor2 = 1 / (0.3) ** (1.5) * np.exp(-lmbda * 0) * (1 - np.exp(-lmbda * 6.5))
    factor2 += 1 / (1.5) ** (1.5) * np.exp(-lmbda * 9.5) * (1 - np.exp(-lmbda * 24))
    dose_hand = factor1 * factor2 / 1000.0  # uSv -> mSv
    dose_constraint = dose_hand

    # restriction period calculation by code
    theta = np.array([0, 9.5])
    c = np.array([6.5, 24])
    d = [0.3, 1.5]
    cpat = ContactPatternOnceoff(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, admin_datetime=datetime_admin
    )
    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, datetime_admin
    )
    assert tau == np.ceil(tau_original)
    assert datetime_end == datetime_admin + timedelta(hours=tau)
    assert dose == cpat.get_dose(cfit, tau)
    assert dose <= dose_constraint
    assert tau_arr[-1] == tau
    assert dose_arr[-1] == dose
    assert len(tau_arr) == len(dose_arr)
    assert cpat._get_restriction_arrays(cfit, dose_constraint)[4] is None

    tau_fast, dose_fast, datetime_end_fast = cpat.get_restriction(
        cfit, dose_constraint, admin_datetime=datetime_admin
    )
    tau_fast, dose_fast, datetime_end_fast = cpat.get_restriction(
        cfit, dose_constraint, datetime_admin
    )
    assert np.isclose(tau_fast, tau_original)
    assert datetime_end_fast == datetime_admin + timedelta(hours=tau_fast)
    assert dose_fast == cpat.get_dose(cfit, tau_fast)
    assert np.isclose(dose_fast, dose_constraint)
    assert cpat.get_restriction(cfit, dose_constraint)[2] is None

    assert cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[0] == 0.0
    assert cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[
        1
    ] == cpat.get_dose(cfit, 0.0)
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[4] == datetime_admin
    )
    assert cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[0] == 0.0
    assert cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[
        1
    ] == cpat.get_dose(cfit, 0.0)
    assert (
        cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[2]
        == datetime_admin
    )

    with pytest.warns(UserWarning):
        val = cpat._exact_restriction_period(cfit, np.inf)
    assert val == 0.0

    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, 0.0, datetime_admin)
    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, -1.3, datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, 0.0, admin_datetime=datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, -1.3, admin_datetime=datetime_admin)
    with pytest.raises(ValueError):
        cpat._exact_restriction_period(cfit, 0.0)
    with pytest.raises(ValueError):
        cpat._exact_restriction_period(cfit, -1.3)


def test__get_restriction_arrays_biexp():
    """Test ContactPatternOnceoff.get_restriction and ContactPatternOnceoff._get_restriction_arrays methods for
    biexponential clearance function.

    * ContactPatternOnceoff.get_restriction returns true restriction period
    * ContactPatternOnceoff._get_restriction_arrays returns ceil(true restriction period)

    Example problem:
      * Dose rate at 1 m is (90 uSv/h)*[0.3*exp(-ln2 t / (5 h)) + 0.7*exp(-ln2 t / (50 h))],
        where t is time from admin.
      * Contact pattern is once-off; 6.5 hours at 0.3 m, 3 hour break, then 24 hours at 1.5 m.
    Calculate the dose for a delay of 50.32 h, then use this dose as a dose constraint
    and calculate the restriction period.
    """
    dose_rate_init_1m = 90  # uSv/h
    fraction1 = 0.3
    half_life1 = 5  # h
    half_life2 = 50  # h
    tau_original = 50.32  # h

    # dose calculation by hand
    fraction2 = 1.0 - fraction1
    lmbda1 = np.log(2) / half_life1
    lmbda2 = np.log(2) / half_life2

    first_factor1 = (
        dose_rate_init_1m * fraction1 / lmbda1 * np.exp(-lmbda1 * tau_original)
    )
    first_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda1 * 0) * (1 - np.exp(-lmbda1 * 6.5))
    )
    first_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda1 * 9.5) * (1 - np.exp(-lmbda1 * 24))
    )

    second_factor1 = (
        dose_rate_init_1m * fraction2 / lmbda2 * np.exp(-lmbda2 * tau_original)
    )
    second_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda2 * 0) * (1 - np.exp(-lmbda2 * 6.5))
    )
    second_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda2 * 9.5) * (1 - np.exp(-lmbda2 * 24))
    )

    dose_hand = (
        (first_factor1 * first_factor2) + (second_factor1 * second_factor2)
    ) / 1000.0  # uSv -> mSv
    dose_constraint = dose_hand

    # restriction period calculation by code
    theta = np.array([0, 9.5])
    c = np.array([6.5, 24])
    d = [0.3, 1.5]
    cpat = ContactPatternOnceoff(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, admin_datetime=datetime_admin
    )
    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, datetime_admin
    )
    assert tau == np.ceil(tau_original)
    assert datetime_end == datetime_admin + timedelta(hours=tau)
    assert dose == cpat.get_dose(cfit, tau)
    assert dose <= dose_constraint
    assert tau_arr[-1] == tau
    assert dose_arr[-1] == dose
    assert len(tau_arr) == len(dose_arr)
    assert cpat._get_restriction_arrays(cfit, dose_constraint)[4] is None

    tau_fast, dose_fast, datetime_end_fast = cpat.get_restriction(
        cfit, dose_constraint, admin_datetime=datetime_admin
    )
    assert np.isclose(tau_fast, tau_original)
    assert datetime_end_fast == datetime_admin + timedelta(hours=tau_fast)
    assert dose_fast == cpat.get_dose(cfit, tau_fast)
    assert np.isclose(dose_fast, dose_constraint)
    assert cpat.get_restriction(cfit, dose_constraint)[2] is None

    assert cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[0] == 0.0
    assert cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[
        1
    ] == cpat.get_dose(cfit, 0.0)
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin)[4] == datetime_admin
    )
    assert cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[0] == 0.0
    assert cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[
        1
    ] == cpat.get_dose(cfit, 0.0)
    assert (
        cpat.get_restriction(cfit, np.inf, admin_datetime=datetime_admin)[2]
        == datetime_admin
    )

    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, 0.0, datetime_admin)
    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, -1.3, datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, 0.0, admin_datetime=datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, -1.3, admin_datetime=datetime_admin)
