import numpy as np
from scipy.optimize import fsolve


def _biexp(t, a, b, c, d):
    return a * (b * np.exp(-c * t) + (1 - b) * np.exp(-d * t))


def _biexp_root(t, a, b, c, d, val):
    """for fsolve"""
    return _biexp(t, a, b, c, d) - val


class Clearance_1m:
    """Class for the dose rate clearance function from a radioactive person."""

    def __init__(self, model, model_params, distance):
        """Supply an exponential or biexponential model of the
        dose rate at some distance (between 1 and 3 m) from the
        radioactive person as a function of the time from administration
        of the radioactive substance.

        The dose rate at 1 m is calculated assuming it
        drops off with distance as the inverse 1.5 power.

        Args:
            model (str): Type of clearance, either 'exponential' or 'biexponential'.
            model_params (list): Model parameters in terms of dose rate at ``distance``.
                If ``model`` is 'exponential', ``model_params`` is
                [initial dose rate (uSv/h) at ``distance``, effective half-life (h)].
                If ``model`` is 'biexponential', ``model_params`` is
                [initial dose rate (uSv/h) at ``distance``, fraction of first component (0 to 1),
                half-life (h) of first component, half-life (h) of second component].
            distance (int or float): Distance (m) from radioactive person.

        Raises:
            ValueError: If ``model`` not one of 'exponential' or 'biexponential'.
            TypeError: If ``model_params`` not list.
            ValueError: If ``model_params`` not length 2 for exponential.
            ValueError: If ``model_params`` not length 4 for biexponential.
            TypeError: If element in ``model_params`` not int or float.
            TypeError: If ``distance`` not int or float.
            ValueError: If ``distance`` not between 1 and 3 m, inclusive.
        """
        model_options = ["exponential", "biexponential"]
        if model not in model_options:
            raise ValueError("model not one of {}".format(model_options))
        if not isinstance(model_params, list):
            raise TypeError("model_params not list")
        if model == "exponential":
            if len(model_params) != 2:
                raise ValueError("model_params not length 2 for exponential")
        if model == "biexponential":
            if len(model_params) != 4:
                raise ValueError("model_params not length 4 for biexponential")
        if any(not isinstance(p, (int, float)) for p in model_params):
            raise TypeError("element in model_params not int or float")
        if not isinstance(distance, (int, float)):
            raise TypeError("distance not int or float")
        if not (1.0 <= distance <= 3.0):
            raise ValueError("distance not between 1 and 3 m, inclusive")

        self.model = model
        self.model_params = model_params.copy()
        self.model_params[0] = self.model_params[0] * (distance**1.5)

    def at_timedelta(self, timedelta, init=None):
        """Return the dose rate (uSv/h) at 1 m from the radioactive person at ``timedelta`` (h) after administration.
        If ``init`` is provided and is not None,
        instead evaluate at ``timedelta`` the clearance function with initial value ``init``.

        For example, set ``init`` to the administered activity to return the
        activity on board the person at ``timedelta``.

        Args:
            timedelta (int or float): Time (h) from administration.
            init (int or float, optional): Initial value of clearance function.
                Default is the initial dose rate at 1 m.

        Raises:
            TypeError: If ``timedelta`` not int or float.
            ValueError: If ``timedelta`` less than 0.
            TypeError: If ``init`` not None and not int or float.
            ValueError: If ``init`` not None and less than 0.

        Returns:
            float: The dose rate at 1 m from the radioactive person at ``timedelta``
            if ``init`` is None, else the clearance function
            with initial value ``init`` evaluated at ``timedelta``.
        """
        if not isinstance(timedelta, (int, float)):
            raise TypeError("timedelta not int or float")
        if timedelta < 0.0:
            raise ValueError("timedelta less than 0")

        params = self.model_params.copy()
        if init is not None:
            if not isinstance(init, (int, float)):
                raise TypeError("init not None and not int or float")
            if init < 0.0:
                raise ValueError("init not None and less than 0")
            params[0] = init

        if self.model == "exponential":
            return params[0] * (1 / 2) ** (timedelta / params[1])
        elif self.model == "biexponential":
            return _biexp(
                timedelta,
                params[0],
                params[1],
                np.log(2) / params[2],
                np.log(2) / params[3],
            )

    def get_timedelta(self, val, init=None):
        """Return the time (h) from administration to when the dose rate
        at 1 m from the radioactive person reaches ``val`` (uSv/h).
        If ``init`` is provided and is not None,
        the clearance function is used with initial value
        ``init`` instead of the initial dose rate at 1 m.

        For example, set ``init`` to the administered activity to return the time
        for the activity on board the radioactive person to reach ``val``.

        Args:
            val (int or float): Value to be reached by clearance function.
                If ``init`` is None, this is a dose rate (uSv/h) at 1 m.
            init (int or float, optional): Initial value of the clearance function.
                Default is the initial dose rate at 1 m.

        Raises:
            TypeError: If ``val`` not int or float.
            ValueError: If ``val`` not greater than 0.
            TypeError: If ``init`` not None and not int or float.
            ValueError: If ``init`` not None and not greater than 0.
            ValueError: If ``val`` greater than or equal to initial value
                of clearance function.

        Returns:
            float: Time (h) from administration to when the clearance
            function reaches ``val``.
        """
        if not isinstance(val, (int, float)):
            raise TypeError("val not int or float")
        if val <= 0.0:
            raise ValueError("val not greater than 0")

        params = self.model_params.copy()
        if init is not None:
            if not isinstance(init, (int, float)):
                raise TypeError("init not None and not int or float")
            if init <= 0.0:
                raise ValueError("init not None and not greater than 0")
            params[0] = init

        if val >= params[0]:
            raise ValueError(
                "val greater than or equal to initial value of clearance function"
            )

        # for biexp, try initial guesses 0 h, 24 h, 48 h, etc until fsolve finds a solution
        hrs0 = 0
        while True:
            if self.model == "exponential":
                hrs = params[1] * np.log(params[0] / val) / np.log(2)
            elif self.model == "biexponential":
                hrs = fsolve(
                    _biexp_root,
                    hrs0,
                    args=(
                        params[0],
                        params[1],
                        np.log(2) / params[2],
                        np.log(2) / params[3],
                        val,
                    ),
                )[0]

            if hrs != hrs0:
                break

            hrs0 += 24.0

        return hrs

    def residence_time(self):
        """Return the whole body residence time (a.k.a. time-integrated activity coefficient)
        for the radioactive person.

        Returns:
            float: Residence time (h).
        """
        if self.model == "exponential":
            return self.model_params[1] / np.log(2)
        elif self.model == "biexponential":
            fraction1 = self.model_params[1]
            return (
                (fraction1 * self.model_params[2])
                + ((1.0 - fraction1) * self.model_params[3])
            ) / np.log(2)
