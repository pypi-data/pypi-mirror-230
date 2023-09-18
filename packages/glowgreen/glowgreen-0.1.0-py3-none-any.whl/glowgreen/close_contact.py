from datetime import datetime, date, time, timedelta
import numpy as np
import warnings
from . import clearance
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import fsolve


class _ContactPattern:
    """Base class for :class:`ContactPatternRepeating` and
    :class:`ContactPatternOnceoff`.
    Not for instantiation.

    Contains methods common to both repeating and onceoff contact patterns.
    """

    def __init__(self, theta, c, d):
        """Subclass constructors first `super` this constructor to perform
        non-specific quality control.

        Args:
            theta (int, float, list or numpy.ndarray): Start times (h) of pattern elements.
            c (int, float, list or numpy.ndarray): Durations (h) of pattern elements.
            d (int, float, list or numpy.ndarray): Distances (m) of pattern elements.

        Raises:
            TypeError: If ``theta`` is list or numpy.ndarray and ``c`` or `d` are not.
            ValueError: If ``theta``, ``c`` and ``d`` are not equal length.
            TypeError: If ``theta``, ``c`` or ``d`` contain a value not int, float, numpy.int32, numpy.int64 or numpy.float64.
            ValueError: If negative value in ``theta``, ``c`` or ``d``.
            ValueError: If pattern elements not provided in order.
            ValueError: If pattern elements overlap.
            TypeError: If ``theta`` is int or float and ``c`` or ``d`` are not.
            ValueError: If ``theta``, ``c`` or ``d`` is negative.
            TypeError: If ``theta`` not type int, float, list or numpy.ndarray.
        """
        if isinstance(theta, (list, np.ndarray)):
            if (not isinstance(c, (list, np.ndarray))) or (
                not isinstance(d, (list, np.ndarray))
            ):
                raise TypeError("theta is list or numpy.ndarray and c or d are not")

            if (len(theta) != len(c)) or (len(theta) != len(d)):
                raise ValueError("theta, c and d not equal length")

            if not all(
                all(
                    isinstance(x, (int, float, np.int32, np.int64, np.float64))
                    for x in a
                )
                for a in [theta, c, d]
            ):
                raise TypeError(
                    "theta, c or d contain a value not int, float, numpy.int32, numpy.int64 or numpy.float64"
                )

            if any(any(x < 0.0 for x in a) for a in [theta, c, d]):
                raise ValueError("negative value in theta, c or d")

            if any(theta[i + 1] < theta[i] for i in range(len(theta) - 1)):
                raise ValueError("pattern elements not provided in order")

            for i in range(len(theta) - 1):
                if (theta[i] + c[i]) > theta[i + 1]:
                    raise ValueError("pattern elements overlap")

            self.theta = theta.copy()
            self.c = c.copy()
            self.d = d.copy()
        elif isinstance(theta, (int, float)):
            if (not isinstance(c, (int, float))) or (not isinstance(d, (int, float))):
                raise TypeError("theta is int or float and c or d are not")

            if any(x < 0.0 for x in [theta, c, d]):
                raise ValueError("theta, c or d is negative")

            self.theta = theta
            self.c = c
            self.d = d
        else:
            raise TypeError("theta not type int, float, list or numpy.ndarray")

    @staticmethod
    def _dist_func(d):
        """Return the factor by which the dose rate at 1 m can be multiplied to get the dose rate
        at some other distance during the pattern.

        Inverse 1.5 power is used.

        Args:
            d (int, float or numpy.ndarray): Distance (m) of pattern element.

        Returns:
            float or numpy.ndarray: Correction factor to go from dose rate at 1 m to dose rate at ``d``.
        """
        return (1 / d) ** 1.5

    def plot(
        self,
        name=None,
        cfit: clearance.Clearance_1m = None,
        dose_constraint=None,
        admin_datetime: datetime = None,
        test=False,
    ):
        """Generate a plot of the contact pattern and, if sufficient information is provided in optional args,
        an additional plot of the dose from the pattern as a function of the
        time from administration to beginning sharing the onceoff pattern, or
        resuming sharing the repeating pattern, with a radioactive person.

        Args:
            name (str, optional): A name for the contact pattern, to appear in the figure title.
            cfit (clearance.Clearance_1m, optional): Dose rate clearance from radioactive person.
            dose_constraint (int or float, optional): Dose constraint (mSv).
            admin_datetime (datetime.datetime, optional): Administration datetime.
                Has no effect if pattern is onceoff.
            test (bool, optional): Option to not show the plot. Used for testing. Default is False.
        """
        if None not in [cfit, dose_constraint] and (
            admin_datetime is not None or isinstance(self, ContactPatternOnceoff)
        ):
            fig, (ax1, ax2) = plt.subplots(2, 1)
            if name is not None:
                fig.suptitle(name, fontsize=11)
        else:
            fig, ax1 = plt.subplots()
            if name is not None:
                ax1.set_title(name, fontsize=11)

        if isinstance(self, ContactPatternRepeating):
            ax1.bar(
                self.theta,
                self.d ** (-3 / 2),
                width=self.c,
                align="edge",
                fill=True,
                edgecolor="black",
                color=(0, 158 / 255, 115 / 255),
            )
            ax1.set_xlabel("24-hour time")
            ax1.set_xlim(left=0.0, right=24.0)
            ax1.set_xticks(np.arange(0, 25, 1))
            y_up = ax1.get_ylim()[1]
            if admin_datetime is not None:
                ax1.annotate(
                    "ADMIN",
                    xy=(admin_datetime.hour + admin_datetime.minute / 60.0, 0),
                    xytext=(
                        admin_datetime.hour + admin_datetime.minute / 60.0,
                        0.2 * y_up,
                    ),
                    horizontalalignment="center",
                    arrowprops={"arrowstyle": "->"},
                )
        elif isinstance(self, ContactPatternOnceoff):
            ax1.bar(
                self.theta,
                self.d ** (-3 / 2),
                width=self.c,
                align="edge",
                edgecolor="black",
                color=(86 / 255, 180 / 255, 233 / 255),
                fill=True,
            )
            ax1.set_xlabel("Time from end of restriction (h)")
            ax1.set_xlim(left=0.0)
        ax1.set_ylabel(r"${[(1~\mathrm{m}) ~/~ \mathrm{distance}]}^{1.5}$")
        ax1.set_ylim(bottom=1e-4)

        warnings.filterwarnings("ignore", "divide by zero encountered in power")
        secax = ax1.secondary_yaxis(
            "right", functions=(lambda x: x ** (-2 / 3), lambda x: x ** (-3 / 2))
        )

        secax.set_yticks(np.unique(self.d))
        secax.set_ylabel("Distance (m)")

        if None not in [cfit, dose_constraint] and (
            admin_datetime is not None or isinstance(self, ContactPatternOnceoff)
        ):
            _, _, tau_arr, dose_arr, _ = self._get_restriction_arrays(
                cfit, dose_constraint, admin_datetime
            )
            ax2.plot(
                tau_arr,
                dose_arr,
                "o",
                markersize=4,
                markerfacecolor="None",
                markeredgecolor="black",
            )
            ax2.plot(
                np.linspace(0, tau_arr[-1], num=50, endpoint=True),
                dose_constraint * np.ones(50),
                color=(204 / 255, 121 / 255, 167 / 255),
                ls="--",
                label="{:g} mSv".format(dose_constraint),
            )
            ax2.set_xlabel("Delay from time of administration (h)")
            ax2.set_ylabel("Dose (mSv)")
            ax2.set_xlim(left=0.0)
            ax2.set_ylim(bottom=0.0)
            ax2.legend(loc="best")
            plt.tight_layout()

        if not test:
            plt.show()


class ContactPatternRepeating(_ContactPattern):
    """Class for infinitely repeating diurnal contact patterns."""

    def __init__(self, theta, c, d):
        """Constructor:
         * Calls constructor of :class:`_ContactPattern`.
         * ``theta``, ``c`` and ``d`` are converted into numpy.ndarrays if they were not supplied as such.
         * Pattern elements with duration longer than 1 h are broken up, so that
           the restriction period can be better resolved.

        Args:
            theta (int, float, list or numpy.ndarray): Time (h) from 12 AM to start of pattern element.
            c (int, float, list or numpy.ndarray): Duration (h) of pattern element.
            d (int, float, list or numpy.ndarray): Distance (m) of pattern element;
                i.e., distance from radioactive person for duration of pattern element.

        Raises:
            ValueError: If element of repeating pattern has ``d`` of 0 and ``c`` not 0.
            ValueError: If repeating pattern extends beyond pattern period (24 h).
        """
        super().__init__(theta, c, d)

        self.t_r = time(
            0, 0
        )  # Reference time (12 AM), which theta is defined with respect to.
        self.p = 24.0  # Pattern period (h)

        if isinstance(self.theta, (list, np.ndarray)):
            if any(c_num != 0 and d_num == 0 for c_num, d_num in zip(self.c, self.d)):
                raise ValueError("element of repeating pattern has d of 0 and c not 0")
            if (self.theta[-1] + self.c[-1]) > self.p:
                raise ValueError(
                    "repeating pattern extends beyond pattern period (24 h)"
                )
        else:
            if self.c != 0 and self.d == 0:
                raise ValueError("element of repeating pattern has d of 0 and c not 0")
            if (self.theta + self.c) > self.p:
                raise ValueError(
                    "repeating pattern extends beyond pattern period (24 h)"
                )

        self._graduate_pattern()

    @staticmethod
    def _graduate_pattern_element(
        theta_num, c_num, d_num
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Writes a single pattern element as 1 or more elements,
        with all but the last element having duration 1 h.

        For example, ``c_num`` = 1.2 -> c_subarr = np.array([1., 0.2]),
        theta_subarr = np.array([``theta_num``, ``theta_num`` + 1.]) and
        d_subarr = np.array([``d_num``, ``d_num``]).

        Args:
            theta_num (int or float): Time (h) from 12 AM to start of pattern element.
            c_num (int or float): Duration (h) of pattern element.
            d_num (int or float): Distance (m) of pattern element.

        Returns:
            tuple[numy.ndarray, numy.ndarray, numy.ndarray]:
            Graduated versions of ``theta_num``, ``c_num`` and ``d_num``.
        """
        theta_subarr = np.linspace(
            theta_num,
            theta_num + np.ceil(c_num),
            num=int(np.ceil(c_num)),
            endpoint=False,
        )
        c_subarr = np.ones(int(np.floor(c_num)))
        if len(c_subarr) < len(theta_subarr):
            c_subarr = np.append(c_subarr, c_num - np.floor(c_num))
        d_subarr = d_num * np.ones(len(theta_subarr))
        return theta_subarr, c_subarr, d_subarr

    def _graduate_pattern(self):
        """Pattern elements with duration longer than 1 h are broken up.

        ``self``.theta, ``self``.c and ``self``.d finish as numpy.ndarrays.
        """
        if isinstance(self.theta, (int, float)):
            self.theta, self.c, self.d = self._graduate_pattern_element(
                self.theta, self.c, self.d
            )
        else:
            theta_subarr_list = []
            c_subarr_list = []
            d_subarr_list = []
            for i in range(len(self.theta)):
                theta_subarr, c_subarr, d_subarr = self._graduate_pattern_element(
                    self.theta[i], self.c[i], self.d[i]
                )
                theta_subarr_list.append(theta_subarr)
                c_subarr_list.append(c_subarr)
                d_subarr_list.append(d_subarr)
            self.theta = np.array(
                [item for subarr in theta_subarr_list for item in subarr]
            )
            self.c = np.array([item for subarr in c_subarr_list for item in subarr])
            self.d = np.array([item for subarr in d_subarr_list for item in subarr])

    def _subtract_next_t_r_from(self, admin_datetime):
        """Return ``admin_datetime`` minus the next reference time (h).

        Args:
            admin_datetime (datetime.datetime): Administration datetime.

        Returns:
            float: ``admin_datetime`` minus the next reference time (h). Range is [-``self``.p, 0[.
        """
        dt_next_t_r = datetime.combine(
            date(
                day=admin_datetime.day,
                month=admin_datetime.month,
                year=admin_datetime.year,
            ),
            self.t_r,
        ) + timedelta(hours=self.p)
        hrs = (admin_datetime - dt_next_t_r).total_seconds() / 3600.0
        return hrs

    def _get_phi(self, admin_datetime, tau):
        """Return the shift (h) from reference time (12 AM) to when the pattern is resumed (i.e. when ``tau`` ends)

        Args:
            admin_datetime (datetime.datetime): Administration datetime.
            tau (int or float): The time (h) from ``admin_datetime`` to when the pattern is resumed.

        Returns:
            float: The shift (h) from reference time (12 AM) to when the pattern is resumed.
        """
        dt = self._subtract_next_t_r_from(admin_datetime)
        return (dt % (tau + self.p)) % self.p

    def _if_neg_add_p(self, x):
        y = np.zeros(len(x))
        for i in range(len(x)):
            if x[i] >= 0:
                y[i] = x[i]
            else:
                y[i] = x[i] + self.p
            # When the delay period is increased so that its end coincides with the start of a pattern element,
            # x is sometimes a tiny negative number, so p is returned when 0 should be returned
            if np.isclose(y[i], self.p) or np.isclose(y[i], 0.0):
                y[i] = 0.0
        return y

    def _time_to_end_of_element(self, tau, admin_datetime: datetime):
        """If the delay ``tau`` ends during a pattern element, return the time (h) til the end of the element,
        else return 0.

        Args:
            tau (int or float): The time (h) from ``admin_datetime`` to when the pattern is resumed.
            admin_datetime (datetime.datetime): Administration datetime.

        Returns:
            float: The time (h) from when ``tau`` ends til end of concurrent pattern element. Range is [0, 1[.
        """
        t_left = 0.0
        phi = self._get_phi(admin_datetime, tau)
        for i in range(len(self.theta)):
            if self.theta[i] < phi < (self.theta[i] + self.c[i]):
                t_left = self.theta[i] + self.c[i] - phi
                break
        return t_left

    def get_dose(
        self, cfit: clearance.Clearance_1m, tau, admin_datetime: datetime
    ) -> tuple[float, float]:
        """Calculate the lifetime dose (mSv) from sharing the infinitely repeating pattern
        with a radioactive person, for a given dose rate clearance function,
        delay period and administration datetime.

        Implements method in: Cormack J & Shearer J. "Calculation of radiation exposures from patients to whom
        radioactive materials have been administered." Phys Med Biol 1998; 43(3).

        NB. If the delay period ``tau`` ends during a pattern element,
        the dose calculated will not include a contribution from the
        remainder of that pattern element in the first cycle.
        I.e., the calculated dose will be for the delay period shifted forward (by less than 1 h)
        to the end of the pattern element.
        Hence, the potentially corrected delay period is returned along with the dose.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance from radioactive person.
            tau (int or float): Delay period (h); i.e., the time
                from ``admin_datetime`` to when the pattern is resumed.
            admin_datetime (datetime.datetime): Administration datetime.

        Raises:
            ValueError: If ``tau`` less than 0.
            ValueError: If ``tau`` is numpy.inf with repeating pattern.

        Returns:
            tuple[float, float]: Dose (mSv) from the pattern from the end of the delay period to infinity,
            and the potentially corrected delay period (h).
        """
        if tau < 0.0:
            raise ValueError("tau less than 0")
        if tau == np.inf:  # cannot handle, e.g. _get_phi
            raise ValueError("tau is numpy.inf with repeating pattern")

        if cfit.model == "exponential":
            dose_rate_1m_init, effective_half_life = cfit.model_params
            a = 1
            lmbda = np.log(2) / effective_half_life
            lmbda = np.array(
                [lmbda]
            )  # make it an ndarray of length n for n-component exponential
        elif cfit.model == "biexponential":
            dose_rate_1m_init, fraction_1, half_life_1, half_life_2 = cfit.model_params
            fraction_2 = 1.0 - fraction_1
            lmbda_1 = np.log(2) / half_life_1
            lmbda_2 = np.log(2) / half_life_2
            a = np.array([fraction_1, fraction_2])
            lmbda = np.array([lmbda_1, lmbda_2])

        phi = self._get_phi(admin_datetime, tau)
        theta_prime = self._if_neg_add_p(
            self.theta - phi
        )  # theta if the reference time was the end of the delay

        arr = np.zeros(len(lmbda))
        for i in range(len(lmbda)):
            # summing over theta_prime, self.c, self.d arrays (if more than 1 element in pattern, else np.sum does nothing)
            arr[i] = np.sum(
                self._dist_func(self.d)
                * np.exp(-lmbda[i] * theta_prime)
                * (1 - np.exp(-lmbda[i] * self.c))
            )

        # summing over a, lmbda, arr arrays (if biexp, otherwise np.sum does nothing)
        dose = dose_rate_1m_init * np.sum(
            (a / lmbda)
            * np.exp(-lmbda * tau)
            * (1 / (1 - np.exp(-lmbda * self.p)))
            * arr
        )

        tau += self._time_to_end_of_element(tau, admin_datetime)

        return dose / 1000.0, tau  # uSv -> mSv

    def get_dose_finite(
        self, cfit: clearance.Clearance_1m, t1, t2, admin_datetime: datetime
    ) -> tuple[float, float, float]:
        """Return the dose (mSv) from sharing the repeating pattern with a radioactive person between 2 time points.

        For example, the dose if the pattern is resumed after some delay period
        then ceased again permanently at a later time.

        NB. If ``t1`` or ``t2`` end during a pattern element, the calculated dose is for
        that time point shifted forward (by less than 1 h) to the end of the pattern element.
        Hence, the potentially corrected time interval is returned along with the dose.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance from radiaoctive person.
            t1 (int or float): The time (h) from ``admin_datetime`` to the start of the exposure.
            t2 (int or float): The time (h) from ``admin_datetime`` to the end of the exposure.
            admin_datetime (datetime.datetime): Administration datetime.

        Raises:
            ValueError: If ``t2`` less than ``t1``.

        Returns:
            tuple[float, float, float]: Dose (mSv) from the pattern between 2 time points
            with respect to ``admin_datetime``,
            first time point (h), and second time point (h).
        """
        if t2 < t1:
            raise ValueError("t2 less than t1")
        d1, t1 = self.get_dose(cfit, t1, admin_datetime)
        d2, t2 = self.get_dose(cfit, t2, admin_datetime)
        dose_finite = d1 - d2
        return dose_finite, t1, t2

    def get_restriction(
        self,
        cfit: clearance.Clearance_1m,
        dose_constraint,
        admin_datetime: datetime,
        next_element=True,
    ) -> tuple[float, float, datetime]:
        """Calculate the restriction period; i.e., the least time from administration
        (up to the resolution of the pattern element widths)
        to when sharing the pattern with a radioactive person can be resumed, such that the lifetime dose from the
        infinitely repeating pattern is less than the dose constraint.

        NB. Using ``next_element`` True is advisable and can make a large difference for sparse repeating patterns such as public transport to and from work.
        For example, if we want you to miss the morning bus, it means you have to wait for the afternoon bus;
        you can't just get on the morning bus at 9 AM instead of 8 AM and expect to comply with the dose constraint.
        By always having the end of the restriction period coincide with the start of a pattern element,
        it is clear that contact can resume immediately at the end of the restriction period.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance from radioactive person.
            dose_constraint (int or float): Dose constraint (mSv).
            admin_datetime (datetime.datetime): Administration datetime.
            next_element (bool, optional): If the end of the restriction period does not coincide with the start of a pattern element,
                extend the restriction period to the start of the next pattern element. Default is True.

        Raises:
            ValueError: If ``dose_constraint`` not greater than 0.

        Returns:
            tuple[float, float, datetime.datetime]: Calculated restriction period (h),
            dose (mSv) from the pattern from the end of this restriction period to infinity,
            and the datetime at the end of this restriction period.

            With ``next_element`` False, the calculated restriction period is in the range:
            [true restriction period, true restriction period + (1 h) - min(``self``.c)[,
            where the true restriction period is limited only by the pattern element widths.
        """
        if dose_constraint <= 0.0:
            raise ValueError("dose_constraint not greater than 0")

        tau = 0.0
        dose, tau = self.get_dose(cfit, tau, admin_datetime)
        while dose > dose_constraint:  # and not np.isclose(dose, dose_constraint):
            # take larger steps using linear extrapolation
            delta_dose = self.get_dose(cfit, tau + 24.0, admin_datetime)[0] - dose
            slope = delta_dose / 24.0
            intercept = dose - (slope * tau)
            new_tau = (dose_constraint - intercept) / slope
            if (new_tau - tau) < 1.0:
                tau += 1.0
            else:
                tau = np.floor(new_tau)
            dose, tau = self.get_dose(cfit, tau, admin_datetime)

        while True:
            # walk it back
            if tau - 1.0 < 0.0:
                break
            if (
                self.get_dose(cfit, tau - 1.0, admin_datetime)[0] < dose_constraint
            ):  # or np.isclose(self.get_dose(cfit, tau - 1., admin_datetime)[0], dose_constraint):
                tau -= 1.0
                dose, tau = self.get_dose(cfit, tau, admin_datetime)
            else:
                break

        datetime_end = admin_datetime + timedelta(hours=tau)
        if next_element:
            for i in range(len(self.theta)):
                theta_hr = int(np.floor(self.theta[i]))
                theta_minute = int(np.floor((self.theta[i] - theta_hr) * 60.0))
                theta_datetime = datetime.combine(
                    datetime_end.date(), time(hour=theta_hr, minute=theta_minute)
                )
                if theta_datetime == datetime_end:
                    break
                elif theta_datetime > datetime_end:
                    extra_t = (theta_datetime - datetime_end).total_seconds() / 3600
                    tau += extra_t
                    datetime_end = theta_datetime
                    break
                elif i == len(self.theta) - 1:
                    theta_hr = int(np.floor(self.theta[0]))
                    theta_minute = int(np.floor((self.theta[0] - theta_hr) * 60.0))
                    theta_datetime = datetime.combine(
                        datetime_end.date(), time(hour=theta_hr, minute=theta_minute)
                    ) + timedelta(days=1)
                    extra_t = (theta_datetime - datetime_end).total_seconds() / 3600
                    tau += extra_t
                    datetime_end = theta_datetime

        return tau, dose, datetime_end

    def _get_restriction_arrays(
        self,
        cfit: clearance.Clearance_1m,
        dose_constraint,
        admin_datetime: datetime,
        next_element=True,
    ) -> tuple[float, float, np.ndarray, np.ndarray, datetime]:
        """Arrive at the restriction period (at most 1 h longer than it needs to be)
        by calculating the lifetime dose for delays in 1 h steps, starting from administration
        and stopping when the dose drops below the dose constraint
        (it might step once more to the start of the next pattern element if ``next_element`` True).

        * The delay is the time (h) from administration to when the contact pattern is resumed.
        * The restriction period is the least delay (up to the resolution of the pattern element widths) for which the lifetime dose received
          is less than the dose constraint.
        * Setting ``next_element`` True is advisable and can make a large difference for sparse repeating patterns such as public transport to and from work.
          E.g. If we want you to miss the morning bus, it means you have to wait for the afternoon bus;
          you can't just get on the morning bus at 9 AM instead of 8 AM and expect to comply with the dose constraint.
          By making the end of the restriction period coincide with the start of a pattern element,
          it is clear that contact can resume immediately at the end of the restriction period.
        * The calculated restriction period with ``next_element`` False is not necessarily equal to that calcuated by :meth:`get_restriction`
          with ``next_element`` False, though they have the same range.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance object.
            dose_constraint (int or float): Dose constraint (mSv).
            admin_datetime (datetime.datetime): Administration datetime.
            next_element (bool, optional): If the end of the restriction period does not coincide with the start of a pattern element,
                extend the restriction period to the start of the next pattern element. Defaults to True.

        Raises:
            ValueError: If ``dose_constraint`` not greater than 0.

        Returns:
            tuple[float, float, numpy.ndarray, numpy.ndarray, datetime.datetime]: Calculated restriction period (h).
            With ``next_element`` False, this is in the range [true restriction period, true restriction period + (1 h) - min(``self``.c)[,
            where the true restriction period is limited only by the pattern element widths.

            Dose (mSv) from the pattern with the calculated restriction period;

            Delays (h) sampled up to the calculated restriction period;

            Doses (mSv) corresponding to the delays;

            Datetime at the end of the calculated restriction period.
        """
        if dose_constraint <= 0.0:
            raise ValueError("dose_constraint not greater than 0")

        tau_arr = []
        dose_arr = []

        tau = 0
        dose, tau = self.get_dose(cfit, tau, admin_datetime)
        tau_arr.append(tau)
        dose_arr.append(dose)

        while dose > dose_constraint:  # and not np.isclose(dose, dose_constraint):
            tau += 1.0
            dose, tau = self.get_dose(cfit, tau, admin_datetime)
            tau_arr.append(tau)
            dose_arr.append(dose)

        datetime_end = (
            None if admin_datetime == None else admin_datetime + timedelta(hours=tau)
        )
        if next_element:
            for i in range(len(self.theta)):
                theta_hr = int(np.floor(self.theta[i]))
                theta_minute = int(np.floor((self.theta[i] - theta_hr) * 60.0))
                theta_datetime = datetime.combine(
                    datetime_end.date(), time(hour=theta_hr, minute=theta_minute)
                )
                if theta_datetime == datetime_end:
                    break
                elif theta_datetime > datetime_end:
                    extra_t = (theta_datetime - datetime_end).total_seconds() / 3600
                    tau += extra_t
                    tau_arr.append(tau)
                    dose_arr.append(dose)
                    datetime_end = theta_datetime
                    break
                elif i == len(self.theta) - 1:
                    theta_hr = int(np.floor(self.theta[0]))
                    theta_minute = int(np.floor((self.theta[0] - theta_hr) * 60.0))
                    theta_datetime = datetime.combine(
                        datetime_end.date(), time(hour=theta_hr, minute=theta_minute)
                    ) + timedelta(days=1)
                    extra_t = (theta_datetime - datetime_end).total_seconds() / 3600
                    tau += extra_t
                    tau_arr.append(tau)
                    dose_arr.append(dose)
                    datetime_end = theta_datetime

        return tau, dose, np.array(tau_arr), np.array(dose_arr), datetime_end


class ContactPatternOnceoff(_ContactPattern):
    """Class for onceoff contact patterns."""

    def __init__(self, theta, c, d):
        """Constructor:
         * Calls constructor of :class:`_ContactPattern`.
         * ``theta``, ``c`` and ``d`` are converted into numpy.ndarrays if they were not supplied as such.

        Args:
            theta (int, float, list or numpy.ndarray): Time (h) **from end of delay** to start of pattern element.
            c (int, float, list or numpy.ndarray): Duration (h) of pattern element.
            d (int, float, list or numpy.ndarray): Distance (m) of pattern element;
              i.e., distance from radioactive person for duration of pattern element.

        Raises:
            ValueError: If ``theta`` not 0 for first element of onceoff pattern.
            ValueError: If element of onceoff pattern has ``d`` of 0.
        """
        super().__init__(theta, c, d)

        if isinstance(self.theta, (list, np.ndarray)):
            if self.theta[0] != 0:
                raise ValueError("theta not 0 for first element of onceoff pattern")
            if any(x == 0 for x in self.d):
                raise ValueError("element of onceoff pattern has d of 0")
        else:
            if self.theta != 0:
                raise ValueError(
                    "theta value not 0 for first element of onceoff pattern"
                )
            if self.d == 0:
                raise ValueError("element of onceoff pattern has d == 0")

        if isinstance(self.theta, list):
            self.theta = np.array(self.theta)
        elif isinstance(self.theta, (int, float)):
            self.theta = np.array([self.theta])
        if isinstance(self.c, list):
            self.c = np.array(self.c)
        elif isinstance(self.c, (int, float)):
            self.c = np.array([self.c])
        if isinstance(self.d, list):
            self.d = np.array(self.d)
        elif isinstance(self.d, (int, float)):
            self.d = np.array([self.d])

    def get_dose(self, cfit: clearance.Clearance_1m, tau, *args) -> float:
        """Return the dose (mSv) from sharing the onceoff pattern
        with a radioactive person, for a given dose rate clearance function and delay period.

        Unlike with repeating patterns, the dose from a onceoff pattern
        is independent of the administration datetime.
        ``*args`` allows this method to be called with additional argument `administration datetime`,
        so it can be called the same way on both :class:`ContactPatternRepeating` and :class:`ContactPatternOnceoff` objects.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance from radioactive person.
            tau (int or float): Delay period (h); i.e., the time
                from administration to when the pattern is started.

        Raises:
            ValueError: If ``tau`` less than 0.

        Returns:
            float: Dose (mSv) from the pattern.
        """
        if tau < 0.0:
            raise ValueError("tau less than 0")

        if cfit.model == "exponential":
            dose_rate_1m_init, effective_half_life = cfit.model_params
            a = 1
            lmbda = np.log(2) / effective_half_life
            lmbda = np.array(
                [lmbda]
            )  # make it an ndarray of length n for n-component exponential
        elif cfit.model == "biexponential":
            dose_rate_1m_init, fraction_1, half_life_1, half_life_2 = cfit.model_params
            fraction_2 = 1.0 - fraction_1
            lmbda_1 = np.log(2) / half_life_1
            lmbda_2 = np.log(2) / half_life_2
            a = np.array([fraction_1, fraction_2])
            lmbda = np.array([lmbda_1, lmbda_2])

        arr = np.zeros(len(lmbda))
        for i in range(len(lmbda)):
            # summing over self.theta, self.c, self.d arrays (if more than 1 element in pattern, else np.sum does nothing)
            arr[i] = np.sum(
                self._dist_func(self.d)
                * np.exp(-lmbda[i] * self.theta)
                * (1 - np.exp(-lmbda[i] * self.c))
            )

        # summing over a, lmbda, arr arrays (if biexp, otherwise np.sum does nothing)
        dose = dose_rate_1m_init * np.sum((a / lmbda) * np.exp(-lmbda * tau) * arr)

        return dose / 1000.0  # uSv -> mSv

    def _exact_restriction_period(self, cfit: clearance.Clearance_1m, dose_constraint):
        """Return the exact restriction period required for a dose constraint.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance object.
            dose_constraint (float): Dose constraint (mSv).

        Raises:
            ValueError: If ``dose_constraint`` not greater than 0.

        Returns:
            float: Exact restriction period (h).
        """
        if dose_constraint <= 0.0:
            raise ValueError("dose constraint not greater than 0")

        if self.get_dose(cfit, 0.0) < dose_constraint:
            warnings.warn(
                "no exact restriction period as dose is less than dose constraint with no delay"
            )
            return 0.0

        if cfit.model == "exponential":
            dose_rate_1m_init, effective_half_life = cfit.model_params
            lmbda = np.log(2) / effective_half_life
            rho = np.sum(
                self._dist_func(self.d)
                * np.exp(-lmbda * self.theta)
                * (1 - np.exp(-lmbda * self.c))
            )
            tau = (
                np.log(dose_rate_1m_init * rho / (dose_constraint * 1e3 * lmbda))
                / lmbda
            )  # uSv <-> mSv
            return tau
        elif cfit.model == "biexponential":
            return fsolve(lambda tau: self.get_dose(cfit, tau) - dose_constraint, 0.0)[
                0
            ]

    def get_restriction(
        self,
        cfit: clearance.Clearance_1m,
        dose_constraint,
        admin_datetime: datetime = None,
    ) -> tuple[float, float, datetime]:
        """Calculate the restriction period; i.e., the time from administration to beginning sharing the pattern with a
        radioactive person, such that the dose from the pattern is equal to the dose constraint.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance from radioactive person.
            dose_constraint (int or float): Dose constraint (mSv).
            admin_datetime (datetime.datetime, optional): Administration datetime.

        Raises:
            ValueError: If ``dose_constraint`` not greater than 0.

        Returns:
            tuple[float, float, datetime.datetime]: Restriction period (h),
            dose (mSv) from the pattern with this restriction period, and
            datetime at the end of this restriction period (None if ``admin_datetime`` is None).
        """
        if dose_constraint <= 0.0:
            raise ValueError("dose_constraint not greater than 0")

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                "no exact restriction period as dose is less than dose constraint with no delay",
            )
            tau = self._exact_restriction_period(cfit, dose_constraint)
        datetime_end = (
            None if admin_datetime == None else admin_datetime + timedelta(hours=tau)
        )
        return tau, self.get_dose(cfit, tau), datetime_end

    def _get_restriction_arrays(
        self,
        cfit: clearance.Clearance_1m,
        dose_constraint,
        admin_datetime: datetime = None,
    ) -> tuple[float, float, np.ndarray, np.ndarray, datetime]:
        """Arrive at the ceiling of the restriction period
        by calculating the dose for delays in 1 h steps, starting from administration
        and stopping when the dose drops below the dose constraint.

        * The delay is the time (h) from administration to when the contact pattern starts.
        * The restriction period is the delay for which the dose received
          is equal to the dose constraint.

        Args:
            cfit (clearance.Clearance_1m): Dose rate clearance object.
            dose_constraint (int or float): Dose constraint (mSv).
            admin_datetime (datetime.datetime, optional): Administration datetime.

        Raises:
            ValueError: If ``dose_constraint`` is not greater than 0.

        Returns:
            tuple[float, float, numpy.ndarray, numpy.ndarray, datetime.datetime]: Calculated restriction period (h),
            equal to the ceiling of the true restriction period;

            Dose (mSv) from the pattern with the calculated restriction period;

            Delays (h) sampled up to the calculated restriction period;

            Doses (mSv) corresponding to the delays;

            Datetime at the end of the calculated restriction period (None if ``admin_datetime`` is None).
        """
        if dose_constraint <= 0.0:
            raise ValueError("dose_constraint not greater than 0")

        tau_arr = []
        dose_arr = []

        tau = 0
        dose = self.get_dose(cfit, tau, admin_datetime)

        tau_arr.append(tau)
        dose_arr.append(dose)
        while dose > dose_constraint:  # and not np.isclose(dose, dose_constraint):
            tau += 1.0
            dose = self.get_dose(cfit, tau, admin_datetime)
            tau_arr.append(tau)
            dose_arr.append(dose)

        datetime_end = (
            None if admin_datetime == None else admin_datetime + timedelta(hours=tau)
        )
        return tau, dose, np.array(tau_arr), np.array(dose_arr), datetime_end


def cs_patterns() -> pd.DataFrame:
    """Return a dataframe containing the contact patterns published by Cormack & Shearer and adapted by SAMI
    along with appropriate dose constraints.

    Reference: Cormack J & Shearer J. "Calculation of radiation exposures from patients to whom
    radioactive materials have been administered." Phys Med Biol 1998; 43(3).

    Lukas E. "Preliminary recommendations for changes to radionuclide therapy contact patterns." (internal document)

    Returns:
        pandas.DataFrame:
        Dataframe with column labels:
         * `name` (str): A name for the contact pattern and dose constraint pairing.
         * `pattern_type` (str): 'repeating' or 'onceoff', indicating the type of pattern.
         * `theta` (int, float, list or numpy.ndarray): Start times (h) of pattern elements.
         * `c` (int, float, list or numpy.ndarray): Durations (h) of pattern elements.
         * `d` (int, float, list or numpy.ndarray): Distances (m) of pattern elements.
         * `dose_constraint` (int or float): Dose constraint (mSv).
         * `per_episode` (int): 1 if dose constraint is to be treated as per treatment episode, 0 if per annum.
    """
    list_of_dicts = []
    theta = np.linspace(0, 23, num=24)

    list_of_dicts.append(
        {
            "name": "Caring for infants (normal)",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    20,
                    0,
                    0,
                    0,
                    20,
                    30,
                    40,
                    30,
                    20,
                    30,
                    40,
                    30,
                    20,
                    30,
                    40,
                    30,
                    20,
                    0,
                    0,
                    0,
                    35,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0.3,
                0,
                0,
                0,
                0.3,
                0.5,
                1,
                0.5,
                0.3,
                0.5,
                1,
                0.5,
                0.3,
                0.5,
                1,
                0.5,
                0.3,
                0,
                0,
                0,
                0.3,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Caring for infants (demanding or sick)",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    35,
                    0,
                    0,
                    0,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    35,
                    0,
                    0,
                    0,
                    35,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0.3,
                0,
                0,
                0,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0,
                0,
                0,
                0.3,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Prolonged close contact (>15min) with 2-5 year old children",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    60,
                    30,
                    30,
                    30,
                    30,
                    30,
                    60,
                    30,
                    30,
                    30,
                    30,
                    30,
                    60,
                    30,
                    0,
                    0,
                    0,
                    0,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0,
                0,
                0,
                0.3,
                0.3,
                0.3,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                0.3,
                0.3,
                0.3,
                0,
                0,
                0,
                0,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Prolonged close contact (>15min) with 5-15 year old children",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    30,
                    30,
                    60,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    60,
                    60,
                    60,
                    30,
                    30,
                    0,
                    0,
                    0,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0,
                0,
                0,
                0.3,
                0.3,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                0.3,
                0.3,
                0,
                0,
                0,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Sleeping with another person (includes pregnant or child)",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    60,
                    60,
                    60,
                    60,
                    60,
                ]
            )
            / 60.0,
            "d": [
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                1,
                1,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                0.3,
                0.3,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Sleeping with informed supporter",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    60,
                    60,
                    60,
                    60,
                    60,
                ]
            )
            / 60.0,
            "d": [
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                1,
                1,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                0.3,
                0.3,
            ],
            "dose_constraint": 5.0,
            "per_episode": 1,
        }
    )

    list_of_dicts.append(
        {
            "name": "Sleeping with person and prolonged daytime close contact (>15min)",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                ]
            )
            / 60.0,
            "d": [
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                1,
                1,
                1,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                0.3,
                0.3,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Sleeping with informed supporter and prolonged daytime close contact (>15min)",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                ]
            )
            / 60.0,
            "d": [
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                0.3,
                1,
                1,
                1,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                0.3,
                0.3,
            ],
            "dose_constraint": 5.0,
            "per_episode": 1,
        }
    )

    list_of_dicts.append(
        {
            "name": "Prolonged close contact (>15min) with adult household members",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    30,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    30,
                    60,
                    60,
                    0,
                    0,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0.5,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                1,
                1,
                0.5,
                0.3,
                1,
                1,
                0,
                0,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Prolonged close contact (>15min) with pregnant household members",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    30,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    60,
                    30,
                    60,
                    60,
                    0,
                    0,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0.5,
                1,
                1,
                1,
                0.5,
                1,
                1,
                1,
                1,
                1,
                0.5,
                0.3,
                1,
                1,
                0,
                0,
            ],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Prolonged close contact (>15min) with informed persons caring for patient",
            "pattern_type": "repeating",
            "theta": theta,
            "c": np.array(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    30,
                    30,
                    60,
                    0,
                    0,
                    30,
                    30,
                    60,
                    0,
                    0,
                    60,
                    60,
                    60,
                    30,
                    30,
                    0,
                    0,
                    0,
                ]
            )
            / 60.0,
            "d": [
                0,
                0,
                0,
                0,
                0,
                0,
                0.3,
                0.5,
                1,
                0,
                0,
                0.3,
                0.5,
                1,
                0,
                0,
                1,
                1,
                1,
                0.5,
                0.3,
                0,
                0,
                0,
            ],
            "dose_constraint": 5.0,
            "per_episode": 1,
        }
    )

    list_of_dicts.append(
        {
            "name": "Cinema, theatre visits; social functions/visits",
            "pattern_type": "repeating",
            "theta": 9.0,
            "c": 3.0,
            "d": 0.5,
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Daily public transport to and from work",
            "pattern_type": "repeating",
            "theta": [8, 17],
            "c": [1, 1],
            "d": [0.3, 0.3],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Return to work involving prolonged close contact (>15min) with others",
            "pattern_type": "repeating",
            "theta": [9, 12, 14, 16],
            "c": [3, 2, 2, 1],
            "d": [0.5, 1, 0.5, 1],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Return to work not involving prolonged close contact (>15min) with others",
            "pattern_type": "repeating",
            "theta": 9.0,
            "c": 8.0,
            "d": 1.0,
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Work with radiosensitive materials",
            "pattern_type": "repeating",
            "theta": 9.0,
            "c": 8.0,
            "d": 1.0,
            "dose_constraint": 0.1,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "Return to school",
            "pattern_type": "repeating",
            "theta": [9, 12, 14, 16],
            "c": [3, 2, 2, 1],
            "d": [0.5, 1, 0.5, 1],
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    list_of_dicts.append(
        {
            "name": "A single 24-hour trip on public transport",
            "pattern_type": "onceoff",
            "theta": 0,
            "c": 24,
            "d": 0.3,
            "dose_constraint": 1.0,
            "per_episode": 0,
        }
    )

    df = pd.DataFrame.from_records(list_of_dicts)

    return df


def restrictions_for(
    df: pd.DataFrame,
    cfit: clearance.Clearance_1m,
    num_treatments_in_year,
    admin_datetime: datetime = None,
) -> pd.DataFrame:
    """Compute restriction periods for the supplied contact patterns and dose constraints in a dataframe,
    dose rate clearance function, number of treatments anticipated in a year and administration datetime.

    Args:
        df (pandas.DataFrame): Dataframe that includes column labels `pattern_type`, `theta`, `c`, `d`, `dose_constraint` and `per_episode`.
          See ``Returns`` section of :func:`cs_patterns`.
        cfit (clearance.Clearance_1m): Dose rate clearance from radioactive person.
        num_treatments_in_year (int, float): Number of treatments anticipated in a year.
          Used to scale `dose_constraint` if `per_episode` is 0.
        admin_datetime (datetime.datetime, optional): Administration datetime.
          Can only be omitted or None if `pattern_type` is 'onceoff' for all rows in ``df``,
          in which case the returned dataframe will have all None values in column `datetime_end`.

    Raises:
        KeyError: If ``df`` missing column label `pattern_type`, `theta`, `c`, `d`, `dose_constraint` or `per_episode`.
        ValueError: If row in ``df`` has `pattern_type` not 'repeating' or 'onceoff'.
        ValueError: If row in ``df`` has `pattern_type` 'repeating' and ``admin_datetime`` None.
        ValueError: If ``num_treatments_in_year`` less than 1.

    Returns:
        pandas.DataFrame: Deep copy of ``df`` with additional (or overwritten) columns labelled:
         * `dose_constraint_corrected` (float): Dose constraint (mSv) corrected for number of treatments in a year.
           Only differs from `dose_constraint` if `per_episode` is 0. If `per_episode` is 0, `dose_constraint` is per annum, so
           `dose_constraint_corrected` = `dose_constraint` / ``num_treatments_in_year``.
         * `restriction_period` (float): Calculated restriction period (h).
         * `dose` (float): Dose (mSv) from the pattern with the calculated restriction period.
         * `datetime_end` (datetime.datetime): Datetime at the end of the calculated restriction period
           (None if ``admin_datetime`` is None).
    """
    required_cols = [
        "pattern_type",
        "theta",
        "c",
        "d",
        "dose_constraint",
        "per_episode",
    ]
    if any(col not in df.columns for col in required_cols):
        raise KeyError("df missing column label in {}".format(required_cols))

    valid_pattern_types = ["repeating", "onceoff"]
    if any(p not in valid_pattern_types for p in df["pattern_type"].tolist()):
        raise ValueError(
            "row in df has pattern_type not in {}".format(valid_pattern_types)
        )

    if admin_datetime is None and "repeating" in df["pattern_type"].unique():
        raise ValueError("row in df has pattern_type repeating and admin_datetime None")

    if num_treatments_in_year < 1.0:
        raise ValueError("num_treatments_in_year less than 1")

    df = df.copy()

    df["dose_constraint_corrected"] = df["dose_constraint"] / num_treatments_in_year
    df.loc[df["per_episode"] == 1, ["dose_constraint_corrected"]] = df[
        "dose_constraint"
    ]

    tau_column = []
    dose_column = []
    datetime_end_column = []
    for _, row in df.iterrows():
        if row["pattern_type"] == "repeating":
            cpat = ContactPatternRepeating(row["theta"], row["c"], row["d"])
        elif row["pattern_type"] == "onceoff":
            cpat = ContactPatternOnceoff(row["theta"], row["c"], row["d"])

        tau, dose, datetime_end = cpat.get_restriction(
            cfit, row["dose_constraint_corrected"], admin_datetime
        )
        tau_column.append(tau)
        dose_column.append(dose)
        datetime_end_column.append(datetime_end)

    df["restriction_period"] = tau_column
    df["dose"] = dose_column
    df["datetime_end"] = datetime_end_column

    return df


def cs_restrictions(
    cfit: clearance.Clearance_1m, num_treatments_in_year, admin_datetime: datetime
) -> pd.DataFrame:
    """Return a dataframe containing the restriction periods for the contact patterns and dose constraints from Cormack & Shearer,
    using the supplied dose rate clearance function, number of treatments anticipated in a year and administration datetime.

    Reference: Cormack J & Shearer J. "Calculation of radiation exposures from patients to whom
    radioactive materials have been administered." Phys Med Biol 1998; 43(3).

    Args:
        cfit (clearance.Clearance_1m):  Dose rate clearance from radioactive person.
        num_treatments_in_year (int or float): Number of treatments anticipated in a year.
        admin_datetime (datetime.datetime): Administration datetime.

    Returns:
        pandas.DataFrame: Dataframe with column labels:
         * `name` (str): Name of the contact pattern and dose constraint pairing.
         * `pattern_type` (str): 'repeating' or 'onceoff', indicating the type of pattern.
         * `theta` (int, float, list or numpy.ndarray): Start times (h) of pattern elements.
         * `c` (int, float, list or numpy.ndarray): Durations (h) of pattern elements.
         * `d` (int, float, list or numpy.ndarray): Distances (m) of pattern elements.
         * `dose_constraint` (int or float): Dose constraint (mSv).
         * `per_episode` (int): 1 if dose constraint is to be treated as per treatment episode, 0 if per annum.
         * `dose_constraint_corrected` (float): Dose constraint (mSv) corrected for number of treatments in a year.
           Only differs from `dose_constraint` if `per_episode` is 0. If `per_episode` is 0, `dose_constraint` is per annum, so
           `dose_constraint_corrected` = `dose_constraint` / ``num_treatments_in_year``.
         * `restriction_period` (float): Calculated restriction period (h).
         * `dose` (float): Dose (mSv) from the pattern with the calculated restriction period.
         * `datetime_end` (datetime.datetime): Datetime at the end of the calculated restriction period.
    """
    return restrictions_for(
        cs_patterns(), cfit, num_treatments_in_year, admin_datetime=admin_datetime
    )
