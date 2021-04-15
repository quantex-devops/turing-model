###############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
###############################################################################

import matplotlib.pyplot as plt
import time

import sys
sys.path.append("..")

from turing_models.turingutils.turing_global_types import TuringSwapTypes
from turing_models.turingutils.turing_date import TuringDate
from turing_models.turingutils.turing_frequency import TuringFrequencyTypes
from turing_models.turingutils.turing_day_count import TuringDayCountTypes
from turing_models.models.turing_model_rates_hw import TuringModelRatesHW

from turing_models.products.rates.turing_ibor_swap import TuringIborSwap
from turing_models.products.rates.turing_ibor_single_curve import TuringIborSingleCurve
from turing_models.market.curves.turing_discount_curve_flat import TuringDiscountCurveFlat
from turing_models.products.bonds.turing_bond import TuringBond
from turing_models.products.bonds.turing_bond_embedded_option import TuringBondEmbeddedOption

from TuringTestCases import TuringTestCases, globalTestCaseMode
testCases = TuringTestCases(__file__, globalTestCaseMode)

plotGraphs = False

###############################################################################


def test_FinBondEmbeddedOptionMATLAB():

    # https://fr.mathworks.com/help/fininst/optembndbyhw.html
    # I FIND THAT THE PRICE CONVERGES TO 102.88 WHICH IS CLOSE TO 102.9127
    # FOUND BY MATLAB ALTHOUGH THEY DO NOT EXAMINE THE ASYMPTOTIC PRICE
    # WHICH MIGHT BE A BETTER MATCH

    settlementDate = TuringDate(1, 1, 2007)
    valuationDate = settlementDate
    
    ###########################################################################

    dcType = TuringDayCountTypes.THIRTY_E_360
    fixedFreq = TuringFrequencyTypes.ANNUAL
    fixedLegType = TuringSwapTypes.PAY
    swap1 = TuringIborSwap(settlementDate, "1Y", fixedLegType, 0.0350, fixedFreq, dcType)
    swap2 = TuringIborSwap(settlementDate, "2Y", fixedLegType, 0.0400, fixedFreq, dcType)
    swap3 = TuringIborSwap(settlementDate, "3Y", fixedLegType, 0.0450, fixedFreq, dcType)
    swaps = [swap1, swap2, swap3]
    discountCurve = TuringIborSingleCurve(valuationDate, [], [], swaps)

    ###########################################################################

    issueDate = TuringDate(1, 1, 2004)
    maturityDate = TuringDate(1, 1, 2010)
    
    coupon = 0.0525
    freqType = TuringFrequencyTypes.ANNUAL
    accrualType = TuringDayCountTypes.ACT_ACT_ICMA
    bond = TuringBond(issueDate, maturityDate, coupon, freqType, accrualType)

    callDates = []
    callPrices = []
    putDates = []
    putPrices = []

    putDate = TuringDate(1, 1, 2008)
    for _ in range(0, 24):
        putDates.append(putDate)
        putPrices.append(100)
        putDate = putDate.addMonths(1)

    testCases.header("BOND PRICE", "PRICE")
    v = bond.cleanPriceFromDiscountCurve(settlementDate, discountCurve)
    testCases.print("Bond Pure Price:", v)

    sigma = 0.01  # basis point volatility
    a = 0.1

    puttableBond = TuringBondEmbeddedOption(issueDate,
                                            maturityDate, coupon,
                                            freqType, accrualType,
                                            callDates, callPrices,
                                            putDates, putPrices)

    testCases.header("TIME", "NumTimeSteps", "BondWithOption", "BondPure")

    timeSteps = range(50, 1000, 10)
    values = []
    for numTimeSteps in timeSteps:
        model = TuringModelRatesHW(sigma, a, numTimeSteps)
        start = time.time()
        v = puttableBond.value(settlementDate, discountCurve, model)
        end = time.time()
        period = end - start
        testCases.print(period, numTimeSteps, v['bondwithoption'],
                        v['bondpure'])
        values.append(v['bondwithoption'])

    if plotGraphs:
        plt.figure()
        plt.plot(timeSteps, values)

###############################################################################


def test_FinBondEmbeddedOptionQUANTLIB():

    # Based on example at the nice blog on Quantlib at
    # http://gouthamanbalaraman.com/blog/callable-bond-quantlib-python.html
    # I get a price of 68.97 for 1000 time steps which is higher than the
    # 68.38 found in blog article. But this is for 40 grid points.
    # Note also that a basis point vol of 0.120 is 12% which is VERY HIGH!

    valuationDate = TuringDate(16, 8, 2016)
    settlementDate = valuationDate.addWeekDays(3)

    ###########################################################################

    discountCurve = TuringDiscountCurveFlat(valuationDate, 0.035,
                                            TuringFrequencyTypes.SEMI_ANNUAL)

    ###########################################################################

    issueDate = TuringDate(15, 9, 2010)
    maturityDate = TuringDate(15, 9, 2022)
    coupon = 0.025
    freqType = TuringFrequencyTypes.QUARTERLY
    accrualType = TuringDayCountTypes.ACT_ACT_ICMA
    bond = TuringBond(issueDate, maturityDate, coupon, freqType, accrualType)

    ###########################################################################
    # Set up the call and put times and prices
    ###########################################################################

    nextCallDate = TuringDate(15, 9, 2016)
    callDates = [nextCallDate]
    callPrices = [100.0]

    for _ in range(1, 24):
        nextCallDate = nextCallDate.addMonths(3)
        callDates.append(nextCallDate)
        callPrices.append(100.0)

    putDates = []
    putPrices = []

    # the value used in blog of 12% bp vol is unrealistic
    sigma = 0.12  # basis point volatility
    a = 0.03

    puttableBond = TuringBondEmbeddedOption(issueDate,
                                            maturityDate, coupon,
                                            freqType, accrualType,
                                            callDates, callPrices,
                                            putDates, putPrices)

    testCases.header("BOND PRICE", "PRICE")
    v = bond.cleanPriceFromDiscountCurve(settlementDate, discountCurve)
    testCases.print("Bond Pure Price:", v)

    testCases.header("TIME", "NumTimeSteps", "BondWithOption", "BondPure")
    timeSteps = range(100, 1000, 100)
    values = []
    for numTimeSteps in timeSteps:
        model = TuringModelRatesHW(sigma, a, numTimeSteps)
        start = time.time()
        v = puttableBond.value(settlementDate, discountCurve, model)
        end = time.time()
        period = end - start
        testCases.print(period, numTimeSteps, v['bondwithoption'], v['bondpure'])
        values.append(v['bondwithoption'])

    if plotGraphs:
        plt.figure()
        plt.title("Puttable Bond Price Convergence")
        plt.plot(timeSteps, values)

###############################################################################


test_FinBondEmbeddedOptionMATLAB()
test_FinBondEmbeddedOptionQUANTLIB()
testCases.compareTestCases()
