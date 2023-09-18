from datetime import datetime
from glowgreen import Clearance_1m, cs_restrictions, cs_patterns, restrictions_for


def test_cs_patterns():
    cs_patterns()


def test_restrictions_for():
    df_base = cs_patterns()

    admin_datetime = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    model = "exponential"
    dose_rate_xm_init = 60.0
    effective_half_life = 11.0
    model_parameters = [dose_rate_xm_init, effective_half_life]
    measurement_distance = 2.0
    cfit = Clearance_1m(model, model_parameters, measurement_distance)

    num_treatments_in_year = 4

    df = restrictions_for(
        df_base, cfit, num_treatments_in_year, admin_datetime=admin_datetime
    )

    required_cols = ["restriction_period", "dose", "datetime_end"]
    for col in required_cols:
        assert col in df.columns


def test_cs_restrictions():
    admin_datetime = datetime(year=2021, month=10, day=25, hour=10, minute=15)

    model = "exponential"
    dose_rate_xm_init = 60.0
    effective_half_life = 11.0
    model_parameters = [dose_rate_xm_init, effective_half_life]
    measurement_distance = 2.0
    cfit = Clearance_1m(model, model_parameters, measurement_distance)

    num_treatments_in_year = 4

    cs_restrictions(cfit, num_treatments_in_year, admin_datetime)
