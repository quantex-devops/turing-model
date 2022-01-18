from dataclasses import dataclass
from typing import List, Union

import numpy as np

from turing_models.utilities.schedule import TuringSchedule
from turing_models.utilities.frequency import FrequencyType
from turing_models.utilities.calendar import TuringCalendarTypes, TuringBusDayAdjustTypes
from turing_models.utilities.global_variables import gNumObsInYear, gDaysInYear
from turing_models.utilities.global_types import TuringOptionTypes, \
    TuringKnockInTypes, OptionType
from turing_models.models.process_simulator import TuringProcessSimulator, TuringProcessTypes, \
    TuringGBMNumericalScheme
from turing_models.instruments.eq.equity_option import EqOption
from turing_models.utilities.helper_functions import to_string
from turing_models.utilities.error import TuringError
from turing_models.utilities.turing_date import TuringDate


@dataclass(repr=False, eq=False, order=False, unsafe_hash=True)
class SnowballOption(EqOption):

    barrier: float = None
    rebate: float = None
    coupon: float = None
    untriggered_rebate: float = None
    knock_in_price: float = None
    knock_in_type: Union[str, TuringKnockInTypes] = None
    knock_in_strike1: float = None
    knock_in_strike2: float = None
    business_day_adjust_type: Union[str,
                                    TuringBusDayAdjustTypes] = TuringBusDayAdjustTypes.FOLLOWING
    knock_out_obs_days_whole: List[TuringDate] = None

    def __post_init__(self):
        super().__post_init__()
        self.num_ann_obs = gNumObsInYear
        self.days_in_year = gDaysInYear
        self.num_paths = 1_000_000
        self.seed = 4242
        self.check_param()

    def check_param(self):
        if self.option_type is not None:
            rules = {
                "CALL": TuringOptionTypes.SNOWBALL_CALL,
                OptionType.CALL: TuringOptionTypes.SNOWBALL_CALL,
                "PUT": TuringOptionTypes.SNOWBALL_PUT,
                OptionType.PUT: TuringOptionTypes.SNOWBALL_PUT
            }
            self.option_type = rules.get(self.option_type,
                                         TuringError('Please check the input of option_type'))
            if isinstance(self.option_type, TuringError):
                raise self.option_type

        if self.knock_in_type is not None:
            if not isinstance(self.knock_in_type, TuringKnockInTypes):
                rules = {
                    "RETURN": TuringKnockInTypes.RETURN,
                    "VANILLA": TuringKnockInTypes.VANILLA,
                    "SPREADS": TuringKnockInTypes.SPREADS
                }
                self.knock_in_type = rules.get(self.knock_in_type,
                                               TuringError('Please check the input of knock_in_type'))
                if isinstance(self.knock_in_type, TuringError):
                    raise self.knock_in_type

        if self.business_day_adjust_type is None:
            self.business_day_adjust_type = TuringBusDayAdjustTypes.NONE
        else:
            if not isinstance(self.business_day_adjust_type, TuringBusDayAdjustTypes):
                rules = {
                    "FOLLOWING": TuringBusDayAdjustTypes.FOLLOWING,
                    "MODIFIED_FOLLOWING": TuringBusDayAdjustTypes.MODIFIED_FOLLOWING,
                    "PRECDING": TuringBusDayAdjustTypes.PRECDING,
                    "MODIFIED_PRECEDING": TuringBusDayAdjustTypes.MODIFIED_PRECEDING
                }
                self.business_day_adjust_type = rules.get(self.business_day_adjust_type,
                                                          TuringError('Please check the input of business_day_adjust_type'))
                if isinstance(self.business_day_adjust_type, TuringError):
                    raise self.business_day_adjust_type

    @property
    def bus_days(self) -> List[TuringDate]:
        """生成从估值日到到期日的交易日时间表（包含首尾日）"""
        schedule_daily = TuringSchedule(self._value_date,
                                        self.expiry,
                                        freqType=FrequencyType.DAILY,
                                        calendarType=TuringCalendarTypes.CHINA_SSE,
                                        busDayAdjustType=self.business_day_adjust_type)
        return schedule_daily._adjustedDates

    @property
    def _knock_out_obs_days_whole(self) -> List[TuringDate]:
        """如果用户未传入敲出观察日时间表，就按月生成（包含首尾日）；
           如果用户传入敲出观察日时间表，就使用该值"""
        if self.knock_out_obs_days_whole:
            return self.knock_out_obs_days_whole
        else:
            schedule_monthly = TuringSchedule(self.start_date,
                                              self.expiry,
                                              freqType=FrequencyType.MONTHLY,
                                              calendarType=TuringCalendarTypes.CHINA_SSE,
                                              busDayAdjustType=self.business_day_adjust_type)
            return schedule_monthly._adjustedDates

    def price(self) -> float:
        s0 = self._stock_price
        r = self.r
        q = self.q
        vol = self._volatility
        texp = self.texp
        num_ann_obs = self.num_ann_obs
        num_paths = self.num_paths
        seed = self.seed

        process = TuringProcessSimulator()
        process_type = TuringProcessTypes.GBM
        scheme = TuringGBMNumericalScheme.ANTITHETIC
        model_params = (s0, r - q, vol, scheme)
        # 减一是为了适配getGBMPaths函数
        num_time_steps = len(self.bus_days) - 1

        sall = process.getProcess(process_type, texp, model_params,
                                  num_ann_obs, num_paths, seed, num_time_steps)
        (num_paths, _) = sall.shape
        return self._payoff(sall, num_paths)

    def _payoff(self, sall, num_paths):
        k1 = self.barrier
        k2 = self.knock_in_price
        sk1 = self.knock_in_strike1
        sk2 = self.knock_in_strike2
        start_date = self.start_date
        initial_spot = self.initial_spot
        expiry = self.expiry
        value_date = self._value_date
        r = self.r
        rebate = self.rebate
        untriggered_rebate = self.untriggered_rebate
        notional = self.notional
        texp = self.texp
        option_type = self.option_type
        knock_in_type = self.knock_in_type
        flag = self.annualized_flag
        participation_rate = self.participation_rate
        days_in_year = self.days_in_year
        bus_days = self.bus_days

        # 统计从估值日到到期日之间的敲出观察日
        knock_out_obs_days = sorted(
            list(set(self._knock_out_obs_days_whole).intersection(set(bus_days))))

        # 统计敲出观察日在交易日列表中的索引值
        knock_out_obs_days_index = []
        for day in knock_out_obs_days:
            i = bus_days.index(day)
            knock_out_obs_days_index.append(i)

        out_call_sign = [False] * num_paths
        out_call_index = [False] * num_paths
        out_call_index2 = [False] * num_paths
        in_call_sign = [False] * num_paths
        out_put_sign = [False] * num_paths
        out_put_index = [False] * num_paths
        out_put_index2 = [False] * num_paths
        in_put_sign = [False] * num_paths

        if option_type == TuringOptionTypes.SNOWBALL_CALL:
            for p in range(0, num_paths):
                # 判断每条路径是否存在敲出
                out_call_sign[p] = any(
                    [sall[p][i] >= k1 for i in knock_out_obs_days_index])

                # 如果敲出，就填充对应的索引值，用于计算相关天数
                if out_call_sign[p]:
                    for i in knock_out_obs_days_index:
                        if sall[p][i] >= k1:
                            # 用来计算实际期限
                            out_call_index[p] = bus_days[i] - start_date
                            # 用来做折现
                            out_call_index2[p] = bus_days[i] - value_date
                            break

                # 每天判断是否敲入
                in_call_sign[p] = np.any(sall[p] < k2)

        elif option_type == TuringOptionTypes.SNOWBALL_PUT:
            for p in range(0, num_paths):
                # 判断每条路径是否存在敲出
                out_put_sign[p] = any(
                    [sall[p][i] <= k1 for i in knock_out_obs_days_index])

                # 如果敲出，就填充对应的索引值，用于计算相关天数
                if out_put_sign[p]:
                    for i in knock_out_obs_days_index:
                        if sall[p][i] <= k1:
                            # 用来计算实际期限
                            out_put_index[p] = bus_days[i] - start_date
                            # 用来做折现
                            out_put_index2[p] = bus_days[i] - value_date
                            break

                # 每天判断是否敲入
                in_put_sign[p] = np.any(sall[p] > k2)

        ones = np.ones(num_paths)
        # list转成ndarray
        out_call_sign = np.array(out_call_sign)
        not_out_call_sign = ones - out_call_sign
        out_call_index = np.array(out_call_index)
        out_call_index2 = np.array(out_call_index2)
        in_call_sign = np.array(in_call_sign)
        not_in_call_sign = ones - in_call_sign
        out_put_sign = np.array(out_put_sign)
        not_out_put_sign = ones - out_put_sign
        out_put_index = np.array(out_put_index)
        out_put_index2 = np.array(out_put_index2)
        in_put_sign = np.array(in_put_sign)
        not_in_put_sign = ones - in_put_sign

        whole_term = (expiry - start_date) / days_in_year

        if option_type == TuringOptionTypes.SNOWBALL_CALL:

            payoff = out_call_sign * ((notional * rebate * (out_call_index / days_in_year)**flag) *
                                      np.exp(-r * out_call_index2 / days_in_year)) + not_out_call_sign * not_in_call_sign * \
                ((notional * untriggered_rebate * whole_term**flag) * np.exp(-r * texp))

            if knock_in_type == TuringKnockInTypes.RETURN:
                payoff += not_out_call_sign * in_call_sign * \
                    (-notional * (1 - sall[:, -1] / initial_spot) *
                     participation_rate * np.exp(-r * texp))

            elif knock_in_type == TuringKnockInTypes.VANILLA:
                payoff += not_out_call_sign * in_call_sign * \
                    (-notional * np.maximum(sk1 - sall[:, -1] / initial_spot, 0) *
                     participation_rate * whole_term**flag * np.exp(-r * texp))

            elif knock_in_type == TuringKnockInTypes.SPREADS:
                payoff += not_out_call_sign * in_call_sign * \
                    (-notional * np.maximum(sk1 - np.maximum(sall[:, -1] / initial_spot, sk2), 0) *
                     participation_rate * whole_term**flag * np.exp(-r * texp))

        elif option_type == TuringOptionTypes.SNOWBALL_PUT:

            payoff = out_put_sign * ((notional * rebate * (out_put_index / days_in_year)**flag) *
                                     np.exp(-r * out_put_index2 / days_in_year)) + not_out_put_sign * not_in_put_sign * \
                ((notional * untriggered_rebate * whole_term**flag) * np.exp(-r * texp))

            if knock_in_type == TuringKnockInTypes.RETURN:
                payoff += not_out_put_sign * in_put_sign * \
                    (-notional * (sall[:, -1] / initial_spot - 1) *
                     participation_rate * np.exp(-r * texp))

            elif knock_in_type == TuringKnockInTypes.VANILLA:
                payoff += not_out_put_sign * in_put_sign * \
                    (-notional * np.maximum(sall[:, -1] / initial_spot - sk1, 0) *
                     participation_rate * whole_term**flag * np.exp(-r * texp))

            elif knock_in_type == TuringKnockInTypes.SPREADS:
                payoff += not_out_put_sign * in_put_sign * \
                    (-notional * np.maximum(np.minimum(sall[:, -1] / initial_spot, sk2) - sk1, 0) *
                     participation_rate * whole_term**flag * np.exp(-r * texp))

        return payoff.mean()

    def __repr__(self):
        s = super().__repr__()
        s += to_string("Barrier", self.barrier)
        s += to_string("Rebate", self.rebate)
        s += to_string("Coupon", self.coupon)
        s += to_string("Knock In Price", self.knock_in_price)
        s += to_string("Knock In Type", self.knock_in_type)
        s += to_string("Knock In Strike1", self.knock_in_strike1)
        s += to_string("Knock In Strike2", self.knock_in_strike2)
        return s
