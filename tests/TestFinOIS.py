###############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
###############################################################################

import sys
sys.path.append("..")

from financepy.finutils.turing_math import ONE_MILLION
from financepy.products.rates.turing_ois import FinOIS
from financepy.market.curves.turing_discount_curve_flat import FinDiscountCurveFlat
from financepy.finutils.turing_frequency import FinFrequencyTypes
from financepy.finutils.turing_day_count import FinDayCountTypes
from financepy.finutils.turing_date import FinDate
from financepy.finutils.turing_global_types import FinSwapTypes

from FinTestCases import FinTestCases, globalTestCaseMode
testCases = FinTestCases(__file__, globalTestCaseMode)

###############################################################################

def test_FinFixedOIS():

    # Here I follow the example in
    # https://blog.deriscope.com/index.php/en/excel-quantlib-overnight-index-swap

    effectiveDate = FinDate(30, 11, 2018)
    endDate = FinDate(30, 11, 2023)

    endDate = effectiveDate.addMonths(60)
    oisRate = 0.04
    fixedLegType = FinSwapTypes.PAY
    fixedFreqType = FinFrequencyTypes.ANNUAL
    fixedDayCount = FinDayCountTypes.ACT_360
    floatFreqType = FinFrequencyTypes.ANNUAL
    floatDayCount = FinDayCountTypes.ACT_360
    floatSpread = 0.0
    notional = ONE_MILLION
    paymentLag = 1
    
    ois = FinOIS(effectiveDate,
                 endDate,
                 fixedLegType,
                 oisRate,
                 fixedFreqType,
                 fixedDayCount,
                 notional,
                 paymentLag,
                 floatSpread,
                 floatFreqType,
                 floatDayCount)

#    print(ois)

    valueDate = effectiveDate
    marketRate = 0.05
    oisCurve = FinDiscountCurveFlat(valueDate, marketRate,
                                    FinFrequencyTypes.ANNUAL)

    v = ois.value(effectiveDate, oisCurve)
    
#    print(v)
    
#    ois._fixedLeg.printValuation()
#    ois._floatLeg.printValuation()
    
    testCases.header("LABEL", "VALUE")
    testCases.print("SWAP_VALUE", v)
    
###############################################################################

test_FinFixedOIS()
testCases.compareTestCases()
