from typing import Union

import numpy as np
from numba import njit

from turing_models.utilities.mathematics import covar
from turing_models.utilities.global_variables import gDaysInYear
from turing_models.utilities.frequency import TuringFrequencyTypes
from turing_models.utilities.error import TuringError

from turing_models.utilities.global_types import TuringOptionTypes
from turing_models.utilities.helper_functions import checkArgumentTypes, labelToString
from turing_models.utilities.turing_date import TuringDate
from turing_models.models.model import TuringModel
from turing_models.market.curves.discount_curve import TuringDiscountCurve
from turing_models.models.model_black_scholes import TuringModelBlackScholes

from turing_models.utilities.mathematics import N


bump = 1e-4


class TuringEquitySnowBallOption:

    def __init__(self,
                 expiry_date: TuringDate,
                 knock_out_price: float,
                 knock_in_price: float,
                 notional: float,
                 coupon_rate: float,
                 observation_frequency: TuringFrequencyTypes = TuringFrequencyTypes.MONTHLY):
        """用到期日期、敲出价格、敲入价格、敲出观察频率、名义本金和票面利率
        创建一个雪球期权对象"""

        checkArgumentTypes(self.__init__, locals())

        self._expiry_date = expiry_date
        self.k1 = knock_out_price
        self.k2 = knock_in_price
        self.obs_freq = observation_frequency
        self.notional = notional
        self.coupon_rate = coupon_rate

    def value(self,
              value_date: TuringDate,
              stock_price: float,
              discount_curve: TuringDiscountCurve,
              dividend_curve: TuringDiscountCurve,
              model: TuringModel,
              num_paths: int = 10000,
              seed: int = 4242):
        """用蒙特卡洛方法对雪球期权进行估值计算"""

        texp = (self._expiry_date - value_date) / gDaysInYear

        df = discount_curve.df(self._expiry_date)
        r = -np.log(df)/texp

        dq = dividend_curve.df(self._expiry_date)
        q = -np.log(dq)/texp

        vol = model._volatility

        np.random.seed(seed)
        mu = r - q
        v2 = vol**2
        n = int(self._expiry_date - value_date)
        dt = 1/gDaysInYear
        s0 = stock_price
        date_list = []
        date_list.append(value_date)
        for i in range(1, n + 1):
            dateinc = value_date.addDays(i)
            date_list.append(dateinc)

        s_1 = np.empty(n+1)
        s_2 = np.empty(n+1)
        s_1[0] = s_2[0] = s0
        s_1_pd = np.empty(num_paths)
        s_2_pd = np.empty(num_paths)

        for j in range(0, num_paths):
            g = np.random.normal(0.0, 1.0, size=n)
            syb_up_1 = 0
            syb_up_2 = 0
            syb_down_1 = 0
            syb_down_2 = 0

            for ip in range(1, n+1):
                s_1[ip] = s_1[ip-1] * np.exp((mu - v2 / 2.0) *
                                             dt + g[ip-1] * np.sqrt(dt) *
                                             vol)
                if s_1[ip] < self.k2:
                    syb_down_1 = 1

                if (self.obs_freq == TuringFrequencyTypes.MONTHLY and
                    date_list[ip]._d == self._expiry_date._d and
                        s_1[ip] >= self.k1):
                    syb_up_1 = 1
                    payoff_discounted = (self.notional * self.coupon_rate * ip / gDaysInYear) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_1_pd[j] = payoff_discounted

                    break
                if ip == n and syb_up_1 == 0 and syb_down_1 == 0:
                    payoff_discounted = (self.notional * self.coupon_rate * ip / gDaysInYear) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_1_pd[j] = payoff_discounted
                elif ip == n and syb_up_1 == 0 and syb_down_1 == 1:
                    payoff_discounted = -self.notional * (1 - s_1[ip] / s0) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_1_pd[j] = payoff_discounted
            for ip in range(1, n+1):
                s_2[ip] = s_2[ip-1] * np.exp((mu - v2 / 2.0) *
                                             dt - g[ip-1] * np.sqrt(dt) *
                                             vol)
                if s_2[ip] < self.k2:
                    syb_down_2 = 1

                if (self.obs_freq == TuringFrequencyTypes.MONTHLY and
                    date_list[ip]._d == self._expiry_date._d and
                        s_2[ip] >= self.k1):
                    syb_up_2 = 1
                    payoff_discounted = (self.notional * self.coupon_rate * ip / gDaysInYear) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_2_pd[j] = payoff_discounted

                    break
                if ip == n and syb_up_2 == 0 and syb_down_2 == 0:
                    payoff_discounted = (self.notional * self.coupon_rate * ip / gDaysInYear) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_2_pd[j] = payoff_discounted
                elif ip == n and syb_up_2 == 0 and syb_down_2 == 1:
                    payoff_discounted = -self.notional * (1 - s_2[ip] / s0) * \
                        np.exp(-r * ip / gDaysInYear)
                    s_2_pd[j] = payoff_discounted

        return 0.5 * np.mean(s_1_pd + s_2_pd)

    def delta(self,
              value_date: TuringDate,
              stock_price: float,
              discount_curve: TuringDiscountCurve,
              dividend_curve: TuringDiscountCurve,
              model):
        ''' Calculation of option delta by perturbation of stock price and
        revaluation. '''
        v = self.value(value_date, stock_price, discount_curve,
                       dividend_curve, model)

        vBumped = self.value(value_date, stock_price + bump, discount_curve,
                             dividend_curve, model)

        delta = (vBumped - v) / bump
        return delta

###############################################################################

    def gamma(self,
              value_date: TuringDate,
              stock_price: float,
              discount_curve: TuringDiscountCurve,
              dividend_curve: TuringDiscountCurve,
              model):
        ''' Calculation of option gamma by perturbation of stock price and
        revaluation. '''

        v = self.value(value_date, stock_price, discount_curve,
                       dividend_curve, model)

        vBumpedDn = self.value(value_date, stock_price - bump, discount_curve,
                               dividend_curve, model)

        vBumpedUp = self.value(value_date, stock_price + bump, discount_curve,
                               dividend_curve, model)

        gamma = (vBumpedUp - 2.0 * v + vBumpedDn) / bump / bump
        return gamma

###############################################################################

    def vega(self,
             value_date: TuringDate,
             stock_price: float,
             discount_curve: TuringDiscountCurve,
             dividend_curve: TuringDiscountCurve,
             model):
        ''' Calculation of option vega by perturbing vol and revaluation. '''

        v = self.value(value_date, stock_price, discount_curve,
                       dividend_curve, model)

        model = TuringModelBlackScholes(model._volatility + bump)

        vBumped = self.value(value_date, stock_price, discount_curve,
                             dividend_curve, model)

        vega = (vBumped - v) / bump
        return vega

###############################################################################

    def theta(self,
              value_date: TuringDate,
              stock_price: float,
              discount_curve: TuringDiscountCurve,
              dividend_curve: TuringDiscountCurve,
              model):
        ''' Calculation of option theta by perturbing value date by one
        calendar date (not a business date) and then doing revaluation and
        calculating the difference divided by dt = 1 / gDaysInYear. '''

        v = self.value(value_date, stock_price,
                       discount_curve,
                       dividend_curve, model)

        nextDate = value_date.addDays(1)

        # Need to do this carefully.

        discount_curve._valuationDate = nextDate
        bump = (nextDate - value_date) / gDaysInYear

        vBumped = self.value(nextDate, stock_price,
                             discount_curve,
                             dividend_curve, model)

        discount_curve._valuationDate = value_date
        theta = (vBumped - v) / bump
        return theta

###############################################################################

    def rho(self,
            value_date: TuringDate,
            stock_price: float,
            discount_curve: TuringDiscountCurve,
            dividend_curve: TuringDiscountCurve,
            model):
        ''' Calculation of option rho by perturbing interest rate and
        revaluation. '''

        v = self.value(value_date, stock_price, discount_curve,
                       dividend_curve, model)

        vBumped = self.value(value_date, stock_price, discount_curve.bump(bump),
                             dividend_curve, model)

        rho = (vBumped - v) / bump
        return rho
