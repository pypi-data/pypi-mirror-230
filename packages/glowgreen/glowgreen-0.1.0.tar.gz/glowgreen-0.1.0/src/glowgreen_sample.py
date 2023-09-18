from glowgreen import ContactPatternRepeating

theta = [7.5, 16]  # Start times (h) of pattern elements
c = [0.75, 3.5]  # Durations (h) of pattern elements
d = [0.3, 1]  # Distances (m) of pattern elements
cpat = ContactPatternRepeating(theta, c, d)

import matplotlib.pyplot as plt
plt.rcParams["figure.dpi"] = 200
cpat.plot()

from glowgreen import Clearance_1m

dose_rate_init_2m = 60  # uSv/h
fraction1 = 0.3
half_life1 = 8  # h
half_life2 = 30  # h
distance = 2  # m
cfit = Clearance_1m(
    "biexponential", [dose_rate_init_2m, fraction1, half_life1, half_life2], distance
)

from datetime import datetime, timedelta

dose_constraint = 1  # mSv
admin_datetime = datetime(day=25, month=12, year=2021, hour=10, minute=30)
restriction_period, dose, datetime_end = cpat.get_restriction(
    cfit, dose_constraint, admin_datetime
)

assert dose <= dose_constraint
assert datetime_end == admin_datetime + timedelta(hours=restriction_period)

print(restriction_period, dose, datetime_end)

cpat.plot(cfit=cfit, dose_constraint=dose_constraint, admin_datetime=admin_datetime)

from glowgreen import cs_restrictions

num_treatments_in_year = 2
df = cs_restrictions(cfit, num_treatments_in_year, admin_datetime)

import pandas as pd
with pd.option_context('display.max_colwidth', None):
    print(df[["name", "datetime_end"]])
