###############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
###############################################################################

import sys
sys.path.append("..")

from financepy.market.curves.turing_discount_curve_flat import TuringDiscountCurveFlat
from financepy.finutils.turing_date import TuringDate
from financepy.finutils.turing_frequency import TuringFrequencyTypes

from TuringTestCases import TuringTestCases, globalTestCaseMode
testCases = TuringTestCases(__file__, globalTestCaseMode)

##############################################################################

def test_FinFlatCurve():

    curveDate = TuringDate(1, 1, 2019)
    months = range(1, 60, 3)
    dates = curveDate.addMonths(months)
    testCases.header("COMPOUNDING", "DFS")
    compounding = TuringFrequencyTypes.CONTINUOUS

    flatCurve = TuringDiscountCurveFlat(curveDate, 0.05, compounding)
    dfs = flatCurve.df(dates)
    testCases.print(compounding, dfs)

    compounding = TuringFrequencyTypes.ANNUAL
    flatCurve = TuringDiscountCurveFlat(curveDate, 0.05, compounding)
    dfs = flatCurve.df(dates)
    testCases.print(compounding, dfs)

    compounding = TuringFrequencyTypes.SEMI_ANNUAL
    flatCurve = TuringDiscountCurveFlat(curveDate, 0.05, compounding)
    dfs = flatCurve.df(dates)
    testCases.print(compounding, dfs)

    compounding = TuringFrequencyTypes.QUARTERLY
    flatCurve = TuringDiscountCurveFlat(curveDate, 0.05, compounding)
    dfs = flatCurve.df(dates)
    testCases.print(compounding, dfs)

    compounding = TuringFrequencyTypes.MONTHLY
    flatCurve = TuringDiscountCurveFlat(curveDate, 0.05, compounding)
    dfs = flatCurve.df(dates)
    testCases.print(compounding, dfs)

###############################################################################


test_FinFlatCurve()
testCases.compareTestCases()
