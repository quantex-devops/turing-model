import sys
sys.path.append("..")

import numpy as np

from turing_models.market.curves.discount_curve_flat import TuringDiscountCurveFlat
from turing_models.market.volatility.fx_vol_surface import TuringFXVolSurface
from turing_models.market.volatility.fx_vol_surface_plus import TuringFXVolSurfacePlus
from turing_models.market.volatility.fx_vol_surface_plus import TuringFXATMMethod
from turing_models.market.volatility.fx_vol_surface_plus import TuringFXDeltaMethod
from turing_models.market.volatility.fx_vol_surface_vv import TuringFXVolSurfaceVV
from turing_models.utilities.turing_date import TuringDate
from turing_models.models.model_volatility_fns import TuringVolFunctionTypes

# from TuringTestCases import TuringTestCases, globalTestCaseMode
# testCases = TuringTestCases(__file__, globalTestCaseMode)

import matplotlib.pyplot as plt

###############################################################################

PLOT_GRAPHS = False

###############################################################################
# TODO: ADD LOGGING TO TEST CASES
###############################################################################

def test_FinFXMktVolSurface1(verboseCalibration):

    ###########################################################################

    if 1 == 1:

        # Example from Book extract by Iain Clark using Tables 3.3 and 3.4
        # print("EURUSD EXAMPLE CLARK")

        valueDate = TuringDate(10, 4, 2020)

        forName = "EUR"
        domName = "USD"
        forCCRate = 0.03460  # EUR
        domCCRate = 0.02940  # USD

        domDiscountCurve = TuringDiscountCurveFlat(valueDate, domCCRate)
        forDiscountCurve = TuringDiscountCurveFlat(valueDate, forCCRate)

        currencyPair = forName + domName
        spotFXRate = 1.3465

        tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y']
        atmVols = [21.00, 21.00, 20.750, 19.400, 18.250, 17.677]
        marketStrangle25DeltaVols = [0.65, 0.75, 0.85, 0.90, 0.95, 0.85]
        riskReversal25DeltaVols = [-0.20, -0.25, -0.30, -0.50, -0.60, -0.562]
        marketStrangle10DeltaVols = [2.433, 2.83, 3.228, 3.485, 3.806, 3.208]
        riskReversal10DeltaVols = [-1.258, -1.297, -1.332, -1.408, -1.359, -1.208]

        notionalCurrency = forName

        atmMethod = TuringFXATMMethod.FWD_DELTA_NEUTRAL
        deltaMethod = TuringFXDeltaMethod.SPOT_DELTA
        volFunctionType = TuringVolFunctionTypes.CLARK5
        alpha = 0.5 # FIT WINGS AT 10D if ALPHA = 1.0

        fxMarketPlus = TuringFXVolSurfacePlus(valueDate,
                                              spotFXRate,
                                              currencyPair,
                                              notionalCurrency,
                                              domDiscountCurve,
                                              forDiscountCurve,
                                              tenors,
                                              atmVols,
                                              marketStrangle25DeltaVols,
                                              riskReversal25DeltaVols,
                                              marketStrangle10DeltaVols,
                                              riskReversal10DeltaVols,
                                              alpha,
                                              atmMethod,
                                              deltaMethod,
                                              volFunctionType)

        fxMarketPlus.checkCalibration(False)

        if 1==0: # PLOT_GRAPHS:

            fxMarketPlus.plotVolCurves()

            plt.figure()

            dbns = fxMarketPlus.impliedDbns(0.5, 2.0, 1000)

            for i in range(0, len(dbns)):
                plt.plot(dbns[i]._x, dbns[i]._densitydx)
                plt.title(volFunctionType)
                print("SUM:", dbns[i].sum())

###############################################################################


def test_FinFXMktVolSurface2(verboseCalibration):

        #print("==============================================================")

        # Example from Book extract by Iain Clarke using Tables 3.3 and 3.4
        # print("EURJPY EXAMPLE CLARK")

        valueDate = TuringDate(10, 4, 2020)

        forName = "EUR"
        domName = "JPY"
        forCCRate = 0.0294  # EUR
        domCCRate = 0.0171  # USD

        domDiscountCurve = TuringDiscountCurveFlat(valueDate, domCCRate)
        forDiscountCurve = TuringDiscountCurveFlat(valueDate, forCCRate)

        currencyPair = forName + domName
        spotFXRate = 90.72

        tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y']
        atmVols = [21.50, 20.50, 19.85, 18.00, 15.95, 14.009]
        marketStrangle25DeltaVols = [0.35, 0.325, 0.300, 0.225, 0.175, 0.100]
        riskReversal25DeltaVols = [-8.350, -8.650, -8.950, -9.250, -9.550, -9.500]
        marketStrangle10DeltaVols = [3.704, 4.047, 4.396, 4.932, 5.726, 5.709]
        riskReversal10DeltaVols = [-15.855, -16.467, -17.114, -17.882, -18.855, -18.217]
        alpha = 0.50 # Equally fit 10 and 25 Delta

        notionalCurrency = forName

        atmMethod = TuringFXATMMethod.FWD_DELTA_NEUTRAL_PREM_ADJ
        deltaMethod = TuringFXDeltaMethod.SPOT_DELTA_PREM_ADJ
        volFunctionType = TuringVolFunctionTypes.CLARK5

        fxMarketPlus = TuringFXVolSurfacePlus(valueDate,
                                              spotFXRate,
                                              currencyPair,
                                              notionalCurrency,
                                              domDiscountCurve,
                                              forDiscountCurve,
                                              tenors,
                                              atmVols,
                                              marketStrangle25DeltaVols,
                                              riskReversal25DeltaVols,
                                              marketStrangle10DeltaVols,
                                              riskReversal10DeltaVols,
                                              alpha,
                                              atmMethod,
                                              deltaMethod,
                                              volFunctionType)

#        fxMarketPlus.checkCalibration(True)

        if PLOT_GRAPHS:
            fxMarketPlus.plotVolCurves()

            plt.figure()

            dbns = fxMarketPlus.impliedDbns(30, 120, 1000)

            for i in range(0, len(dbns)):
                plt.plot(dbns[i]._x, dbns[i]._densitydx)
                plt.title(volFunctionType)
                print("SUM:", dbns[i].sum())


###############################################################################

def test_FinFXMktVolSurface3(verboseCalibration):

    ###########################################################################

    if 1 == 1:

        # Example from Book extract by Iain Clark using Tables 4.4 and 4.5
        # where we examine the calibration to a full surface in Chapter 4

        valueDate = TuringDate(10, 4, 2020)

        forName = "EUR"
        domName = "USD"
        forCCRate = 0.03460  # EUR
        domCCRate = 0.02940  # USD

        domDiscountCurve = TuringDiscountCurveFlat(valueDate, domCCRate)
        forDiscountCurve = TuringDiscountCurveFlat(valueDate, forCCRate)

        currencyPair = forName + domName
        spotFXRate = 1.3465

        tenors = ['1Y', '2Y']
        atmVols = [18.250, 17.677]
        marketStrangle25DeltaVols = [0.95, 0.85]
        riskReversal25DeltaVols = [-0.60, -0.562]
        marketStrangle10DeltaVols = [3.806, 3.208]
        riskReversal10DeltaVols = [-1.359, -1.208]

        notionalCurrency = forName

        # I HAVE NO YET MADE DELTA METHOD A VECTOR FOR EACH TERM AS I WOULD
        # NEED TO DO AS DESCRIBED IN CLARK PAGE 70
        
        atmMethod = TuringFXATMMethod.FWD_DELTA_NEUTRAL
        deltaMethod = TuringFXDeltaMethod.FORWARD_DELTA # THIS IS DIFFERENT
        volFunctionType = TuringVolFunctionTypes.CLARK5
        alpha = 0.5 # FIT WINGS AT 10D if ALPHA = 1.0

        fxMarketPlus = TuringFXVolSurfacePlus(valueDate,
                                              spotFXRate,
                                              currencyPair,
                                              notionalCurrency,
                                              domDiscountCurve,
                                              forDiscountCurve,
                                              tenors,
                                              atmVols,
                                              marketStrangle25DeltaVols,
                                              riskReversal25DeltaVols,
                                              marketStrangle10DeltaVols,
                                              riskReversal10DeltaVols,
                                              alpha,
                                              atmMethod,
                                              deltaMethod,
                                              volFunctionType)

        fxMarketPlus.checkCalibration(False)

        if 1==0: # PLOT_GRAPHS:

            fxMarketPlus.plotVolCurves()

            plt.figure()

            dbns = fxMarketPlus.impliedDbns(0.5, 2.0, 1000)

            for i in range(0, len(dbns)):
                plt.plot(dbns[i]._x, dbns[i]._densitydx)
                plt.title(volFunctionType)
                print("SUM:", dbns[i].sum())

        # Test interpolation
        
        years = [1.0, 1.5, 2.0]
        dates = valueDate.addYears(years)

        strikes = np.linspace(1.0, 2.0, 20)

        if 1==1:
            volSurface = []        
            for k in strikes:
                volSmile = []
                for dt in dates:
                    vol = fxMarketPlus.volatilityFromStrikeDate(k, dt)
                    volSmile.append(vol*100.0)
                    
                    print(k, dt, vol*100.0)
                volSurface.append(volSmile)
    
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(years, strikes)
            zs = np.array(volSurface)
            Z = zs.reshape(X.shape)
            
            ax.plot_surface(X, Y, Z)
            
            ax.set_xlabel('Years')
            ax.set_ylabel('Strikes')
            ax.set_zlabel('Volatility')
            
            plt.show()

        #######################################################################

        deltas = np.linspace(0.10, 0.90, 17)

        if 1==1:
            volSurface = []        
            for delta in deltas:
                volSmile = []
                for dt in dates:
                    (vol, k) = fxMarketPlus.volatilityFromDeltaDate(delta, dt)
                    volSmile.append(vol*100.0)
                    print(delta, k, dt, vol*100.0)

                volSurface.append(volSmile)
    
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(years, deltas)
            zs = np.array(volSurface)
            Z = zs.reshape(X.shape)
            
            ax.plot_surface(X, Y, Z)
            
            ax.set_xlabel('Years')
            ax.set_ylabel('Delta')
            ax.set_zlabel('Volatility')
            plt.title("EURUSD Volatility Surface")
            plt.show()

###############################################################################


def test_FinFXMktVolSurface4(verboseCalibration):

    ###########################################################################
    # Here I remove the 25D Vols
    ###########################################################################
    
    if 1 == 1:

        # Example from Book extract by Iain Clark using Tables 3.3 and 3.4
        # print("EURUSD EXAMPLE CLARK")

        valueDate = TuringDate(2020, 4, 10)

        forName = "EUR"
        domName = "USD"
        forCCRate = 0.03460  # EUR
        domCCRate = 0.02940  # USD

        domDiscountCurve = TuringDiscountCurveFlat(valueDate, domCCRate)
        forDiscountCurve = TuringDiscountCurveFlat(valueDate, forCCRate)

        currencyPair = forName + domName
        spotFXRate = 1.3465

        tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y']
        atmVols = [21.00, 21.00, 20.750, 19.400, 18.250, 17.677]
        marketStrangle25DeltaVols = [0.65, 0.75, 0.85, 0.90, 0.95, 0.85]
        riskReversal25DeltaVols = [-0.20, -0.25, -0.30, -0.50, -0.60, -0.562]
        marketStrangle10DeltaVols = [2.433, 2.83, 3.228, 3.485, 3.806, 3.208]
        riskReversal10DeltaVols = [-1.258, -1.297, -1.332, -1.408, -1.359, -1.208]
        
        atmVols = [x/100 for x in atmVols]
        marketStrangle25DeltaVols = [x/100 for x in marketStrangle25DeltaVols]
        riskReversal25DeltaVols = [x/100 for x in riskReversal25DeltaVols]
        marketStrangle10DeltaVols = [x/100 for x in marketStrangle10DeltaVols]
        riskReversal10DeltaVols = [x/100 for x in riskReversal10DeltaVols]

        # marketStrangle25DeltaVols = None
        # riskReversal25DeltaVols = None
        
        notionalCurrency = forName

        atmMethod = TuringFXATMMethod.FWD_DELTA_NEUTRAL
        deltaMethod = TuringFXDeltaMethod.SPOT_DELTA
        volFunctionType = TuringVolFunctionTypes.VANNA_VOLGA
        alpha = 1.00 # FIT WINGS AT 10D if ALPHA = 1.0

        fxMarketPlus = TuringFXVolSurfaceVV(valueDate,
                                              spotFXRate,
                                              currencyPair,
                                              domDiscountCurve,
                                              forDiscountCurve,
                                              tenors,
                                              atmVols,
                                              marketStrangle25DeltaVols,
                                              riskReversal25DeltaVols,
                                              marketStrangle10DeltaVols,
                                              riskReversal10DeltaVols,
                                              alpha,
                                              atmMethod,
                                              deltaMethod,
                                              volFunctionType)

        # fxMarketPlus.checkCalibration(False)

        years = [1.0/12.0, 2./12., 0.25, 0.5, 1.0, 2.0]

        dates = valueDate.addYears(years)

        deltas = np.linspace(0.10, 0.90, 17)

        if 1==1:
            volSurface = []        
            for delta in deltas:
                volSmile = []
                for dt in dates:
                    (vol, k) = fxMarketPlus.volatilityFromDeltaDate(delta, dt)
                    volSmile.append(vol*100.0)
                    print(delta, k, dt, vol*100.0)

                volSurface.append(volSmile)
    
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(years, deltas)
            zs = np.array(volSurface)
            Z = zs.reshape(X.shape)
            
            ax.plot_surface(X, Y, Z)
            
            ax.set_xlabel('Years')
            ax.set_ylabel('Delta')
            ax.set_zlabel('Volatility')
            plt.title("EURUSD Volatility Surface")
            plt.show()
###############################################################################


def test_FinFXMktVolSurface5(verboseCalibration):

    ###########################################################################
    # Here I remove the 10D Vols
    ###########################################################################
    
    if 1 == 1:

        # Example from Book extract by Iain Clark using Tables 3.3 and 3.4
        # print("EURUSD EXAMPLE CLARK")

        valueDate = TuringDate(2020, 10, 4)

        forName = "EUR"
        domName = "USD"
        forCCRate = 0.03460  # EUR
        domCCRate = 0.02940  # USD

        domDiscountCurve = TuringDiscountCurveFlat(valueDate, domCCRate)
        forDiscountCurve = TuringDiscountCurveFlat(valueDate, forCCRate)

        currencyPair = forName + domName
        spotFXRate = 1.3465

        tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y']
        atmVols = [21.00, 21.00, 20.750, 19.400, 18.250, 17.677]
        marketStrangle25DeltaVols = [0.65, 0.75, 0.85, 0.90, 0.95, 0.85]
        riskReversal25DeltaVols = [-0.20, -0.25, -0.30, -0.50, -0.60, -0.562]
        marketStrangle10DeltaVols = [2.433, 2.83, 3.228, 3.485, 3.806, 3.208]
        riskReversal10DeltaVols = [-1.258, -1.297, -1.332, -1.408, -1.359, -1.208]

        # marketStrangle10DeltaVols = None
        # riskReversal10DeltaVols = None
        
        notionalCurrency = forName

        atmMethod = TuringFXATMMethod.FWD_DELTA_NEUTRAL
        deltaMethod = TuringFXDeltaMethod.SPOT_DELTA
        volFunctionType = TuringVolFunctionTypes.CLARK
        alpha = 0.0 # FIT WINGS AT 10D if ALPHA = 1.0

        fxMarketPlus = TuringFXVolSurfaceVV(valueDate,
                                              spotFXRate,
                                              currencyPair,
                                              domDiscountCurve,
                                              forDiscountCurve,
                                              tenors,
                                              atmVols,
                                              marketStrangle25DeltaVols,
                                              riskReversal25DeltaVols,
                                              marketStrangle10DeltaVols,
                                              riskReversal10DeltaVols,
                                              alpha,
                                              atmMethod,
                                              deltaMethod,
                                              volFunctionType)
        fxMarketPlus.plotVolCurves()

        # fxMarketPlus.checkCalibration(False)

###############################################################################


import time

if __name__ == '__main__':

    start = time.time()

    verboseCalibration = False

    # test_FinFXMktVolSurface1(verboseCalibration)
    # test_FinFXMktVolSurface2(verboseCalibration)
    # test_FinFXMktVolSurface3(verboseCalibration)
    test_FinFXMktVolSurface4(verboseCalibration)
    # test_FinFXMktVolSurface5(verboseCalibration)
    
    end = time.time()
    
    elapsed = end - start
#    print("Elapsed Time:", elapsed)
    # testCases.compareTestCases()
