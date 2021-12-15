# from datetime import datetime
#
# import matplotlib.pyplot as plt
# from matplotlib.ticker import MultipleLocator
#
# from turing_models.market.constants import dates, rates
# from turing_models.market.curves.curve_generation import CurveGeneration
#
#
# curve_gen = CurveGeneration(dates, rates)
# curve_data = curve_gen.get_data_dict()
# terms, spot_rates = list(curve_data.keys()), list(curve_data.values())
# terms = [datetime.strftime(d, '%Y-%m-%d') for d in terms]
#
# plt.figure(figsize=(20, 6))
# ax = plt.gca()
# plt.xlabel('term')
# plt.ylabel('spot rate')
# plt.title('curve')
# plt.plot(terms, spot_rates)
# plt.xticks(rotation=30)
# ax.xaxis.set_major_locator(MultipleLocator(40))  # 设置40倍数
# plt.show()

from turing_models.instruments.common import YieldCurveCode, RiskMeasure
from turing_models.instruments.rates.bond_fixed_rate import BondFixedRate
from turing_models.market.data.china_money_yield_curve import dates, rates
from turing_models.market.curves.curve_generation import CurveGeneration
from turing_models.market.curves.curve_adjust import CurveAdjustmentImpl
from fundamental.pricing_context import PricingContext
import pandas as pd


# curve_data：曲线数据
# parallel_shift：曲线整体平移，单位bp，正值表示向上平移，负值相反
# curve_shift：曲线旋转，单位bp，表示曲线左端和右端分别绕pivot_point旋转的绝对值之和，正值表示右侧向上旋转，负值相反
# pivot_point：旋转中心，单位是年，若不传该参数，表示旋转中心是曲线的第一个时间点
# tenor_start：旋转起始点，单位是年，若不传该参数，表示从曲线的第一个时间点开始旋转
# tenor_end：旋转结束点，单位是年，若不传该参数，表示从曲线的最后一个时间点结束旋转
# pivot_point、tenor_start和tenor_end的范围为[原曲线的第一个时间点，原曲线的最后一个时间点]
from turing_models.utilities.day_count import TuringDayCountTypes
from turing_models.utilities.frequency import TuringFrequencyTypes
from turing_models.utilities.turing_date import TuringDate

curve_data = pd.DataFrame(data={'tenor': dates, 'rate': rates})
# ca = CurveAdjustmentImpl(curve_data=curve_data,
#                          parallel_shift=1000,
#                          curve_shift=1000,
#                          pivot_point=1,
#                          tenor_start=0.5,
#                          tenor_end=1.5)
# curve_data_adjusted = ca.get_curve_data()
# terms_adjusted, rates_adjusted = list(curve_data_adjusted['tenor']), list(curve_data_adjusted['rate'])
# curve_gen = CurveGeneration(terms_adjusted, rates_adjusted)
# curve_data = curve_gen.get_data_dict()
# terms, spot_rates = list(curve_data.keys()), list(curve_data.values())
# curve = pd.Series(data=spot_rates, index=terms)
# print(curve)

curve_chinabond = YieldCurveCode.CBD100222
bond_fr = BondFixedRate(bond_symbol="143756.SH",
                        coupon=0.04,
                        # curve_code=curve_chinabond,
                        issue_date=TuringDate(2015, 11, 13),
                        # due_date=TuringDate(2025, 11, 14),
                        bond_term_year=10,
                        freq_type=TuringFrequencyTypes.SEMI_ANNUAL,
                        accrual_type=TuringDayCountTypes.ACT_365L,
                        par=100)

scenario_extreme = PricingContext(
    bond_yield_curve=[
        {"bond_symbol": "143756.SH", "value": curve_data},
    ],

)

# price_1 = bond_fr.calc(RiskMeasure.FullPrice)
# clean_price_1 = bond_fr.calc(RiskMeasure.CleanPrice)
# ytm_1 = bond_fr.calc(RiskMeasure.YTM)
# dv01_1 = bond_fr.calc(RiskMeasure.Dv01)
# modified_duration_1 = bond_fr.calc(RiskMeasure.ModifiedDuration)
# dollar_convexity_1 = bond_fr.calc(RiskMeasure.DollarConvexity)
#
# print('price', price_1)
# print('clean_price', clean_price_1)
# print('ytm', ytm_1)
# print('dv01:', dv01_1)
# print('modified_duration:', modified_duration_1)
# print('dollar_convexity:', dollar_convexity_1)
# print("---------------------------------------------")

with scenario_extreme:
    price_2 = bond_fr.calc(RiskMeasure.FullPrice)
    clean_price_2 = bond_fr.calc(RiskMeasure.CleanPrice)
    ytm_2 = bond_fr.calc(RiskMeasure.YTM)
    dv01_2 = bond_fr.calc(RiskMeasure.Dv01)
    modified_duration_2 = bond_fr.calc(RiskMeasure.ModifiedDuration)
    dollar_convexity_2 = bond_fr.calc(RiskMeasure.DollarConvexity)
    print(bond_fr.cv.curve_data)

    print('price', price_2)
    print('clean_price', clean_price_2)
    print('ytm', ytm_2)
    print('dv01:', dv01_2)
    print('modified_duration:', modified_duration_2)
    print('dollar_convexity:', dollar_convexity_2)
    print("---------------------------------------------")