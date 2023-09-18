glowgreen
=========

Introduction
************

``glowgreen`` is a small Python package for calculating the radiation dose received by an individual 
who shares a pattern of close contact with a radioactive person.
Two kinds of contact patterns are supported: onceoff patterns and infinitely repeating diurnal patterns.
The dose from the contact pattern can be calculated taking into account a period of delay 
from the time of administration of the radioactive substance to when the contact pattern is started or resumed.
A method is also provided to calculate the shortest delay required to satisfy a given dose constraint, 
referred to as the restriction period.
At this stage, the clearance of radioactivity from the patient must be either exponential or biexponential.

Installation
************

Install the package from the Python Package Index (PyPI) using pip:

    python -m pip install glowgreen


Example usage
*************

Define a contact pattern
########################

Create a onceoff pattern or a diurnal repeating pattern. 
For example, a diurnal repeating pattern consisting of contact from 7:30 to 8:15 AM at a distance of 0.3 m 
and 4:00 to 7:30 PM at 1 m can be created as follows:

.. code-block:: python

    from glowgreen import ContactPatternRepeating

    theta = [7.5, 16]  # Start times (h) of pattern elements
    c = [0.75, 3.5]    # Durations (h) of pattern elements
    d = [0.3, 1]       # Distances (m) of pattern elements
    cpat = ContactPatternRepeating(theta, c, d)

.. note::
    For repeating patterns, `theta` is defined with respect to midnight by default.
    Conversely, for onceoff patterns ``ContactPatternOnceoff``, `theta` is defined with respect to the end of the delay period.

Generate a plot of the pattern with:

.. code-block:: python

    cpat.plot()

.. image:: docs_cpat.png
   :width: 600
   :align: center
   :alt: Plot of contact pattern

Define a dose rate clearance function
#####################################
Supply an exponential or biexponential model of the dose rate at some distance (between 1 and 3 m) 
from the radioactive person as a function of the time from administration of the radioactive substance.
For example:

.. code-block:: python

    from glowgreen import Clearance_1m

    dose_rate_init_2m = 60  # uSv/h
    fraction1 = 0.3         # 0 to 1
    half_life1 = 8          # h
    half_life2 = 30         # h
    distance = 2            # m
    cfit = Clearance_1m('biexponential', [dose_rate_init_2m, fraction1, half_life1, half_life2], 
		distance)

Values must be given in the units shown.

.. note::
    For exponential models, the model parameter list consists of the initial dose rate at `distance` and the effective half life, in that order.

Calculate the restriction period
################################
How soon after administration can a person resume this infinitely repeating contact pattern with the radioactive person, 
without their lifetime dose exceeding a given dose constraint? 

.. code-block:: python

    from datetime import datetime, timedelta

    dose_constraint = 1  # mSv
    admin_datetime = datetime(day=25, month=12, year=2021, hour=10, minute=30)
    restriction_period, dose, datetime_end = cpat.get_restriction(cfit, dose_constraint, 
        admin_datetime)

    assert dose <= dose_constraint
    assert datetime_end == admin_datetime + timedelta(hours=restriction_period)

Printing the results::

    >>> restriction_period
    29.5 
    >>> dose
    0.9399700449166117 
    >>> datetime_end
    2021-12-26 16:00:00


In this case, the restriction period is 29.5 h for a lifetime dose of 0.94 mSv.
The pattern can resume the next day starting with the contact from 4:00 to 7:30 PM.

Generate a plot of the lifetime dose as a function of the delay period by supplying additional arguments to the plot method:

.. code-block:: python

    cpat.plot(cfit=cfit, dose_constraint=dose_constraint, admin_datetime=admin_datetime)

.. image:: docs_cpat_dose.png
   :width: 600
   :align: center
   :alt: Plots of contact pattern and dose versus delay period

.. note::
    For repeating patterns, the end of the calculated restriction period coincides with the start of a pattern element by default, 
    so it is clear that contact can resume at the end of the restriction period.

Standard contact patterns
#########################
Restriction periods can be calculated for the "real-world" contact patterns published by 
`Cormack & Shearer <https://iopscience.iop.org/article/10.1088/0031-9155/43/3/003>`_,
along with appropriate dose constraints, using:

.. code-block:: python
    
    from glowgreen import cs_restrictions

    num_treatments_in_year = 2
    df = cs_restrictions(cfit, num_treatments_in_year, admin_datetime)

Then we have::

    >>> import pandas as pd
    >>> with pd.option_context('display.max_colwidth', None):
    ...     df[['name', 'datetime_end']]
    ...
                                                                                name               datetime_end
    0                                                     Caring for infants (normal) 2021-12-31 23:00:00.000000
    1                                          Caring for infants (demanding or sick) 2022-01-03 03:00:00.000000
    2                     Prolonged close contact (>15min) with 2-5 year old children 2022-01-02 06:00:00.000000
    3                    Prolonged close contact (>15min) with 5-15 year old children 2021-12-31 08:00:00.000000
    4                       Sleeping with another person (includes pregnant or child) 2021-12-31 03:00:00.000000
    5                                                Sleeping with informed supporter 2021-12-27 02:00:00.000000
    6               Sleeping with person and prolonged daytime close contact (>15min) 2021-12-31 12:00:00.000000
    7   Sleeping with informed supporter and prolonged daytime close contact (>15min) 2021-12-27 06:00:00.000000
    8                  Prolonged close contact (>15min) with adult friends and family 2021-12-30 08:00:00.000000
    9                            Prolonged close contact (>15min) with pregnant women 2021-12-30 08:00:00.000000
    10      Prolonged close contact (>15min) with informed persons caring for patient 2021-12-27 07:00:00.000000
    11                                       Cinema, theatre visits; social functions 2021-12-27 15:00:00.000000
    12                                        Daily public transport to and from work 2021-12-28 17:00:00.000000
    13          Return to work involving prolonged close contact (>15min) with others 2021-12-29 09:00:00.000000
    14      Return to work not involving prolonged close contact (>15min) with others 2021-12-27 15:00:00.000000
    15                                             Work with radiosensitive materials 2021-12-31 16:00:00.000000
    16                                                               Return to school 2021-12-29 09:00:00.000000
    17                                      A single 24-hour trip on public transport 2021-12-31 08:33:45.528190


See :ref:`API reference` for additional package features and more detailed information.


Development
***********
`<https://github.com/SAMI-Medical-Physics/glowgreen>`_ 


Publications
************
Papers that use glowgreen:

* Close contact restriction periods for patients who received radioactive iodine-131 therapy for differentiated thyroid cancer, J. C. Forster et al., In preparation.
