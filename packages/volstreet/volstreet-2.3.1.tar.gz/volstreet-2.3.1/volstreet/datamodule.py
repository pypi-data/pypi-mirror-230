import volstreet as vs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import url_changes
from kiteconnect import KiteConnect
from time import sleep
from functools import partial
import pyotp
from volstreet.exceptions import ApiKeyNotFound
from eod import EodHistoricalData
import pandas as pd
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR
import numpy as np
from datetime import datetime, timedelta, time
from collections import defaultdict
import json


class DataClient:
    def __init__(self, api_key=None):
        if api_key is None:
            try:  # Try to get the api key from the environment variable
                api_key = __import__("os").getenv("EOD_API_KEY")
            except KeyError:
                raise ApiKeyNotFound(
                    "EOD API Key not found. Please set the API key in environment variables or pass it as an argument."
                )
        self.api_key = api_key
        self.client = EodHistoricalData(api_key=api_key)

    @staticmethod
    def parse_symbol(symbol):
        symbol_dict = {
            "NIFTY": "NSEI.INDX",
            "NIFTY 50": "NSEI.INDX",
            "NIFTY50": "NSEI.INDX",
            "BANKNIFTY": "NSEBANK.INDX",
            "NIFTY BANK": "NSEBANK.INDX",
            "NIFTYBANK": "NSEBANK.INDX",
            "FINNIFTY": "CNXFIN.INDX",
            "NIFTY FIN SERVICE": "CNXFIN.INDX",
            "VIX": "NIFVIX.INDX",
            "USVIX": "VIX.INDX",
            "US VIX": "VIX.INDX",
        }
        symbol = symbol.upper()
        if "." not in symbol:
            if symbol in symbol_dict:
                symbol = symbol_dict[symbol]
            else:
                symbol = symbol + ".NSE"
        return symbol

    def get_data(self, symbol, from_date="2011-01-01", return_columns=None):
        name = symbol.split(".")[0] if "." in symbol else symbol

        symbol = self.parse_symbol(symbol)

        if return_columns is None:
            return_columns = ["open", "close", "gap", "intra", "abs_gap", "abs_intra"]

        resp = self.client.get_prices_eod(
            symbol, period="d", order="a", from_=from_date
        )
        df = pd.DataFrame(resp)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index(df.date, inplace=True)
        df["p_close"] = df.close.shift(1)
        df["gap"] = (df.open / df.p_close - 1) * 100
        df["intra"] = (df.close / df.open - 1) * 100
        df["abs_gap"] = abs(df.gap)
        df["abs_intra"] = abs(df.intra)
        df = df.loc[:, return_columns]
        df.name = name
        return df

    def get_intraday_data(
        self,
        symbol,
        interval,
        from_date="2011-01-01",
        to_date=None,
        return_columns=None,
        time_zone="Asia/Kolkata",
    ):
        name = symbol.split(".")[0] if "." in symbol else symbol

        symbol = self.parse_symbol(symbol)

        if return_columns is None:
            return_columns = ["open", "high", "low", "close"]

        to_date = pd.to_datetime(to_date) if to_date is not None else datetime.now()
        from_date = pd.to_datetime(from_date)

        resp_list = []
        while to_date.date() > from_date.date():
            _to_date_temp = (
                from_date + timedelta(days=120)
                if to_date - from_date > timedelta(days=120)
                else to_date
            )
            resp = self.client.get_prices_intraday(
                symbol,
                interval=interval,
                from_=str(int(from_date.timestamp())),
                to=str(int(_to_date_temp.timestamp())),
            )

            resp_list.extend(resp)
            # If the last date in the resp is greater than the temp to_date, then we will advance the from_date
            # to the last date in the resp. Else, we will advance the from_date by 120 days.
            if (
                datetime.fromisoformat(resp[-1]["datetime"]).date()
                > _to_date_temp.date()
            ):
                from_date = datetime.fromisoformat(resp[-1]["datetime"])
                print(
                    f"Given more data than requested. Advancing from_date to {from_date}"
                )
            else:
                from_date = _to_date_temp

        df = pd.DataFrame(resp_list)
        df = df.drop_duplicates()
        df.index = (
            pd.to_datetime(df.datetime).dt.tz_localize("UTC").dt.tz_convert(time_zone)
        )
        df.index = df.index.tz_localize(None)
        df = df[return_columns]
        df.name = name
        return df


class BackTester:
    def __init__(self, data_client=None):
        if data_client is None:
            data_client = DataClient()
        self.data_client = data_client
        self.historical_expiry_dates = None
        self.set_historical_expiry_dates()

    def set_historical_expiry_dates(self):
        all_expiry_dates = {}

        # Setting market days
        nifty = self.data_client.get_data("NIFTY", return_columns=["close"])
        bad_dates = [datetime(2021, 11, 4)]
        nifty.drop(index=bad_dates, inplace=True)
        market_days = nifty.index
        market_days_forward_looking = nifty.index.union(
            pd.date_range(
                start=market_days[-1], end=market_days[-1] + timedelta(days=7)
            )
        )

        for i, weekday in enumerate([MO, TU, WE, TH, FR]):
            proxy_expiry_dates = pd.to_datetime(
                market_days.date + relativedelta(weekday=weekday(1))
            ).unique()
            expiry_dates = proxy_expiry_dates.where(
                proxy_expiry_dates.isin(market_days_forward_looking),
                proxy_expiry_dates - timedelta(days=1),
            )
            expiry_dates = expiry_dates.where(
                expiry_dates.isin(market_days_forward_looking),
                expiry_dates - timedelta(days=1),
            )
            all_expiry_dates[i] = expiry_dates + timedelta(hours=15, minutes=30)

        self.historical_expiry_dates = all_expiry_dates

    def fetch_nearest_expiry_from_date(
        self, date_time, expiry_on=3, threshold_days=0, n_exp=1
    ):
        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        filtered_dates = self.historical_expiry_dates[expiry_on]
        delta_days = (filtered_dates - date_time.replace(hour=00, minute=00)).days
        valid_indices = np.where(
            delta_days < threshold_days, np.inf, delta_days
        ).argsort()[:n_exp]

        nearest_exp_dates = filtered_dates[valid_indices].sort_values()

        if n_exp == 1:
            return nearest_exp_dates[0] if len(nearest_exp_dates) != 0 else None
        else:
            return nearest_exp_dates

    def historic_time_to_expiry(
        self,
        date_time: str | datetime,
        expiry_weekday: int = 3,
        in_days: bool = False,
        threshold_days: int = 0,
        n_exp: int = 1,
    ):
        """Return time left to expiry"""
        if in_days:
            multiplier = 365
            rounding = 0
        else:
            multiplier = 1
            rounding = 5

        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        expiry = self.fetch_nearest_expiry_from_date(
            date_time.replace(hour=00, minute=00), expiry_weekday, threshold_days, n_exp
        )

        if expiry is None:
            return None
        elif isinstance(expiry, pd.DatetimeIndex):
            time_left = (expiry - date_time) / timedelta(days=365)
        else:
            time_left = (expiry - date_time) / timedelta(days=365)

        # Multiplying by the multiplier and rounding
        time_left = np.round(time_left * multiplier, rounding)
        return time_left

    def clean_stockmock_excel(self, filename):
        df = read_excel_file(filename)

        ceindex = ["CE" in entry for entry in df.columns].index(1)
        peindex = ["PE" in entry for entry in df.columns].index(1)

        df = df.set_axis(df.iloc[0], axis=1, copy=False)
        df.drop(df.index[0], inplace=True)

        strike = df.Strike.iloc[:, 0]
        df = df.filter(regex="Date|Exit|Entry")
        df.drop(columns=df.filter(regex="Fut").columns, inplace=True)
        df["Strike"] = strike

        if "Exit Time" not in df.columns:
            indices_to_insert = np.where(df.columns == "Exit Price")[0]
            for idx in indices_to_insert:
                df.insert(idx + 1, "Exit Time", "15:29")

        renamecols = [
            "Date",
            "Expiry",
            "VixEntry",
            "VixExit",
            "EntrySpot",
            "ExitSpot",
            "CallEntryPrice" if ceindex < peindex else "PutEntryPrice",
            "CallExitPrice" if ceindex < peindex else "PutExitPrice",
            "CallExitTime" if ceindex < peindex else "PutExitTime",
            "PutEntryPrice" if ceindex < peindex else "CallEntryPrice",
            "PutExitPrice" if ceindex < peindex else "CallExitPrice",
            "PutExitTime" if ceindex < peindex else "CallExitTime",
            "Strike",
        ]

        if ceindex == peindex:
            raise Exception("Cannot determine whether call column is before put column")

        df.columns = renamecols
        df["Strike"] = df.Strike.apply(lambda x: int(x.rstrip("PE|CE")))

        # Process data
        df["TotalEntryPrice"] = df.CallEntryPrice + df.PutEntryPrice
        df["TotalExitPrice"] = df.CallExitPrice + df.PutExitPrice
        df["Profit"] = df.TotalEntryPrice - df.TotalExitPrice

        # Handle dates
        df["Date"] = [
            *map(lambda x: x.date(), pd.to_datetime(df.Date, format="%Y-%m-%d"))
        ]
        df.set_index("Date", inplace=True)
        df.index = pd.to_datetime(df.index)
        expiry_on = 1 if "finnifty" in filename.lower() else 3
        df["Expiry"] = df.index.to_series().apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                x, expiry_on=expiry_on
            ).replace(hour=15, minute=30)
        )
        df["TimeToExpiry"] = df.Expiry - df.index.map(
            lambda x: x.replace(hour=9, minute=15)
        )

        cols = [
            "Expiry",
            "TimeToExpiry",
            "VixEntry",
            "VixExit",
            "EntrySpot",
            "ExitSpot",
            "Strike",
            "CallEntryPrice",
            "PutEntryPrice",
            "TotalEntryPrice",
            "CallExitPrice",
            "PutExitPrice",
            "TotalExitPrice",
            "CallExitTime",
            "PutExitTime",
            "Profit",
        ]

        return df[cols]

    @staticmethod
    def process_stockmock_df(df, spotoneminutedf, maxtrendsl=0.3, maxtrendprofit=0.7):
        df = df.copy()
        spotoneminutedf = spotoneminutedf.copy()

        spotoneminutedf = (
            spotoneminutedf.resample("1min")
            .last()
            .interpolate(method="time")
            .between_time("09:15", "15:30")
        )
        oneminutedf_grouped = pd.DataFrame(
            spotoneminutedf.groupby(spotoneminutedf.index.date), columns=["date", "df"]
        )
        oneminutedf_grouped = oneminutedf_grouped.set_index(
            pd.to_datetime(oneminutedf_grouped.date)
        ).drop("date", axis=1)

        def locate(df, datetime):
            try:
                price = df.loc[datetime].close
            except KeyError:
                if df.loc[datetime.date()].empyty():
                    print(f"No price df for day: {datetime.date()}. Returning None.")
                    return None
                else:
                    newdatetime = df[df.index > datetime].iloc[0].name
                    price = df[df.index > datetime].iloc[0].close
                    print(
                        f"No price found for {datetime}. Substituting with {newdatetime}.\n"
                    )
            return price

        def fetchexitprice(row):
            if row.SL_type == "NA":
                slprice = row.ExitSpot
            elif row.SL_type == "Call":
                slprice = locate(
                    spotoneminutedf, datetime.combine(row.name, row.CallExitTime)
                )
            elif row.SL_type == "Put":
                slprice = locate(
                    spotoneminutedf, datetime.combine(row.name, row.PutExitTime)
                )
            elif row.SL_type.startswith("Both"):
                if row.CallExitTime < row.PutExitTime:
                    slprice = locate(
                        spotoneminutedf, datetime.combine(row.name, row.CallExitTime)
                    )
                else:
                    slprice = locate(
                        spotoneminutedf, datetime.combine(row.name, row.PutExitTime)
                    )

            closeprice = locate(
                spotoneminutedf, datetime.combine(row.name, time(15, 28))
            )

            return slprice, closeprice

        def sltype(callexittime, putexittime):
            if all([callexittime == "No SL", putexittime == "No SL"]):
                return "NA"
            elif callexittime != "No SL" and putexittime != "No SL":
                if callexittime < putexittime:
                    return "Both. First:Call"
                else:
                    return "Both. First:Put"
            elif callexittime != "No SL" and putexittime == "No SL":
                return "Call"
            else:
                return "Put"

        def trend_checker(
            row,
            stoploss_max_trend=maxtrendsl,
            take_profit_max_trend=maxtrendprofit,
            _print=False,
        ):
            if row.SL_type == "NA":
                return None, None, None, None, None, None

            pricedf = oneminutedf_grouped.loc[row.name].df

            if row.SL_type.startswith("Both"):
                sltype = row.SL_type.split(":")[1]
            else:
                sltype = row.SL_type

            timeofexit = datetime.combine(row.name, row[f"{sltype}ExitTime"])
            niftyatexit = row.SpotAtFirstSL
            extreme_price_label = "max" if sltype == "Call" else "min"
            trend_modifier = 1 if sltype == "Call" else -1

            # Extreme price and its time
            price_extreme = (
                pricedf.loc[timeofexit:].close.max()
                if sltype == "Call"
                else pricedf.loc[timeofexit:].close.min()
            )
            time_of_extreme_price = (
                pricedf.loc[timeofexit:].close.idxmax()
                if sltype == "Call"
                else pricedf.loc[timeofexit:].close.idxmin()
            )

            # SL and profit price and time
            def get_price_time(
                pricedf, timeofexit, niftyatexit, price_multiplier, condition
            ):
                target_price = niftyatexit * price_multiplier
                price_condition = condition(
                    pricedf.loc[timeofexit:].close, target_price
                )
                target_array = pricedf.loc[timeofexit:].close[price_condition]
                return (
                    (target_price, target_array.iloc[0], target_array.index[0])
                    if not target_array.empty
                    else (target_price, False, False)
                )

            # Stoploss price and time
            stoploss_multiplier = (
                1 + (-1 if sltype == "Call" else 1) * stoploss_max_trend / 100
            )
            stoploss_condition = lambda x, y: x < y if sltype == "Call" else x > y
            (
                stoploss_price,
                stoploss_price_matched,
                time_of_maxtrend_sl,
            ) = get_price_time(
                pricedf,
                timeofexit,
                niftyatexit,
                stoploss_multiplier,
                stoploss_condition,
            )

            # Profit target price and time
            profit_target_multiplier = 1 + trend_modifier * take_profit_max_trend / 100
            profit_target_condition = lambda x, y: x > y if sltype == "Call" else x < y
            (
                profit_target_price,
                profit_target_price_matched,
                time_of_maxtrend_pt,
            ) = get_price_time(
                pricedf,
                timeofexit,
                niftyatexit,
                profit_target_multiplier,
                profit_target_condition,
            )

            if stoploss_price_matched and profit_target_price_matched:
                if time_of_maxtrend_sl < time_of_maxtrend_pt:
                    max_trend_sl_hit = True
                else:
                    max_trend_sl_hit = False
            elif stoploss_price_matched:
                max_trend_sl_hit = True
            else:
                max_trend_sl_hit = False

            extreme_change_after_sl = (
                ((price_extreme / niftyatexit) - 1) * 100 * trend_modifier
            )
            nifty_close_price = row.ExitSpot
            end_change_after_sl = (
                ((nifty_close_price / niftyatexit) - 1) * 100 * trend_modifier
            )

            if max_trend_sl_hit:
                trend_captured = (
                    (stoploss_price / niftyatexit - 1) * 100 * trend_modifier
                )
            else:
                if profit_target_price_matched:
                    trend_captured = (
                        (profit_target_price / niftyatexit - 1) * 100 * trend_modifier
                    )
                else:
                    trend_captured = (
                        (nifty_close_price / niftyatexit - 1) * 100 * trend_modifier
                    )
            if _print is True:
                print(
                    f"Day: {row.name}, SL: {sltype}, Nifty at exit: {niftyatexit}, Stoploss price: {stoploss_price}, "
                    f"Stoploss price matched: {stoploss_price_matched}, Time of max trend SL: {time_of_maxtrend_sl}, "
                    f"Nifty {extreme_price_label} price: {price_extreme}, Time of {extreme_price_label} price: {time_of_extreme_price}, "
                    f"Nifty close price: {nifty_close_price}, {extreme_price_label.capitalize()} change after SL: {extreme_change_after_sl}, "
                    f"End change after SL: {end_change_after_sl}"
                )

            return (
                end_change_after_sl,
                extreme_change_after_sl,
                max_trend_sl_hit,
                stoploss_price,
                time_of_maxtrend_sl,
                trend_captured,
            )

        # Actual Analysis After Function Definitions

        df.loc[((df.CallExitTime.isna()) & (df.PutExitTime.isna())), "SL_hit"] = False
        df.loc[~((df.CallExitTime.isna()) & (df.PutExitTime.isna())), "SL_hit"] = True
        # df['SL_contribution'] = df.Profit_SL - df.Profit_NOSL
        df["CallExitTime"] = df.CallExitTime.fillna("No SL").apply(
            lambda x: "No SL" if x == "No SL" else datetime.strptime(x, "%H:%M").time()
        )
        df["PutExitTime"] = df.PutExitTime.fillna("No SL").apply(
            lambda x: "No SL" if x == "No SL" else datetime.strptime(x, "%H:%M").time()
        )
        df["SL_type"] = df.apply(
            lambda row: sltype(row.CallExitTime, row.PutExitTime), axis=1
        )
        df["FirstSL"] = df.SL_type.where(
            df.SL_type.str.fullmatch("Call|Put"), df.SL_type.str.lstrip("Both. First:")
        )
        df[["SpotAtFirstSL", "SpotClosePrice"]] = df.apply(
            lambda row: fetchexitprice(row), axis=1
        ).to_list()
        df["ChangeFirstSL"] = ((df.SpotAtFirstSL / df.EntrySpot) - 1) * 100
        df["AbsChangeFirstSL"] = abs(df.ChangeFirstSL)
        df[
            [
                "TrendAtClose",
                "MaxTrend",
                "MaxTrendSL",
                "MaxTrendSLPrice",
                "MaxTrendSLTime",
                "TrendCaptured",
            ]
        ] = df.apply(lambda row: trend_checker(row), axis=1).to_list()
        df["ProfitPct"] = (df.Profit / df.EntrySpot) * 100
        df["NAV"] = ((df.ProfitPct + 100) / 100).dropna().cumprod()
        df["Max_NAV"] = df.NAV.cummax()
        df["Drawdown"] = ((df.NAV / df.Max_NAV) - 1) * 100
        df["EntryIV"] = df.apply(
            lambda row: vs.straddle_iv(
                row.CallEntryPrice,
                row.PutEntryPrice,
                row.EntrySpot,
                timeleft=row.TimeToExpiry / timedelta(days=365),
                strike=row.Strike,
            )[2],
            axis=1,
        )
        df["CallExitTime"] = df.apply(
            lambda row: datetime.combine(row.name, row.CallExitTime)
            if row.CallExitTime != "No SL"
            else "No SL",
            axis=1,
        )
        df["PutExitTime"] = df.apply(
            lambda row: datetime.combine(row.name, row.PutExitTime)
            if row.PutExitTime != "No SL"
            else "No SL",
            axis=1,
        )
        df["FirstSLTime"] = np.where(
            df.FirstSL == "Call",
            df.CallExitTime,
            np.where(
                df.FirstSL == "Put",
                df.PutExitTime,
                df.index.map(lambda x: datetime.combine(x, time(15, 28))),
            ),
        )

        def convert_to_datetime(value):
            if isinstance(value, int):
                # Assuming the integer represents a Unix timestamp in nanoseconds
                return datetime.utcfromtimestamp(
                    value / 1e9
                )  # Divide by 1e9 to convert to seconds
            return value

        df["FirstSLTime"] = df.FirstSLTime.apply(convert_to_datetime)

        cols = [
            "EntrySpot",
            "EntryIV",
            "Strike",
            "Expiry",
            "TimeToExpiry",
            "CallEntryPrice",
            "PutEntryPrice",
            "CallExitPrice",
            "PutExitPrice",
            "CallExitTime",
            "PutExitTime",
            "SL_hit",
            "FirstSLTime",
            "SL_type",
            "FirstSL",
            "SpotAtFirstSL",
            "ChangeFirstSL",
            "AbsChangeFirstSL",
            "ExitSpot",
            "SpotClosePrice",
            "TrendAtClose",
            "MaxTrend",
            "MaxTrendSL",
            "MaxTrendSLPrice",
            "MaxTrendSLTime",
            "TrendCaptured",
            "Profit",
            "ProfitPct",
            "NAV",
            "Max_NAV",
            "Drawdown",
        ]

        return df[cols]

    def backtest_option_buying_strategy_on_expiry(
        self,
        one_min_df,
        iv_df,
        threshold_price,
        target_price=None,
        symbol="NIFTY",
        cutoff_time=(15, 00),
    ):
        # Payoff function
        def buy_straddle_if_price_touched(
            group, price=threshold_price, target=target_price, cut_off_time=cutoff_time
        ):
            # Checking if price is touched before cut off time
            group = group[
                (group.index.time <= time(*cut_off_time))
                & (group.index.time >= time(9, 30))
            ]
            first_time_price_touched = (
                group[group.tracked_straddle_premium <= price].index[0]
                if not group[group.tracked_straddle_premium <= price].empty
                else None
            )
            if first_time_price_touched is None:
                return group
            else:
                touched_price = group.loc[
                    first_time_price_touched
                ].tracked_straddle_premium
                # Appending data from the first time the price is touched
                group.loc[:, "touched_price"] = touched_price
                group.loc[:, "touched_time"] = first_time_price_touched
                if target is not None:
                    forward_looking_prices = group.loc[
                        first_time_price_touched:, "tracked_straddle_premium"
                    ]
                    if not forward_looking_prices.empty:
                        target_hit_time = (
                            forward_looking_prices[
                                forward_looking_prices >= target
                            ].index[0]
                            if not forward_looking_prices[
                                forward_looking_prices >= target
                            ].empty
                            else None
                        )
                        if target_hit_time is not None:
                            group.loc[:, "target_hit"] = forward_looking_prices.loc[
                                target_hit_time
                            ]
                            group.loc[:, "target_hit_time"] = target_hit_time
                        else:
                            group.loc[:, "target_hit"] = False
                            group.loc[:, "target_hit_time"] = None
                    else:
                        group.loc[:, "target_hit"] = False
                        group.loc[:, "target_hit_time"] = None
                else:
                    group.loc[:, "target_hit"] = False
                    group.loc[:, "target_hit_time"] = None
                return group

        if symbol not in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
            raise ValueError("Symbol must be one of NIFTY, BANKNIFTY or FINNIFTY")

        strike_base = 100 if symbol == "BANKNIFTY" else 50
        expiry_on = 1 if symbol == "FINNIFTY" else 3

        # Truncating the data to the same date range as the stockmock data
        one_min_df = one_min_df.loc[
            pd.to_datetime(one_min_df.index.date).isin(iv_df.index)
        ]

        one_min_df = prepare_one_min_df_for_backtest(one_min_df)

        open_prices = (
            one_min_df.groupby(one_min_df["date"].dt.date)
            .apply(lambda x: x.iloc[0])
            .open.to_frame()
        )

        close_prices = (
            one_min_df.groupby(one_min_df["date"].dt.date).close.last().to_frame()
        )

        day_info = open_prices.merge(
            close_prices, left_index=True, right_index=True
        ).merge(iv_df, left_index=True, right_index=True)

        day_info.columns = [
            "open",
            "close",
            "iv",
        ]

        day_info["strike"] = day_info.open.apply(
            lambda x: vs.findstrike(x, strike_base)
        )
        day_info["expiry"] = day_info.index.to_series().apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                x, expiry_on=expiry_on
            ).replace(hour=15, minute=30)
        )
        # Setting info about the open
        one_min_df[["open_strike", "day_close", "open_iv", "expiry"]] = (
            day_info[["strike", "close", "iv", "expiry"]]
            .loc[one_min_df.index.date]
            .values
        )
        one_min_df["open_strike"] = one_min_df["open_strike"].astype(int)

        # Calculating final payoff
        one_min_df["payoff"] = (one_min_df.day_close - one_min_df.open_strike).abs()

        # Filtering down to only expiry days
        one_min_df = one_min_df.loc[one_min_df.expiry.dt.date == one_min_df.index.date]

        # Adding running time to expiry
        one_min_df["time_to_expiry"] = (
            one_min_df.expiry - one_min_df.index
        ) / timedelta(days=365)

        # Modelling IV throughout the day
        one_min_df["current_iv"] = one_min_df.apply(
            lambda row: vs.bs.simulate_iv(
                strike=row.open_strike,
                original_iv=row.open_iv,
                original_spot=one_min_df.close.iloc[0],
                original_time_to_expiry=one_min_df.time_to_expiry.iloc[0],
                new_spot=row.close,
                new_time_to_expiry=row.time_to_expiry,
                symbol=symbol,
            ),
            axis=1,
        )

        # Calculating the premium
        one_min_df["tracked_straddle_premium"] = one_min_df.apply(
            lambda row: vs.calc_combined_premium(
                row.close, row.time_to_expiry, strike=row.open_strike, iv=row.current_iv
            ),
            axis=1,
        )

        # Using the function
        with_entry_details = one_min_df.groupby(one_min_df.index.date).apply(
            lambda group: buy_straddle_if_price_touched(group)
        )

        # Converting the data to a DataFrame
        one_min_df = with_entry_details.reset_index(level=0, drop=True)

        # Summary DataFrame
        summary_df = one_min_df.groupby(one_min_df.index.date).agg(
            {
                "open_strike": "first",
                "day_close": "first",
                "open_iv": "first",
                "payoff": "first",
                "touched_price": "first",
                "touched_time": "first",
                "target_hit": "first",
                "target_hit_time": "first",
            }
        )
        summary_df["our_payoff"] = np.where(
            summary_df.target_hit == False, summary_df.payoff, summary_df.target_hit
        )
        summary_df["profit"] = summary_df.our_payoff - summary_df.touched_price

        return summary_df, one_min_df

    def backtest_intraday_strangle(
        self,
        one_min_df,
        iv_df,
        symbol,
        call_offset=0,
        put_offset=0,
        iv_decay=0,
        enter_minute=0,
    ):
        expiry_weekday = 1 if symbol == "FINNIFTY" else 3
        strike_base = 100 if symbol == "BANKNIFTY" else 50

        one_min_df = prepare_one_min_df_for_backtest(one_min_df)

        open_prices = (
            one_min_df.groupby(one_min_df["date"].dt.date)
            .apply(lambda x: x.iloc[enter_minute])
            .open.to_frame()
        )

        close_prices = (
            one_min_df.groupby(one_min_df["date"].dt.date).close.last().to_frame()
        )

        day_info = open_prices.merge(
            close_prices, left_index=True, right_index=True
        ).merge(iv_df, left_index=True, right_index=True)

        day_info.columns = [
            "open",
            "close",
            "iv",
        ]

        day_info["date"] = day_info.index

        day_info["start_time_to_expiry"] = day_info.date.apply(
            lambda x: self.historic_time_to_expiry(
                x.replace(hour=9, minute=15), expiry_weekday
            )
        )

        day_info["end_time_to_expiry"] = day_info.date.apply(
            lambda x: self.historic_time_to_expiry(
                x.replace(hour=15, minute=30), expiry_weekday
            )
        )

        day_info["traded_call_strike"] = (day_info.open * (1 + call_offset)).apply(
            lambda x: vs.findstrike(x, strike_base)
        )
        day_info["traded_put_strike"] = (day_info.open * (1 - put_offset)).apply(
            lambda x: vs.findstrike(x, strike_base)
        )

        day_info["start_premium"] = day_info.apply(
            lambda row: vs.calc_combined_premium(
                row.open,
                row.start_time_to_expiry,
                call_strike=row.traded_call_strike,
                put_strike=row.traded_put_strike,
                call_iv=vs.bs.adjusted_iv_from_atm_iv(
                    row.iv,
                    row.traded_call_strike,
                    row.open,
                    row.start_time_to_expiry,
                    symbol=symbol,
                ),
                put_iv=vs.bs.adjusted_iv_from_atm_iv(
                    row.iv,
                    row.traded_put_strike,
                    row.open,
                    row.start_time_to_expiry,
                    symbol=symbol,
                ),
            ),
            axis=1,
        )
        day_info["end_premium"] = day_info.apply(
            lambda row: vs.calc_combined_premium(
                row.close,
                row.end_time_to_expiry,
                call_strike=row.traded_call_strike,
                put_strike=row.traded_put_strike,
                call_iv=vs.bs.adjusted_iv_from_atm_iv(
                    row.iv * (1 - iv_decay),
                    row.traded_call_strike,
                    row.close,
                    row.end_time_to_expiry,
                    symbol=symbol,
                ),
                put_iv=vs.bs.adjusted_iv_from_atm_iv(
                    row.iv * (1 - iv_decay),
                    row.traded_put_strike,
                    row.close,
                    row.end_time_to_expiry,
                    symbol=symbol,
                ),
            ),
            axis=1,
        )
        day_info["payoff"] = day_info.start_premium - day_info.end_premium

        day_info = nav_drawdown_analyser(day_info, "payoff", "open")

        return day_info

    @staticmethod
    def backtest_intraday_trend(
        one_min_df,
        vix_df,
        open_nth=0,
        beta=1,
        fixed_trend_threshold=None,
        stop_loss=0.3,
        max_entries=3,
        rolling_days=60,
        randomize=False,
    ):
        one_min_df = prepare_one_min_df_for_backtest(one_min_df)

        vix = vix_df.copy()
        vix["open"] = vix["open"] * beta
        vix["close"] = vix["close"] * beta

        open_prices = (
            one_min_df.groupby(one_min_df["date"].dt.date)
            .apply(lambda x: x.iloc[open_nth])
            .open.to_frame()
        )
        open_data = open_prices.merge(
            vix["open"].to_frame(),
            left_index=True,
            right_index=True,
            suffixes=("", "_vix"),
        )

        if randomize:
            fixed_trend_threshold = 0.0001

        open_data["threshold_movement"] = fixed_trend_threshold or (
            open_data["open_vix"] / 48
        )
        open_data["upper_bound"] = open_data["open"] * (
            1 + open_data["threshold_movement"] / 100
        )
        open_data["lower_bound"] = open_data["open"] * (
            1 - open_data["threshold_movement"] / 100
        )
        open_data["day_close"] = one_min_df.groupby(
            one_min_df["date"].dt.date
        ).close.last()

        daily_minute_vols = one_min_df.groupby(one_min_df["date"].dt.date).apply(
            lambda x: x["close"].pct_change().abs().mean() * 100
        )

        daily_minute_vols_rolling = daily_minute_vols.rolling(
            rolling_days, min_periods=1
        ).mean()

        daily_open_to_close_trends = one_min_df.open.groupby(
            one_min_df["date"].dt.date
        ).apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)

        daily_open_to_close_trends_rolling = (
            daily_open_to_close_trends.abs().rolling(rolling_days, min_periods=1).mean()
        )

        rolling_ratio = daily_open_to_close_trends_rolling / daily_minute_vols_rolling

        open_data.columns = [
            "day_open",
            "open_vix",
            "threshold_movement",
            "upper_bound",
            "lower_bound",
            "day_close",
        ]
        one_min_df[
            [
                "day_open",
                "open_vix",
                "threshold_movement",
                "upper_bound",
                "lower_bound",
                "day_close",
            ]
        ] = open_data.loc[one_min_df["date"].dt.date].values
        one_min_df["change_from_open"] = (
            (one_min_df["close"] / one_min_df["day_open"]) - 1
        ) * 100

        def calculate_daily_trade_data(group):
            """The group is a dataframe"""

            all_entries_in_a_day = {}
            # Find the first index where the absolute price change crosses the threshold
            entry = 1
            while entry <= max_entries:
                # Filtering the dataframe to only include the rows after open nth
                group = group.iloc[open_nth:]
                idx = group[
                    abs(group["change_from_open"]) >= group["threshold_movement"]
                ].first_valid_index()
                if idx is not None:  # if there is a crossing
                    result_dict = {
                        "returns": 0,
                        "trigger_time": np.nan,
                        "trigger_price": np.nan,
                        "trend_direction": np.nan,
                        "stop_loss_price": np.nan,
                        "stop_loss_time": np.nan,
                    }
                    # Record the price and time of crossing the threshold
                    cross_price = group.loc[idx, "close"]
                    cross_time = group.loc[idx, "date"]

                    # Determine the direction of the movement
                    if randomize:
                        direction = np.random.choice([-1, 1])
                    else:
                        direction = np.sign(group.loc[idx, "change_from_open"])

                    # Calculate the stoploss price
                    if stop_loss == "dynamic":
                        # Selecting previous days rolling ratio
                        current_rolling_ratio = rolling_ratio.loc[
                            : cross_time.date()
                        ].iloc[-1]
                        # Calculating the stop_loss pct
                        if current_rolling_ratio > 30:
                            stop_loss_pct = 0.3
                        elif current_rolling_ratio < 10:
                            stop_loss_pct = 0.5
                        else:
                            stop_loss_pct = ((30 - current_rolling_ratio) / 100) + 0.3
                    else:
                        stop_loss_pct = stop_loss

                    stoploss_price = cross_price * (
                        1 - (stop_loss_pct / 100) * direction
                    )
                    result_dict.update(
                        {
                            "trigger_time": cross_time,
                            "trigger_price": cross_price,
                            "trend_direction": direction,
                            "stop_loss_price": stoploss_price,
                        }
                    )
                    future_prices = group.loc[idx:, "close"]

                    if (direction == 1 and future_prices.min() <= stoploss_price) or (
                        direction == -1 and future_prices.max() >= stoploss_price
                    ):  # Stop loss was breached
                        result_dict["returns"] = -stop_loss_pct
                        stoploss_time_idx = (
                            future_prices[
                                future_prices <= stoploss_price
                            ].first_valid_index()
                            if direction == 1
                            else future_prices[
                                future_prices >= stoploss_price
                            ].first_valid_index()
                        )
                        stoploss_time = group.loc[stoploss_time_idx, "date"]
                        result_dict["stop_loss_time"] = stoploss_time
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        group = group.loc[stoploss_time_idx:]
                        entry += 1
                    else:  # Stop loss was not breached
                        if direction == 1:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * 100
                        else:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * -100
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        break
                else:
                    break

            all_entries_in_a_day["total_returns"] = sum(
                [v["returns"] for v in all_entries_in_a_day.values()]
            )
            return all_entries_in_a_day

        # Applying the function to each day's worth of data
        returns = one_min_df.groupby(one_min_df["date"].dt.date).apply(
            calculate_daily_trade_data
        )
        returns = returns.to_frame()
        returns.index = pd.to_datetime(returns.index)
        returns.columns = ["trade_data"]

        # merging with open_data
        merged = returns.merge(open_data, left_index=True, right_index=True)
        merged["total_returns"] = merged["trade_data"].apply(
            lambda x: x["total_returns"]
        )

        merged["predicted_trend"] = merged.trade_data.apply(
            lambda x: x.get("entry_1", {}).get("trend_direction", None)
        )

        # calculating prediction accuracy
        merged["actual_trend"] = daily_open_to_close_trends.apply(np.sign)
        merged["trend_match"] = merged.predicted_trend == merged.actual_trend
        merged["rolling_prediction_accuracy"] = (
            merged[~pd.isna(merged.predicted_trend)]
            .trend_match.expanding(min_periods=1)
            .mean()
        )
        merged["rolling_prediction_accuracy"] = merged[
            "rolling_prediction_accuracy"
        ].fillna(method="ffill")

        merged = nav_drawdown_analyser(
            merged, column_to_convert="total_returns", profit_in_pct=True
        )

        # calculating the minute vol
        merged["minute_vol"] = daily_minute_vols

        # calculating the open to close trend
        merged["open_to_close_trend"] = daily_open_to_close_trends

        merged["open_to_close_trend_abs"] = merged["open_to_close_trend"].abs()

        # calculating the ratio and rolling mean
        merged["minute_vol_rolling"] = daily_minute_vols_rolling
        merged["open_to_close_trend_rolling"] = daily_open_to_close_trends_rolling
        merged["ratio"] = merged["open_to_close_trend_abs"] / merged["minute_vol"]
        merged["rolling_ratio"] = rolling_ratio

        return merged


def retain_name(func):
    def wrapper(df, *args, **kwargs):
        try:
            name = df.name
        except AttributeError:
            name = None
        df = func(df, *args, **kwargs)
        df.name = name
        return df

    return wrapper


def analyser(df, frequency=None, date_filter=None, _print=False):
    name = df.name
    if date_filter is None:
        pass
    else:
        dates = date_filter.split("to")
        if len(dates) > 1:
            df = df.loc[dates[0] : dates[1]]
        else:
            df = df.loc[dates[0]]

    frequency = frequency.upper() if frequency is not None else None

    if frequency is None or frequency.startswith("D") or frequency == "B":
        custom_frequency = "B"
        multiplier = 24
        df = df.resample("B").ffill()

    elif frequency.startswith("W") or frequency.startswith("M"):
        custom_frequency = frequency
        if frequency.startswith("W"):
            multiplier = 9.09
            df = df.resample(frequency).ffill()
        elif frequency.startswith("M"):
            multiplier = 4.4
            if len(frequency) == 1:
                df = df.resample("M").ffill()
            else:
                weekday_module_dict = {
                    "MON": MO,
                    "TUE": TU,
                    "WED": WE,
                    "THU": TH,
                    "FRI": FR,
                }
                frequency = frequency.lstrip("M-")
                df = df.resample(f"W-{frequency.upper()}").ffill()
                df = df.resample("M").ffill()
                df.index = df.index.date + relativedelta(
                    weekday=weekday_module_dict[frequency.upper()](-1)
                )
                df.index = pd.Series(pd.to_datetime(df.index), name="date")
        else:
            raise ValueError("Frequency not supported")
    else:
        raise ValueError("Frequency not supported")

    df.loc[:, "change"] = df.close.pct_change() * 100
    df.loc[:, "open_change"] = ((df.open / df.close.shift(1)) - 1) * 100
    df.loc[:, "abs_change"] = abs(df.change)
    df.loc[:, "abs_open_change"] = abs(df.open_change)
    df.loc[:, "realized_vol"] = df.abs_change * multiplier

    if frequency in ["D-MON", "D-TUE", "D-WED", "D-THU", "D-FRI"]:
        day_of_week = frequency.split("-")[1]
        df = df[df.index.day_name().str.upper().str.contains(day_of_week)]

    if _print:
        print(
            "Vol for period: {:0.2f}%, IV: {:0.2f}%".format(
                df.abs_change.mean(), df.abs_change.mean() * multiplier
            )
        )
    else:
        pass

    df.custom_frequency = custom_frequency.upper()
    df.name = name
    return df


def get_recent_vol(df, periods=None, ignore_last=1):
    """Returns a dictionary of vol for each period in periods list
    :param df: Dataframe with 'abs_change' column
    :param periods: List of periods to calculate vol for
    :param ignore_last: Number of rows to ignore from the end
    :return: Dictionary of vol for each period in periods list
    """

    if periods is None:
        periods = [5]
    else:
        periods = [periods] if isinstance(periods, int) else periods

    if ignore_last == 0:
        df = df
    else:
        df = df.iloc[:-ignore_last]

    vol_dict = {}
    for period in periods:
        abs_change = df.tail(period).abs_change.mean()
        realized_vol = df.tail(period).realized_vol.mean()
        vol_dict[period] = (abs_change, realized_vol)
    return vol_dict


def get_multiple_recent_vol(
    list_of_symbols, frequency, periods=None, ignore_last=1, client=None
):
    if client is None:
        client = DataClient(api_key=__import__("os").environ.get("EOD_API_KEY"))
    df_dict = {}
    for symbol in list_of_symbols:
        symbol_data = client.get_data(symbol=symbol)
        symbol_monthly_data = analyser(symbol_data, frequency=frequency)
        recent_vol = get_recent_vol(
            symbol_monthly_data, periods=periods, ignore_last=ignore_last
        )
        df_dict[symbol] = recent_vol
    return df_dict


def ratio_analysis(
    x_df: pd.DataFrame,
    y_df: pd.DataFrame,
    periods_to_avg: int = None,
    return_summary=True,
    add_rolling: bool | int = False,
):
    if periods_to_avg is None:
        periods_to_avg = len(x_df)

    x_close = x_df.iloc[-periods_to_avg:].close
    x_array = x_df.iloc[-periods_to_avg:].abs_change
    x_avg = x_array.mean()

    y_close = y_df.iloc[-periods_to_avg:].close
    y_array = y_df.iloc[-periods_to_avg:].abs_change
    y_avg = y_array.mean()

    avg_ratio = x_avg / y_avg
    ratio_array = x_df.abs_change / y_df.abs_change
    ratio_array = ratio_array[-periods_to_avg:]

    labels = [x_df.name, y_df.name]

    ratio_summary = pd.DataFrame(
        {
            labels[0]: x_close,
            f"{labels[0]} Change": x_array,
            labels[1]: y_close,
            f"{labels[1]} Change": y_array,
            "Ratio": ratio_array,
        }
    )
    # print(f'\n{periods_to_avg} Period Average = {avg_ratio}\n\n')
    if return_summary:
        ratio_summary.loc["Summary"] = ratio_summary.mean()
        ratio_summary.loc["Summary", "Ratio"] = avg_ratio

    if add_rolling:
        rolling_x_avg = x_array.rolling(add_rolling, min_periods=1).mean()
        rolling_y_avg = y_array.rolling(add_rolling, min_periods=1).mean()
        rolling_ratio = rolling_x_avg / rolling_y_avg
        ratio_summary[f"Rolling {add_rolling} Ratio"] = rolling_ratio

    return ratio_summary


def get_summary_ratio(
    target_symbol, benchmark_symbol, frequency="D", periods_to_avg=50, client=None
):
    try:
        if client is None:
            try:
                dc = DataClient()
            except ApiKeyNotFound:
                return None
        else:
            dc = client

        from_date = vs.currenttime() - timedelta(days=2 * periods_to_avg)
        from_date = from_date.date().strftime("%Y-%m-%d")
        benchmark = dc.get_data(benchmark_symbol, from_date=from_date)
        target = dc.get_data(target_symbol, from_date=from_date)
        benchmark = analyser(benchmark, frequency=frequency)
        target = analyser(target, frequency=frequency)
        ratio = ratio_analysis(target, benchmark, periods_to_avg=periods_to_avg)
        return ratio.loc["Summary", "Ratio"]
    except Exception as e:
        vs.logger.error(f"Error in get_summary_ratio: {e}")
        return None


@retain_name
def generate_streak(df, query):
    df = df.copy(deep=True)

    # Create a boolean series with the query
    _bool = df.query(f"{query}")
    df["result"] = df.index.isin(_bool.index)
    df["start_of_streak"] = (df["result"].ne(df["result"].shift())) & (
        df["result"] == True
    )
    df["streak_id"] = df.start_of_streak.cumsum()
    df.loc[df["result"] == False, "streak_id"] = np.nan
    df["streak_count"] = df.groupby("streak_id").cumcount() + 1

    return df[df.result == True].drop(columns=["start_of_streak"])


@retain_name
def gambler(instrument, freq, query):
    """
    This function takes in instrument dataframe, frequency, and query and returns the streaks for the query.
    The instrument df should be a dataframe with daily closing values.
    The query should be a string with the following format: '{column} {operator} {value}'.
    The column should be a column in the instrument dataframe.
    The operator should be one of the following: '>', '<', '>=', '<=', '==', '!='.
    The value should be a number.
    """

    def generate_frequency(frequency):
        if frequency.startswith("W") or frequency.startswith("M"):
            if len(frequency) == 1:
                days = ["mon", "tue", "wed", "thu", "fri"]
                return [f"{frequency}-{day}" for day in days]
            else:
                return [frequency]
        else:
            return [frequency]

    def _calculate_streak_summary(df, frequency, query):
        # Calculate the streak summary

        if df.index[-1].replace(hour=15, minute=30) > vs.currenttime():
            df = df.iloc[:-1]
        check_date = df.index[-1]
        total_instances = len(df)
        df = generate_streak(df, query)
        total_streaks = len(df)
        number_of_positive_events = total_instances - total_streaks
        event_occurrence_pct = number_of_positive_events / total_instances

        df = (
            df.reset_index()
            .groupby("streak_id")
            .agg({"date": ["min", "max"], "streak_count": "max"})
            .reset_index()
        )
        df.columns = ["streak_id", "start_date", "end_date", "streak_count"]

        # Check if there is an ongoing streak
        current_streak = (
            df.iloc[-1].streak_count if df.iloc[-1].end_date == check_date else None
        )

        # Calculating the percentile of the current streak
        if current_streak:
            current_streak_percentile = (
                df.streak_count.sort_values().values.searchsorted(current_streak)
                / len(df)
            )
        else:
            current_streak_percentile = 0

        return {
            "freq": frequency,  # Use the given freq value instead of df.iloc[-1].name
            "total_instances": total_instances,
            "total_streaks": total_streaks,
            "event_occurrence": event_occurrence_pct,
            "longest_streak": df.streak_count.max(),
            "longest_streak_start": df.start_date[df.streak_count.idxmax()],
            "longest_streak_end": df.end_date[df.streak_count.idxmax()],
            "current_streak": current_streak,
            "current_streak_percentile": current_streak_percentile,
            "dataframe": df,
        }

    def print_streak_summary(summary):
        print(
            f"Query: {dataframe.name} {query}\n"
            f"Frequency: {summary['freq']}\n"
            f"Total Instances: {summary['total_instances']}\n"
            f"Total Streaks: {summary['total_streaks']}\n"
            f"Event Occurrence: {summary['event_occurrence']}\n"
            f"Longest Streak: {summary['longest_streak']}\n"
            f"Longest Streak Start: {summary['longest_streak_start']}\n"
            f"Longest Streak End: {summary['longest_streak_end']}\n"
            f"Current Streak: {summary['current_streak']}\n"
            f"Current Streak Percentile: {summary['current_streak_percentile']}\n"
        )

    freqs = generate_frequency(freq)
    streaks = []
    for freq in freqs:
        dataframe = analyser(instrument, frequency=freq)
        if query == "abs_change":
            recommended_threshold = (
                dataframe.abs_change.mean() * 0.70
            )  # 0.70 should cover 50% of the data
            # (mildly adjusted for abnormal distribution)
            recommended_threshold = round(recommended_threshold, 2)
            recommended_sign = (
                ">" if dataframe.iloc[-2].abs_change > recommended_threshold else "<"
            )
            query = f"abs_change {recommended_sign} {recommended_threshold}"
            print(f"Recommended query: {query}\n")
        streak_summary = _calculate_streak_summary(dataframe, freq, query)
        streaks.append(streak_summary)
        print_streak_summary(streak_summary)
    # Convert the list of dictionaries to a list of DataFrames
    streaks_df = [pd.DataFrame([streak]) for streak in streaks]

    # Concatenate the list of DataFrames
    return (
        pd.concat(streaks_df)
        .sort_values("longest_streak", ascending=False)
        .reset_index(drop=True)
    )


def simulate_strike_premium_payoff(
    close: pd.Series,
    iv: pd.Series,
    time_to_expiry: pd.Series,
    strike_offset: float,
    base: float = 100,
    label: str = "",
    action="buy",
):
    if label:
        label = f"{label}_"

    action = action.lower()

    if action not in ["buy", "sell"]:
        raise ValueError("action must be either 'buy' or 'sell'")

    data = pd.DataFrame(
        {
            "close": close,
            "iv": iv,
            "time_to_expiry": time_to_expiry,
        }
    )

    data["call_strike"] = data["close"].apply(
        lambda x: vs.findstrike(x * (1 + strike_offset), base)
    )
    data["put_strike"] = data["close"].apply(
        lambda x: vs.findstrike(x * (1 - strike_offset), base)
    )
    data["outcome_spot"] = data["close"].shift(-1)
    data["initial_premium"] = data.apply(
        lambda row: vs.calc_combined_premium(
            row.close,
            row.time_to_expiry,
            call_strike=row.call_strike,
            put_strike=row.put_strike,
            iv=row.iv / 100,
        ),
        axis=1,
    )
    data["outcome_premium"] = data.apply(
        lambda row: vs.calc_combined_premium(
            row.outcome_spot,
            0,
            call_strike=row.call_strike,
            put_strike=row.put_strike,
            iv=row.iv / 100,
        ),
        axis=1,
    )
    data["payoff"] = (
        data["initial_premium"] - data["outcome_premium"]
        if action == "sell"
        else data["outcome_premium"] - data["initial_premium"]
    )
    data["payoff"] = data["payoff"].shift(1)
    data["payoff_pct"] = data["payoff"] / data["close"]
    data = data[
        [
            "call_strike",
            "put_strike",
            "initial_premium",
            "outcome_premium",
            "payoff",
            "payoff_pct",
        ]
    ]
    data.columns = [f"{label}{col}" for col in data.columns]
    return data


def get_index_vs_constituents_recent_vols(
    index_symbol,
    return_all=False,
    simulate_backtest=False,
    strike_offset=0,
    hedge_offset=0,
    stock_vix_adjustment=0.7,
    index_action="sell",
):
    """
    Get the recent volatility of the index and its constituents
    """
    if return_all is False:
        simulate_backtest = False

    index = vs.Index(index_symbol)
    constituents, weights = index.get_constituents(cutoff_pct=90)
    weights = [w / sum(weights) for w in weights]

    dc = DataClient(api_key=__import__("os").environ["EOD_API_KEY"])

    index_data = dc.get_data(symbol=index_symbol)
    index_monthly_data = analyser(index_data, frequency="M-THU")
    index_monthly_data = index_monthly_data[["close", "abs_change"]]
    index_monthly_data.columns = ["index_close", "index_abs_change"]

    if simulate_backtest:
        if index_symbol == "BANKNIFTY":
            index_ivs = pd.read_csv(
                "data/banknifty_ivs.csv",
                parse_dates=True,
                index_col="date",
                dayfirst=True,
            )
            index_ivs.index = pd.to_datetime(index_ivs.index)
            index_ivs = index_ivs.resample("D").ffill()
            index_monthly_data = index_monthly_data.merge(
                index_ivs, left_index=True, right_index=True, how="left"
            )
            index_monthly_data["index_iv"] = index_monthly_data["close"].fillna(
                method="ffill"
            )
            index_monthly_data.drop(columns=["close"], inplace=True)
            index_monthly_data["iv_diff_from_mean"] = (
                index_monthly_data["index_iv"] / index_monthly_data["index_iv"].mean()
            )
            index_monthly_data["time_to_expiry"] = (
                index_monthly_data.index.to_series().diff().dt.days / 365
            )

            index_hedge_action = "buy" if index_action == "sell" else "sell"

            # The main strike
            simulated_data = simulate_strike_premium_payoff(
                index_monthly_data["index_close"],
                index_monthly_data["index_iv"],
                index_monthly_data["time_to_expiry"],
                strike_offset,
                100,
                label="index",
                action=index_action,
            )
            index_monthly_data = index_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            index_monthly_data["index_initial_premium_pct"] = (
                index_monthly_data["index_initial_premium"]
                / index_monthly_data["index_close"]
            )

            # The hedge strike
            simulated_data = simulate_strike_premium_payoff(
                index_monthly_data["index_close"],
                index_monthly_data["index_iv"],
                index_monthly_data["time_to_expiry"],
                hedge_offset,
                100,
                label="index_hedge",
                action=index_hedge_action,
            )

            index_monthly_data = index_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            index_monthly_data["index_hedge_initial_premium_pct"] = (
                index_monthly_data["index_hedge_initial_premium"]
                / index_monthly_data["index_close"]
            )

            index_monthly_data["index_bep_pct"] = (
                index_monthly_data["index_initial_premium_pct"]
                - index_monthly_data["index_hedge_initial_premium_pct"]
            )

        else:
            raise NotImplementedError

    constituent_dfs = []
    for i, constituent in enumerate(constituents):
        constituent_data = dc.get_data(symbol=constituent)
        constituent_monthly_data = analyser(constituent_data, frequency="M-THU")
        constituent_monthly_data = constituent_monthly_data[["close", "abs_change"]]
        constituent_monthly_data.columns = [
            f"{constituent}_close",
            f"{constituent}_abs_change",
        ]
        constituent_monthly_data[f"{constituent}_abs_change_weighted"] = (
            constituent_monthly_data[f"{constituent}_abs_change"] * weights[i]
        )

        if simulate_backtest:
            constituent_monthly_data[f"{constituent}_iv"] = index_monthly_data[
                "iv_diff_from_mean"
            ] * (
                (
                    constituent_monthly_data[f"{constituent}_abs_change"].mean()
                    - stock_vix_adjustment
                )
                * 4.4
            )  # the adjustment factor is to account for the spurious volatility on account of splits

            constituent_action = "buy" if index_action == "sell" else "sell"
            constituent_hedge_action = "sell" if constituent_action == "buy" else "sell"

            # The main strike
            simulated_data = simulate_strike_premium_payoff(
                constituent_monthly_data[f"{constituent}_close"],
                constituent_monthly_data[f"{constituent}_iv"],
                index_monthly_data["time_to_expiry"],
                strike_offset,
                5,
                label=constituent,
                action=constituent_action,
            )
            constituent_monthly_data = constituent_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            constituent_monthly_data[f"{constituent}_initial_premium_pct"] = (
                constituent_monthly_data[f"{constituent}_initial_premium"]
                / constituent_monthly_data[f"{constituent}_close"]
            )

            # The hedge strike
            simulated_data = simulate_strike_premium_payoff(
                constituent_monthly_data[f"{constituent}_close"],
                constituent_monthly_data[f"{constituent}_iv"],
                index_monthly_data["time_to_expiry"],
                hedge_offset,
                5,
                label=f"{constituent}_hedge",
                action=constituent_hedge_action,
            )
            constituent_monthly_data = constituent_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            constituent_monthly_data[f"{constituent}_hedge_initial_premium_pct"] = (
                constituent_monthly_data[f"{constituent}_hedge_initial_premium"]
                / constituent_monthly_data[f"{constituent}_close"]
            )

            constituent_monthly_data[f"{constituent}_bep_pct"] = (
                constituent_monthly_data[f"{constituent}_initial_premium_pct"]
                - constituent_monthly_data[f"{constituent}_hedge_initial_premium_pct"]
            )

            constituent_monthly_data[f"{constituent}_total_payoff"] = (
                constituent_monthly_data[f"{constituent}_payoff"]
                + constituent_monthly_data[f"{constituent}_hedge_payoff"]
            )
            constituent_monthly_data[f"{constituent}_total_payoff_pct"] = (
                constituent_monthly_data[f"{constituent}_total_payoff"]
                / constituent_monthly_data[f"{constituent}_close"]
            )
            constituent_monthly_data[f"{constituent}_total_payoff_pct_weighted"] = (
                constituent_monthly_data[f"{constituent}_total_payoff_pct"] * weights[i]
            )

        constituent_dfs.append(constituent_monthly_data)

    index_monthly_data = index_monthly_data.merge(
        pd.concat(constituent_dfs, axis=1),
        left_index=True,
        right_index=True,
        how="inner",
    )
    index_monthly_data = index_monthly_data.copy()
    index_monthly_data["sum_constituent_movement"] = index_monthly_data.filter(
        regex="abs_change_weighted"
    ).sum(axis=1)
    index_monthly_data["ratio_of_movements"] = (
        index_monthly_data["sum_constituent_movement"]
        / index_monthly_data["index_abs_change"]
    )

    if simulate_backtest:
        index_monthly_data["index_total_payoff"] = (
            index_monthly_data["index_payoff"]
            + index_monthly_data["index_hedge_payoff"]
        )
        index_monthly_data["index_total_payoff_pct"] = (
            index_monthly_data["index_total_payoff"] / index_monthly_data["index_close"]
        )
        index_monthly_data["sum_constituent_payoff_pct"] = index_monthly_data.filter(
            regex="total_payoff_pct_weighted"
        ).sum(axis=1)

        index_monthly_data["total_combined_payoff_pct"] = (
            index_monthly_data["index_total_payoff_pct"]
            + index_monthly_data["sum_constituent_payoff_pct"]
        )

    if return_all:
        return index_monthly_data
    else:
        summary_df = index_monthly_data[
            ["index_abs_change", "sum_constituent_movement", "ratio_of_movements"]
        ]
        summary_df["index_rolling"] = (
            summary_df["index_abs_change"].rolling(12, min_periods=1).mean()
        )
        summary_df["cons_rolling"] = (
            summary_df["sum_constituent_movement"].rolling(12, min_periods=1).mean()
        )
        summary_df["rolling_ratio"] = (
            summary_df["cons_rolling"] / summary_df["index_rolling"]
        )
        return summary_df


def get_greenlit_kite(
    kite_api_key,
    kite_api_secret,
    kite_user_id,
    kite_password,
    kite_auth_key,
    chrome_path=None,
):
    if chrome_path is None:
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Chrome(chrome_path)

    authkey_obj = pyotp.TOTP(kite_auth_key)
    kite = KiteConnect(api_key=kite_api_key)
    login_url = kite.login_url()

    driver.get(login_url)
    wait = WebDriverWait(driver, 10)  # waits for up to 10 seconds

    userid = wait.until(EC.presence_of_element_located((By.ID, "userid")))
    userid.send_keys(kite_user_id)

    password = wait.until(EC.presence_of_element_located((By.ID, "password")))
    password.send_keys(kite_password)

    submit = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "button-orange"))
    )
    submit.click()

    sleep(10)  # wait for the OTP input field to be clickable
    otp_input = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "input")))
    otp_input.send_keys(authkey_obj.now())

    # wait until the URL changes
    wait.until(url_changes(driver.current_url))

    # now you can safely get the current URL
    current_url = driver.current_url

    split_url = current_url.split("=")
    request_token = None
    for i, string in enumerate(split_url):
        if "request_token" in string:
            request_token = split_url[i + 1]
            request_token = (
                request_token.split("&")[0] if "&" in request_token else request_token
            )
            break

    driver.quit()

    if request_token is None:
        raise Exception("Request token not found")

    data = kite.generate_session(request_token, api_secret=kite_api_secret)
    kite.set_access_token(data["access_token"])

    return kite


def get_1m_data(kite, symbol, path="C:\\Users\\Administrator\\"):
    def fetch_minute_data_from_kite(_kite, _token, _from_date, _to_date):
        date_format = "%Y-%m-%d %H:%M:%S"
        _prices = _kite.historical_data(
            _token,
            from_date=_from_date.strftime(date_format),
            to_date=_to_date.strftime(date_format),
            interval="minute",
        )
        return _prices

    instruments = kite.instruments(exchange="NSE")
    token = [
        instrument["instrument_token"]
        for instrument in instruments
        if instrument["tradingsymbol"] == symbol
    ][0]

    try:
        main_df = pd.read_csv(
            f"{path}{symbol}_onemin_prices.csv", index_col=0, parse_dates=True
        )
        from_date = main_df.index[-1] + timedelta(minutes=1)
    except FileNotFoundError:
        print(f"No existing data for {symbol}, starting from scratch.")
        main_df = False
        from_date = datetime(2015, 1, 1, 9, 16)

    end_date = vs.currenttime()
    mainlist = []

    fetch_data_partial = partial(fetch_minute_data_from_kite, kite, token)

    while from_date < end_date:
        to_date = from_date + timedelta(days=60)
        prices = fetch_data_partial(from_date, to_date)
        if (
            len(prices) < 2 and not mainlist
        ):  # if there is no data for the period and no data at all
            print(
                f'No data for {from_date.strftime("%Y-%m-%d %H:%M:%S")} to {to_date.strftime("%Y-%m-%d %H:%M:%S")}'
            )
            if to_date > vs.currenttime():
                return None
            else:
                from_date += timedelta(days=60)
                continue
        else:  # if there is data for the period
            mainlist.extend(prices)
            from_date += timedelta(days=60)

    df = pd.DataFrame(mainlist).set_index("date")
    df.index = df.index.tz_localize(None)
    df = df[~df.index.duplicated(keep="first")]
    df = df[(df.index.time >= time(9, 15)) & (df.index.time <= time(15, 30))]
    df.to_csv(
        f"{path}{symbol}_onemin_prices.csv",
        mode="a",
        header=not isinstance(main_df, pd.DataFrame),
    )
    print(
        f"Finished fetching data for {symbol}. Fetched data from {df.index[0]} to {df.index[-1]}"
    )
    full_df = pd.concat([main_df, df]) if isinstance(main_df, pd.DataFrame) else df
    return full_df


def get_constituent_1m_data(kite_object, index_name, path="C:\\Users\\Administrator\\"):
    tickers, _weights = vs.get_index_constituents(index_name)
    for ticker in tickers:
        print(f"Fetching data for {ticker}")
        get_1m_data(kite_object, ticker, path=path)


def resample_series(times, series, interval="1min"):
    """
    Resamples a time series of implied volatility (IV) into the given interval.

    Args:
        times (list): A list of datetime objects representing the timestamps.
        series (list): A list of IV values corresponding to the timestamps.
        interval (str): The resampling interval (default is '1min').

    Returns:
        list, list: The resampled IV series and resampled timestamps.
    """
    # Create a DataFrame with the time series data
    df = pd.DataFrame({"iv": series}, index=times)

    # Resample the data into the given interval
    resampled_df = df.resample(interval).last().ffill()

    # Return the resampled IV series and timestamps as lists
    return resampled_df["iv"].tolist(), resampled_df.index.tolist()


def reorganize_captured_data(data: dict, interval: str = "1min") -> dict:
    """
    Resamples the data into one-minute intervals and reorganizes it into the desired hierarchy:
    index -> strike -> expiry -> call/put/total.

    Args:
        data (dict): The original data structure.
        interval (str): The resampling interval (default is '1min').

    Returns:
        dict: The resampled and reorganized data.
    """

    def parse_timestamp(time_string, date=None):
        # Check if the time_string contains only the time (based on the absence of "-")
        if time_string.count(":") == 2 and time_string.count("-") == 0:
            assert (
                date is not None
            ), "Date must be provided if time_string contains only the time"
            # If a date portion is provided, combine it with the time
            return datetime.fromisoformat(date + " " + time_string)
        # If the time_string contains both date and time, parse it directly
        else:
            return datetime.fromisoformat(time_string)

    def handle_data_field(
        data_dict, field_name, timestamps, resample_interval, reorg_data_dict, stk, exp
    ):
        # Check if the field exists in the data
        if field_name in ["call_ltps", "put_ltps", "call_ivs", "put_ivs", "total_ivs"]:
            field_values = data_dict[field_name]
            field_values = [*map(lambda x: vs.round_to_nearest(x, 3), field_values)]
            field_values, _ = resample_series(
                timestamps, field_values, resample_interval
            )
            reorg_data_dict[stk][exp][field_name] = field_values
        elif field_name == "times":
            _, resampled_ts = resample_series(timestamps, timestamps, resample_interval)
            reorg_data_dict[stk][exp]["times"] = resampled_ts
        else:
            pass

    reorganized_data = {}

    # Iterate through the indexes, expiries, and strikes
    for index_name, expiries in data.items():
        reorganized_data[index_name] = {}
        for expiry, strikes in expiries.items():
            for strike, strike_data in strikes.items():
                # Convert the strike to a string
                strike = str(strike)
                # Ensure the strike exists in the reorganized data
                if strike not in reorganized_data[index_name]:
                    reorganized_data[index_name][strike] = {}

                # Ensure the expiry exists in the reorganized data
                if expiry not in reorganized_data[index_name][strike]:
                    reorganized_data[index_name][strike][expiry] = {}

                # If the times are strings, parse them into datetime objects
                if isinstance(strike_data["times"][0], str):
                    # Extract the date portion from the last notified time if the times are only the time portion
                    if strike_data["times"][0].count("-") == 0:
                        date_portion = strike_data["last_notified_time"].split(" ")[0]
                        times = [
                            parse_timestamp(t, date_portion)
                            for t in strike_data["times"]
                        ]
                    else:
                        times = [parse_timestamp(t) for t in strike_data["times"]]

                # If the times are already datetime objects, use them directly
                elif isinstance(strike_data["times"][0], datetime):
                    times = strike_data["times"]

                # If the times are time objects, append the date portion to the times
                elif isinstance(strike_data["times"][0], time):
                    date_portion = strike_data["last_notified_time"].date()
                    times = [
                        datetime.combine(date_portion, t) for t in strike_data["times"]
                    ]

                else:
                    raise ValueError("Invalid type for times")

                data_fields = strike_data.keys()

                for field_name in data_fields:
                    handle_data_field(
                        strike_data,
                        field_name,
                        times,
                        interval,
                        reorganized_data[index_name],
                        strike,
                        expiry,
                    )

    return vs.convert_to_serializable(reorganized_data)


def merge_reorganized_data(existing_data: dict, new_data: dict) -> dict:
    """
    Merges the new data into the existing data.

    Args:
        existing_data (dict): The existing data.
        new_data (dict): The new data.

    Returns:
        dict: The merged data.
    """

    if existing_data is None:
        existing_data = defaultdict(dict)

    # Iterate through the indexes, expiries, and strikes
    for index_name, strikes in new_data.items():
        for strike, strike_data in strikes.items():
            for expiry, expiry_data in strike_data.items():
                if index_name not in existing_data:
                    existing_data[index_name] = {}

                # Ensure the strike exists in the existing data
                if strike not in existing_data[index_name]:
                    existing_data[index_name][strike] = {}

                # Ensure the expiry exists in the existing data
                if expiry not in existing_data[index_name][strike]:
                    existing_data[index_name][strike][expiry] = {}
                data_fields = [
                    "call_ltps",
                    "put_ltps",
                    "call_ivs",
                    "put_ivs",
                    "total_ivs",
                    "times",
                ]
                for field_name in data_fields:
                    if field_name not in existing_data[index_name][strike][expiry]:
                        existing_data[index_name][strike][expiry][field_name] = []
                    if (
                        field_name not in expiry_data
                        or len(expiry_data[field_name]) == 0
                    ):
                        new_data = [np.nan] * len(expiry_data["times"])
                    else:
                        new_data = expiry_data[field_name]

                    existing_data[index_name][strike][expiry][field_name].extend(
                        new_data
                    )

    return existing_data


def store_captured_data(new_data: dict, filename: str):
    """
    Merges the new reorganized data with the existing data and stores it in the same JSON file.

    Args:
        new_data (dict): The new reorganized data.
        filename (str): The name of the file that contains existing data. If the file does not exist, it will be created as an empty dictionary.
    """

    try:
        with open(filename, "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        vs.logger.info(
            f"File {filename} not found for storing captured price data. Creating a new file."
        )
        existing_data = {}
    except Exception as e:
        vs.logger.error(
            f"Error while reading file to store captured data {filename}: {e}"
        )
        raise e

    merged_data = merge_reorganized_data(existing_data, new_data)

    with open(filename, "w") as f:
        json.dump(merged_data, f)


def prepare_one_min_df_for_backtest(
    one_min_df, start_after=(9, 15), end_before=(15, 30)
):
    unavailable_dates = [
        datetime(2015, 2, 28).date(),
        datetime(2016, 10, 30).date(),
        datetime(2019, 10, 27).date(),
        datetime(2020, 2, 1).date(),
        datetime(2020, 11, 14).date(),
    ]

    one_min_df = one_min_df.copy()
    if one_min_df.index.name == "date":
        one_min_df = one_min_df.reset_index()
    one_min_df = one_min_df[
        (one_min_df["date"].dt.time > time(*start_after))
        & (one_min_df["date"].dt.time < time(*end_before))
    ]

    one_min_df.drop(
        one_min_df[one_min_df["date"].dt.date.isin(unavailable_dates)].index,
        inplace=True,
    )

    return one_min_df


def nav_drawdown_analyser(
    df,
    column_to_convert="profit",
    base_price_col="close",
    nav_start=100,
    profit_in_pct=False,
):
    """Supply an analysed dataframe with a column that has the profit/loss in percentage or absolute value.
    Params:
    df: Dataframe with the column to be converted to NAV
    column_to_convert: Column name to be converted to NAV (default: 'profit')
    nav_start: Starting NAV (default: 100)
    profit_in_pct: If the column is in percentage or absolute value (default: False)
    """

    df = df.copy(deep=True)
    if column_to_convert in df.columns:
        if profit_in_pct == False:
            df["profit_pct"] = (df[column_to_convert] / df[base_price_col]) * 100
        else:
            df["profit_pct"] = df[column_to_convert]
        df["strat_nav"] = ((df.profit_pct + 100) / 100).dropna().cumprod() * nav_start
        df["cum_max"] = df.strat_nav.cummax()
        df["drawdown"] = ((df.strat_nav / df.cum_max) - 1) * 100
        df["rolling_cagr"] = df[:-1].apply(
            lambda row: (
                (df.strat_nav[-1] / row.strat_nav)
                ** (1 / ((df.iloc[-1].name - row.name).days / 365))
                - 1
            )
            * 100,
            axis=1,
        )

        # Drawdown ID below
        df["drawdown_checker"] = np.where(df.drawdown != 0, 1, 0)
        df["change_in_trend"] = df.drawdown_checker.ne(df.drawdown_checker.shift(1))
        # df['streak_id'] = df.change_in_trend.cumsum()
        df["start_of_drawdown"] = np.where(
            (df.change_in_trend == True) & (df.drawdown_checker == 1), True, False
        )
        df["end_of_drawdown"] = np.where(
            (df.change_in_trend == True) & (df.drawdown_checker == 0), True, False
        )
        df["drawdown_id"] = df.start_of_drawdown.cumsum()
        df.drawdown_id = np.where(df.drawdown_checker == 1, df.drawdown_id, None)
        return df.drop(
            [
                "start_of_drawdown",
                "end_of_drawdown",
                "drawdown_checker",
                "change_in_trend",
            ],
            axis=1,
        )
    else:
        print("No profit column found in df.")


def read_excel_file(filename):
    filename_without_extension = filename.split(".")[0]
    return pd.read_excel(f"data\\{filename_without_extension}.xlsx", sheet_name=2)
