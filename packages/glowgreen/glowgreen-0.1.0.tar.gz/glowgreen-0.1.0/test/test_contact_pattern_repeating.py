import pytest
import numpy as np
from datetime import datetime, timedelta
from glowgreen import ContactPatternRepeating, Clearance_1m


def test_rep_cpat_raises():
    with pytest.raises(ValueError):
        ContactPatternRepeating([0, 1], [1, 24], [1, 2])

    with pytest.raises(ValueError):
        ContactPatternRepeating(0, 25, 1)


def test_graduate_pattern():
    """Test ContactPatternRepeating.graduate_pattern, called in ContactPatternRepeating constructor."""
    theta = np.array([0.6, 2.5])
    c = np.array([0.7, 2])
    d = np.array([1, 2])
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6, 2.5, 3.5]))
    assert np.array_equal(cpat.c, np.array([0.7, 1.0, 1.0]))
    assert np.array_equal(cpat.d, np.array([1.0, 2.0, 2.0]))
    assert np.array_equal(theta, np.array([0.6, 2.5]))
    assert np.array_equal(c, np.array([0.7, 2]))
    assert np.array_equal(d, np.array([1, 2]))

    theta = [0.6, 2.5]
    c = [0.7, 2]
    d = [1, 2]
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6, 2.5, 3.5]))
    assert np.array_equal(cpat.c, np.array([0.7, 1.0, 1.0]))
    assert np.array_equal(cpat.d, np.array([1.0, 2.0, 2.0]))
    assert theta == [0.6, 2.5]
    assert c == [0.7, 2]
    assert d == [1, 2]

    theta = np.array([0.6, 1.4])
    c = np.array([0.7, 1.1])
    d = [1, 2]
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6, 1.4, 2.4]))
    assert np.allclose(cpat.c, np.array([0.7, 1.0, 0.1]))
    assert isinstance(cpat.c, np.ndarray)
    assert np.array_equal(cpat.d, np.array([1.0, 2.0, 2.0]))

    theta = [0.6, 1.4]
    c = [0.7, 1.1]
    d = np.array([1, 2])
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6, 1.4, 2.4]))
    assert np.allclose(cpat.c, np.array([0.7, 1.0, 0.1]))
    assert isinstance(cpat.c, np.ndarray)
    assert np.array_equal(cpat.d, np.array([1.0, 2.0, 2.0]))

    theta = [1.6, 2.9, 14.04]
    c = [0.3, 3.05, 1.31]
    d = [0.1, 1.9, 3.1]
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([1.6, 2.9, 3.9, 4.9, 5.9, 14.04, 15.04]))
    assert np.allclose(cpat.c, np.array([0.3, 1.0, 1.0, 1.0, 0.05, 1, 0.31]))
    assert isinstance(cpat.c, np.ndarray)
    assert np.array_equal(cpat.d, np.array([0.1, 1.9, 1.9, 1.9, 1.9, 3.1, 3.1]))

    theta = 0.6
    c = 0.7
    d = 1
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6]))
    assert np.array_equal(cpat.c, np.array([0.7]))
    assert np.array_equal(cpat.d, np.array([1.0]))

    theta = [0.6]
    c = [0.7]
    d = [1]
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([0.6]))
    assert np.array_equal(cpat.c, np.array([0.7]))
    assert np.array_equal(cpat.d, np.array([1.0]))

    theta = 1.3
    c = 0
    d = 0.4
    cpat = ContactPatternRepeating(theta, c, d)
    assert cpat.theta.size == 0
    assert cpat.c.size == 0
    assert cpat.d.size == 0

    theta = [1, 3, 4]
    c = [1.3, 0, 1]
    d = [0.4, 0, 0.6]
    cpat = ContactPatternRepeating(theta, c, d)
    assert np.array_equal(cpat.theta, np.array([1, 2, 4]))
    assert np.allclose(cpat.c, np.array([1, 0.3, 1]))
    assert np.array_equal(cpat.d, np.array([0.4, 0.4, 0.6]))

    theta = [1, 3, 4]
    c = [1.3, 0, 1]
    d = [0.4, 0, 0]
    with pytest.raises(ValueError):
        cpat = ContactPatternRepeating(theta, c, d)


def test_subtract_next_t_r_from():
    theta = np.array([5, 13])
    c = np.array([2, 3.5])
    d = [0.3, 1.5]
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    assert cpat._subtract_next_t_r_from(datetime_admin) == -13.75


def test_get_dose_exp_1():
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau = 0  # h

    # dose calculation by hand
    dose_hand = (
        dose_rate_init_1m * effective_half_life / (np.log(2) * 1e3)
    )  # uSv -> mSv

    # dose calculation by code
    theta = 0
    c = 24
    d = 1
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=0)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]

    assert np.isclose(dose_hand, dose_code)


def test_get_dose_exp_2():
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau = 48  # h

    # dose calculation by hand
    dose_hand = (
        dose_rate_init_1m
        * effective_half_life
        * np.exp(-np.log(2) * tau / effective_half_life)
        / (np.log(2) * 1e3)
    )  # uSv -> mSv

    # dose calculation by code
    theta = 0
    c = 24
    d = 1
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=0)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]

    assert np.isclose(dose_hand, dose_code)


def test_get_dose_exp_3():
    """Test ContactPatternRepeating.get_dose method with exponential clearance function.

    Example problem:
      * Admin at 10:15 AM.
      * Dose rate at 1 m is (50 uSv/h)*exp[-ln2 t / (40 h)], where t is time from admin.
      * Contact pattern is repeating; 5 AM to 7 AM at 0.3 m, 1 PM to 4:30 PM at 1.5 m.
    Caclulate the dose for a restriction period of 51 h, so contact resumes at 1:15 PM 2 days later.

    Note the restriction period ends during a pattern element.
    The code breaks up the 13:00 to 16:30 PM pattern element into start times of 13, 14, 15 and 16.
    So the exposure from 1:15 to 2 PM of the first cycle will not be included.
    """
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau = 51  # h

    # dose calculation by hand
    # phi = { (T_a - T_r) mod (p + tau)} mod p
    # phi = { (10.25 - 24) mod (24 + 51)} mod 24
    # phi = 13.25  # correct, restriction ends at 1:15 PM
    lmbda = np.log(2) / effective_half_life
    factor1 = (
        dose_rate_init_1m / lmbda * np.exp(-lmbda * tau) / (1 - np.exp(-lmbda * 24.0))
    )
    # 5 AM to 7 AM: theta_j - phi = 5 - 13.25 = -8.25, so S_p = -8.25 + 24 = 15.75, correct, this many hours from delay end to the first cycle (1:15 PM to 5 AM = 15.75 h)
    factor2 = 1 / (0.3) ** (1.5) * np.exp(-lmbda * 15.75) * (1 - np.exp(-lmbda * 2))
    # 1 PM to 4:30 PM: need to split up the contact, else the entire 3.5 hours of contact will be ignored for the first cycle, which is not what the code does
    # 1 PM to 2 PM:
    # theta_j - phi = 13 - 13.25 = -0.25, so S_p = -0.25 + 24 = 23.75, correct, this many hours from delay end to the first cycle (1:15 PM to 1 PM = 23.75 h)
    factor2 += 1 / (1.5) ** (1.5) * np.exp(-lmbda * 23.75) * (1 - np.exp(-lmbda * 1))
    # 2 PM to 4:30 PM: theta_j - phi = 14 - 13.25 = 0.75, so S_p = 0.75, correct, this many hours from delay end to the first cycle (1:15 PM to 2 PM = 0.75 h)
    factor2 += 1 / (1.5) ** (1.5) * np.exp(-lmbda * 0.75) * (1 - np.exp(-lmbda * 2.5))
    dose_hand = factor1 * factor2 / 1000.0  # uSv -> mSv

    # dose calculation by code
    theta = np.array([5, 13])
    c = np.array([2, 3.5])
    d = [0.3, 1.5]
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]
    assert np.isclose(dose_code, dose_hand)
    # ending tau at 2 PM gives the same dose
    assert np.isclose(cpat.get_dose(cfit, tau + 0.75, datetime_admin)[0], dose_code)
    # ending tau even slightly after 2PM means the exposure from 2 PM to 3 PM of the first cycle will not be included
    assert cpat.get_dose(cfit, tau + 0.76, datetime_admin)[0] < dose_code

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, -0.1, datetime_admin)

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, np.inf, datetime_admin)

    assert cpat.get_dose(cfit, 1e9, datetime_admin)[0] == 0.0

    with pytest.raises(ValueError):
        cpat.get_dose_finite(cfit, 2.0, 1.9, datetime_admin)
    assert np.isclose(
        cpat.get_dose_finite(cfit, tau, 1e9, datetime_admin)[0], dose_hand
    )
    assert (
        cpat.get_dose_finite(cfit, 0.0, 1e9, datetime_admin)[0]
        == cpat.get_dose(cfit, 0.0, datetime_admin)[0]
    )
    assert cpat.get_dose_finite(cfit, 1e9, 1e9, datetime_admin)[0] == 0.0


def test_get_dose_biexp_1():
    dose_rate_init_1m = 90  # uSv/h
    fraction1 = 0.3
    half_life1 = 5  # h
    half_life2 = 50  # h
    tau = 0  # h

    # dose calculation by hand
    dose_hand = (
        dose_rate_init_1m
        * (half_life1 * fraction1 + half_life2 * (1.0 - fraction1))
        / (np.log(2) * 1e3)
    )  # uSv -> mSv

    # dose calculation by code
    theta = 0
    c = 24
    d = 1
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=0)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]

    assert np.isclose(dose_hand, dose_code)


def test_get_dose_biexp_2():
    dose_rate_init_1m = 90  # uSv/h
    fraction1 = 0.3
    half_life1 = 5  # h
    half_life2 = 50  # h
    tau = 48  # h

    # dose calculation by hand
    dose_hand = (
        dose_rate_init_1m
        * (
            half_life1 * fraction1 * np.exp(-np.log(2) * tau / half_life1)
            + half_life2 * (1.0 - fraction1) * np.exp(-np.log(2) * tau / half_life2)
        )
        / (np.log(2) * 1e3)
    )  # uSv -> mSv

    # dose calculation by code
    theta = 0
    c = 24
    d = 1
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=0)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]

    assert np.isclose(dose_hand, dose_code)


def test_get_dose_biexp_3():
    """Test ContactPatternRepeating.get_dose method with biexponential clearance function.

    Example problem:
      * Admin at 10:15 AM.
      * Dose rate at 1 m is (90 uSv/h)*[0.3*exp(-ln2 t / (5 h)) + 0.7*exp(-ln2 t / (50 h))],
        where t is time from admin.
      * Contact pattern is repeating; 5 AM to 7 AM at 0.3 m, 1 PM to 4:30 PM at 1.5 m.
    Caclulate the dose for a restriction period of 51 h, so contact resumes at 1:15 PM 2 days later.

    Note the restriction period ends during a pattern element.
    The code breaks up the 13:00 to 16:30 PM pattern element into start times of 13, 14, 15 and 16.
    So the exposure from 1:15 to 2 PM of the first cycle will not be included.
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

    # first exp
    first_factor1 = (
        dose_rate_init_1m
        * fraction1
        / lmbda1
        * np.exp(-lmbda1 * tau)
        / (1 - np.exp(-lmbda1 * 24.0))
    )
    first_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda1 * 15.75) * (1 - np.exp(-lmbda1 * 2))
    )
    first_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda1 * 23.75) * (1 - np.exp(-lmbda1 * 1))
    )
    first_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda1 * 0.75) * (1 - np.exp(-lmbda1 * 2.5))
    )

    # second exp
    second_factor1 = (
        dose_rate_init_1m
        * fraction2
        / lmbda2
        * np.exp(-lmbda2 * tau)
        / (1 - np.exp(-lmbda2 * 24.0))
    )
    second_factor2 = (
        1 / (0.3) ** (1.5) * np.exp(-lmbda2 * 15.75) * (1 - np.exp(-lmbda2 * 2))
    )
    second_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda2 * 23.75) * (1 - np.exp(-lmbda2 * 1))
    )
    second_factor2 += (
        1 / (1.5) ** (1.5) * np.exp(-lmbda2 * 0.75) * (1 - np.exp(-lmbda2 * 2.5))
    )

    dose_hand = (
        (first_factor1 * first_factor2) + (second_factor1 * second_factor2)
    ) / 1000.0  # uSv -> mSv

    # dose calculation by code
    theta = np.array([5, 13])
    c = np.array([2, 3.5])
    d = [0.3, 1.5]
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    dose_code = cpat.get_dose(cfit, tau, datetime_admin)[0]
    assert np.isclose(dose_code, dose_hand)
    # ending tau at 2 PM gives the same dose
    assert np.isclose(cpat.get_dose(cfit, tau + 0.75, datetime_admin)[0], dose_code)
    # ending tau even slightly after 2PM means the exposure from 2 PM to 3 PM of the first cycle will not be included
    assert cpat.get_dose(cfit, tau + 0.76, datetime_admin)[0] < dose_code

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, -0.1, datetime_admin)

    with pytest.raises(ValueError):
        cpat.get_dose(cfit, np.inf, datetime_admin)[0]

    assert cpat.get_dose(cfit, 1e9, datetime_admin)[0] == 0.0

    with pytest.raises(ValueError):
        cpat.get_dose_finite(cfit, 2.0, 1.9, datetime_admin)
    assert np.isclose(
        cpat.get_dose_finite(cfit, tau, 1e9, datetime_admin)[0], dose_hand
    )
    assert (
        cpat.get_dose_finite(cfit, 0.0, 1e9, datetime_admin)[0]
        == cpat.get_dose(cfit, 0.0, datetime_admin)[0]
    )
    assert cpat.get_dose_finite(cfit, 1e9, 1e9, datetime_admin)[0] == 0.0


def test_get_restriction_exp():
    """Test ContactPatternRepeating.get_restriction and ContactPatternRepeating._get_restriction_arrays methods for
    exponential clearance function.

    For repeating patterns with next_element False,
    get_restriction and _get_restriction_arrays both return in the range:
    [true restriction period, true restriction period + (1 h) - min(self.c)[,
    where the true restriction period is limited only by the pattern element widths.
    But they do not necessarily return the same thing.

    Example problem:
      * Admin at 10:15 AM.
      * Dose rate at 1 m is (50 uSv/h)*exp[-ln2 t / (40 h)], where t is time from admin.
      * Contact pattern is repeating; 5 AM to 7 AM at 0.3 m, 1 PM to 4:30 PM at 1.5 m.
    Caclulate the dose for a restriction period of 51 h,
    so contact resumes at 1:15 PM 2 days later (= dose for delay of 51.75 h).
    Then use this dose (+ epsilon) as a dose constraint and calculate the restriction period.
    """
    dose_rate_init_1m = 50  # uSv/h
    effective_half_life = 40  # h
    tau_original = 51  # h

    # dose calculation by code
    theta = np.array([5, 13])
    c = np.array([2, 3.5])
    d = [0.3, 1.5]
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m("exponential", [dose_rate_init_1m, effective_half_life], 1.0)

    dose_code = cpat.get_dose(cfit, tau_original, datetime_admin)[0]
    dose_constraint = dose_code + 1e-9

    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, datetime_admin, next_element=False
    )
    assert 51.75 <= tau < (51.75 + 1 - min(cpat.c))
    assert datetime_end == datetime_admin + timedelta(hours=tau)
    assert dose == cpat.get_dose(cfit, tau, datetime_admin)[0]
    assert dose <= dose_constraint
    assert tau_arr[-1] == tau
    assert dose_arr[-1] == dose
    assert len(tau_arr) == len(dose_arr)

    tau_fast, dose_fast, datetime_end_fast = cpat.get_restriction(
        cfit, dose_constraint, datetime_admin, next_element=False
    )
    assert 51.75 <= tau_fast < (51.75 + 1 - min(cpat.c))
    assert datetime_end_fast == datetime_admin + timedelta(hours=tau_fast)
    assert dose_fast == cpat.get_dose(cfit, tau_fast, datetime_admin)[0]
    assert dose_fast <= dose_constraint

    with pytest.raises(AttributeError):
        cpat._exact_restriction_period(cfit, dose_constraint)

    # For inf dose constraint,
    # In this case, admin_datetime is not during a pattern element, so
    # 	if next_element = False, restriction period will be 0 h
    # 	if next_element = True, restriction period will be 2.75 h (10:15 to 13:00)

    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=False)[
            0
        ]
        == 0.0
    )
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=False)[
            1
        ]
        == cpat.get_dose(cfit, 0.0, datetime_admin)[0]
    )
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=False)[
            4
        ]
        == datetime_admin
    )
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=True)[0]
        == 2.75
    )
    assert np.isclose(
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=True)[
            1
        ],
        cpat.get_dose(cfit, 2.75, datetime_admin)[0],
    )
    assert cpat._get_restriction_arrays(
        cfit, np.inf, datetime_admin, next_element=True
    )[4] == datetime_admin + timedelta(hours=2.75)

    # same for get_restriction
    assert (
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[0] == 0.0
    )
    assert (
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[1]
        == cpat.get_dose(cfit, 0.0, datetime_admin)[0]
    )
    assert (
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[2]
        == datetime_admin
    )
    assert (
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[0] == 2.75
    )
    assert np.isclose(
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[1],
        cpat.get_dose(cfit, 2.75, datetime_admin)[0],
    )
    assert cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[
        2
    ] == datetime_admin + timedelta(hours=2.75)

    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, 0.0, datetime_admin)
    with pytest.raises(ValueError):
        cpat._get_restriction_arrays(cfit, -1.3, datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, 0.0, datetime_admin)
    with pytest.raises(ValueError):
        cpat.get_restriction(cfit, -1.3, datetime_admin)


def test_get_restriction_biexp():
    """Test get_restriction and _get_restriction_arrays methods for
    biexponential clearance function.

    For repeating patterns with next_element False,
    get_restriction and _get_restriction_arrays both return in the range:
    [true restriction period, true restriction period + (1 h) - min(self.c)[,
    where the true restriction period is limited only by the pattern element widths.
    But they do not necessarily return the same thing.
    Further, they do not necessarily return the same dose,
    though each dose will be less than the dose constraint.

    Example problem:
      * Admin at 10:15 AM.
      * Dose rate at 1 m is (90 uSv/h)*[0.3*exp(-ln2 t / (5 h)) + 0.7*exp(-ln2 t / (50 h))],
        where t is time from admin.
      * Contact pattern is repeating; 5 AM to 7 AM at 0.3 m, 10 AM to 11 AM at 1 m, 4:20 PM to 4:30 PM at 0.1 m.
    Caclulate the dose for a restriction period of 54.25 h,
    so contact resuming at 4:30 PM 2 days later.
    Then use this dose (+ epsilon) as a dose constraint and calculate the restriction period.
    """
    dose_rate_init_1m = 90  # uSv/h
    fraction1 = 0.3
    half_life1 = 5  # h
    half_life2 = 50  # h

    tau_original = 54.25  # h

    # dose calculation by code
    theta = np.array([5, 10, 16 + 2 / 6])
    c = np.array([2, 1, 1 / 6])
    d = [0.3, 1, 0.1]
    cpat = ContactPatternRepeating(theta, c, d)

    datetime_admin = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    cfit = Clearance_1m(
        "biexponential", [dose_rate_init_1m, fraction1, half_life1, half_life2], 1.0
    )

    dose_code = cpat.get_dose(cfit, tau_original, datetime_admin)[0]
    dose_constraint = dose_code + 1e-9

    tau, dose, tau_arr, dose_arr, datetime_end = cpat._get_restriction_arrays(
        cfit, dose_constraint, datetime_admin, next_element=False
    )
    assert 54.25 <= tau <= (54.25 + 1 - min(cpat.c))
    assert datetime_end == datetime_admin + timedelta(hours=tau)
    assert dose == cpat.get_dose(cfit, tau, datetime_admin)[0]
    assert dose <= dose_constraint
    assert tau_arr[-1] == tau
    assert dose_arr[-1] == dose
    assert len(tau_arr) == len(dose_arr)

    tau_fast, dose_fast, datetime_end_fast = cpat.get_restriction(
        cfit, dose_constraint, datetime_admin, next_element=False
    )
    assert 54.25 <= tau_fast <= (54.25 + 1 - min(cpat.c))
    assert datetime_end_fast == datetime_admin + timedelta(hours=tau_fast)
    assert np.isclose(dose_fast, cpat.get_dose(cfit, tau_fast, datetime_admin)[0])
    assert dose_fast <= dose_constraint

    # next_element True
    tau_next, dose_next, _, _, datetime_end_next = cpat._get_restriction_arrays(
        cfit, dose_constraint, datetime_admin, next_element=True
    )
    assert tau_next == 66.75
    assert dose_next == cpat.get_dose(cfit, 66.75, datetime_admin)[0]
    assert datetime_end_next == datetime_admin + timedelta(hours=66.75)

    tau_fast_next, dose_fast_next, datetime_end_fast_next = cpat.get_restriction(
        cfit, dose_constraint, datetime_admin, next_element=True
    )
    assert tau_fast_next == 66.75
    assert np.isclose(dose_fast_next, cpat.get_dose(cfit, 66.75, datetime_admin)[0])
    assert datetime_end_fast_next == datetime_admin + timedelta(hours=66.75)

    # inf dose constraint
    # In this case, admin_datetime occurs during a contact element, so
    # 	if next_element = False, restriction period will be 0.75 h.
    # 	If next_element = True, restriction period will be 0.75 + 5 + 19/60 h (10:15 AM to 16:19)
    # 	or 0.75 + 5 + 1/3 h (10:15 AM to 16:20), depending how a float appears
    assert (
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=False)[
            0
        ]
        == 0.75
    )

    assert np.isclose(
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=False)[
            1
        ],
        cpat.get_dose(cfit, 0.75, datetime_admin)[0],
    )
    assert cpat._get_restriction_arrays(
        cfit, np.inf, datetime_admin, next_element=False
    )[4] == datetime_admin + timedelta(hours=0.75)
    assert cpat._get_restriction_arrays(
        cfit, np.inf, datetime_admin, next_element=True
    )[0] in [0.75 + 5 + 19 / 60, 0.75 + 5 + 1 / 3]
    assert np.isclose(
        cpat._get_restriction_arrays(cfit, np.inf, datetime_admin, next_element=True)[
            1
        ],
        cpat.get_dose(cfit, 0.75 + 5 + 1 / 3, datetime_admin)[0],
    )
    assert cpat._get_restriction_arrays(
        cfit, np.inf, datetime_admin, next_element=True
    )[4] in [
        datetime_admin + timedelta(hours=0.75 + 5 + 19 / 60),
        datetime_admin + timedelta(hours=0.75 + 5 + 1 / 3),
    ]

    # same for get_restriction
    assert (
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[0]
        == 0.75
    )
    assert np.isclose(
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[1],
        cpat.get_dose(cfit, 0.75, datetime_admin)[0],
    )
    assert cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=False)[
        2
    ] == datetime_admin + timedelta(hours=0.75)
    assert cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[0] in [
        0.75 + 5 + 19 / 60,
        0.75 + 5 + 1 / 3,
    ]
    assert np.isclose(
        cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[1],
        cpat.get_dose(cfit, 0.75 + 5 + 1 / 3, datetime_admin)[0],
    )
    assert cpat.get_restriction(cfit, np.inf, datetime_admin, next_element=True)[2] in [
        datetime_admin + timedelta(hours=0.75 + 5 + 19 / 60),
        datetime_admin + timedelta(hours=0.75 + 5 + 1 / 3),
    ]
