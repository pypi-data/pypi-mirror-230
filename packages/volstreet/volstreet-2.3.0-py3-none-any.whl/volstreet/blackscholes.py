from scipy.stats import norm
from scipy.optimize import brentq
import numpy as np
import logging
from datetime import datetime
from volstreet.exceptions import IntrinsicValueError
from volstreet.constants import iv_models
from collections import namedtuple
import warnings

bs_logger = logging.getLogger("blackscholes")
today = datetime.now().strftime("%Y-%m-%d")
file_handler = logging.FileHandler(f"bs-{today}.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
bs_logger.setLevel(logging.DEBUG)
bs_logger.addHandler(file_handler)
bs_logger.addHandler(stream_handler)

N = norm.cdf
binary_flag = {"c": 1, "p": -1}


def pdf(x):
    """the probability density function"""
    one_over_sqrt_two_pi = 0.3989422804014326779399460599343818684758586311649
    return one_over_sqrt_two_pi * np.exp(-0.5 * x * x)


def d1(S, K, t, r, sigma):
    sigma_squared = sigma * sigma
    numerator = np.log(S / float(K)) + (r + sigma_squared / 2.0) * t
    denominator = sigma * np.sqrt(t)

    if not denominator:
        print("")
    return numerator / denominator


def d2(S, K, t, r, sigma):
    return d1(S, K, t, r, sigma) - sigma * np.sqrt(t)


def forward_price(S, t, r):
    return S / np.exp(-r * t)


def call(S, K, t, r, sigma):
    e_to_the_minus_rt = np.exp(-r * t)
    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    return S * N(D1) - K * e_to_the_minus_rt * N(D2)


def put(S, K, t, r, sigma):
    e_to_the_minus_rt = np.exp(-r * t)
    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    return -S * N(-D1) + K * e_to_the_minus_rt * N(-D2)


def delta(S, K, t, r, sigma, flag):
    d_1 = d1(S, K, t, r, sigma)

    if flag.upper().startswith("P"):
        return N(d_1) - 1.0
    else:
        return N(d_1)


def gamma(S, K, t, r, sigma):
    d_1 = d1(S, K, t, r, sigma)
    return pdf(d_1) / (S * sigma * np.sqrt(t))


def theta(S, K, t, r, sigma, flag):
    two_sqrt_t = 2 * np.sqrt(t)

    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    first_term = (-S * pdf(D1) * sigma) / two_sqrt_t

    if flag.upper().startswith("C"):
        second_term = r * K * np.exp(-r * t) * N(D2)
        return (first_term - second_term) / 365.0

    else:
        second_term = r * K * np.exp(-r * t) * N(-D2)
        return (first_term + second_term) / 365.0


def vega(S, K, t, r, sigma):
    d_1 = d1(S, K, t, r, sigma)
    return S * pdf(d_1) * np.sqrt(t) * 0.01


def rho(S, K, t, r, sigma, flag):
    d_2 = d2(S, K, t, r, sigma)
    e_to_the_minus_rt = np.exp(-r * t)
    if flag.upper().startswith("C"):
        return t * K * e_to_the_minus_rt * N(d_2) * 0.01
    else:
        return -t * K * e_to_the_minus_rt * N(-d_2) * 0.01


def implied_volatility(price, S, K, t, r, flag):
    check_for_intrinsics(flag, S, K, price)
    if flag.upper().startswith("P"):
        f = lambda sigma: price - put(S, K, t, r, sigma)
    else:
        f = lambda sigma: price - call(S, K, t, r, sigma)

    try:
        return brentq(
            f, a=1e-12, b=100, xtol=1e-15, rtol=1e-15, maxiter=1000, full_output=False
        )
    except Exception as e:
        bs_logger.error(
            f"Error in implied_volatility: {e}, price={price}, S={S}, K={K}, t={t}, r={r}, flag={flag}"
        )
        raise e


def greeks(S, K, t, r, sigma, flag):
    greeks_tuple = namedtuple("Greeks", ["delta", "gamma", "theta", "vega"])
    return greeks_tuple(
        delta(S, K, t, r, sigma, flag),
        gamma(S, K, t, r, sigma),
        theta(S, K, t, r, sigma, flag),
        vega(S, K, t, r, sigma),
    )


def test_func():
    # Comparing time to calculate implied volatility using two different methods
    import timeit

    # Generate random data
    np.random.seed(42)
    Ss = np.random.uniform(40000, 45000, 100)
    Ks = np.random.uniform(40000, 45000, 100)
    ts = np.random.uniform(0.0027, 0.0191, 100)
    rs = np.array([0.05] * 100)
    flags = np.random.choice(["c", "p"], 100)
    sigmas = np.random.uniform(0.1, 0.5, 100)
    prices = np.array(
        [
            call(s, k, t, r, sigma) if f == "c" else put(s, k, t, r, sigma)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    deltas = np.array(
        [
            delta(s, k, t, r, sigma, f)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    gammas = np.array(
        [gamma(s, k, t, r, sigma) for s, k, t, r, sigma in zip(Ss, Ks, ts, rs, sigmas)]
    )
    thetas = np.array(
        [
            theta(s, k, t, r, sigma, f)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    vegas = np.array(
        [vega(s, k, t, r, sigma) for s, k, t, r, sigma in zip(Ss, Ks, ts, rs, sigmas)]
    )

    # Calculate implied volatility using two different methods
    start = timeit.default_timer()
    ivs = []
    for price, s, k, t, r, f in zip(prices, Ss, Ks, ts, rs, flags):
        iv = implied_volatility(price, s, k, t, r, f)
        ivs.append(iv)

    stop = timeit.default_timer()
    print("Time to calculate implied volatility using brentq: ", stop - start)

    import pandas as pd

    return pd.DataFrame(
        {
            "spot": Ss,
            "strike": Ks,
            "time": ts * 365,
            "rate": rs,
            "flag": flags,
            "sigma": sigmas,
            "price": prices,
            "delta": deltas,
            "gamma": gammas,
            "theta": thetas,
            "vega": vegas,
            "implied_volatility": ivs,
        }
    )


def check_for_intrinsics(flag, spot, strike, price):
    flag = flag.lower()[0]
    intrinsic_value = max(spot - strike, 0) if flag == "c" else max(strike - spot, 0)
    if intrinsic_value > price:
        bs_logger.error(
            f"Current price {price} of {'call' if flag == 'c' else 'put'} is less than the intrinsic value {intrinsic_value}"
        )
        raise IntrinsicValueError(
            f"Current price {price} of {'call' if flag == 'c' else 'put'} is less than the intrinsic value {intrinsic_value}"
        )


def get_iv_model_for_time_to_expiry(time_to_expiry):
    # Filtering the models based on the time to expiry
    filtered_model = [*filter(lambda x: x[0] <= time_to_expiry < x[1], iv_models)][0]
    # Returning the model for the segment
    return iv_models[filtered_model]


def iv_multiple_to_atm(time_to_expiry, spot, strike, symbol="NIFTY"):
    iv_model = get_iv_model_for_time_to_expiry(time_to_expiry)
    distance = (strike / spot) - 1
    distance_squared = distance**2
    moneyness = spot / strike
    distance_time_interaction = distance_squared * time_to_expiry
    finnifty = True if symbol.upper() == "FINNIFTY" else False
    nifty = True if symbol.upper() == "NIFTY" else False
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", category=UserWarning)
        return iv_model.predict(
            [
                [
                    distance,
                    distance_squared,
                    moneyness,
                    distance_time_interaction,
                    finnifty,
                    nifty,
                ]
            ]
        )[0]


def adjusted_iv_from_atm_iv(atm_iv, strike, spot, time_to_expiry, symbol="NIFTY"):
    iv_multiple = iv_multiple_to_atm(time_to_expiry, spot, strike, symbol)
    return atm_iv * iv_multiple


def set_symbol(symbol: str) -> str:
    return "NIFTY" if symbol is None else symbol.upper()


def adjust_iv_on_expiry_day(
    atm_iv: float, new_time_to_expiry: float, maximum_increase: float
) -> float:
    """Considers no increase in IV for the first 2 hours of the day
    and then increases linearly to the maximum increase"""

    opening_time_left_to_expiry = 375 / 525600
    increase_total_time = 255 / 525600
    time_delta = opening_time_left_to_expiry - new_time_to_expiry
    incremental_delta = max(time_delta - (120 / 525600), 0)
    vol_multiple = 1 + ((incremental_delta / increase_total_time) * maximum_increase)
    return atm_iv * vol_multiple


def get_simulation_inputs(
    strike: float | int,
    flag: str = None,
    original_iv: float = None,
    original_price: float = None,
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
) -> tuple[float, float, float, float, float]:
    """
    This function returns the simulation inputs for the transform_iv function.
    It handles the cases where the inputs are not provided and calculates the missing inputs.
    Important: Movement should be provided as a percentage with sign. For example, -0.005 for 0.5% decrease.
    """

    flag = flag.lower()[0] if flag else None

    # Set the original IV if not provided
    original_iv = original_iv or (
        implied_volatility(
            original_price,
            original_spot,
            strike,
            original_time_to_expiry,
            0.06,
            flag,
        )
        if original_price and original_spot and original_time_to_expiry
        else None
    )

    if not original_iv:
        raise ValueError(
            "Either original_iv or original_price, original_spot, and original_time_to_expiry must be provided."
        )

    # Set the new spot price if not provided
    new_spot = new_spot or (
        ((1 + movement) * original_spot) if original_spot and movement else None
    )
    if not new_spot:
        raise ValueError(
            "Either new_spot or original_spot and movement must be provided."
        )

    # Set the new time to expiry if not provided
    time_delta = time_delta or (
        (time_delta_minutes / 525600) if time_delta_minutes else None
    )

    new_time_to_expiry = new_time_to_expiry or (
        (original_time_to_expiry - time_delta)
        if original_time_to_expiry and time_delta
        else None
    )

    # Safety check for extremely low values
    if new_time_to_expiry < 0.000005:
        new_time_to_expiry = 0.000005

    if not new_time_to_expiry:
        raise ValueError(
            "Either new_time_to_expiry or original_time_to_expiry and time_delta (minutes or years) must be provided."
        )

    return (
        original_iv,
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    )


def simulate_iv(
    strike: float | int,
    flag: str = None,
    original_iv: float = None,
    original_price: float = None,
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
    symbol: str = None,
    maximum_increase: float = 0.8,
) -> float:
    """
    Starting from the original spot, strike and time to expiry, this function returns the adjusted implied volatility
    for that strike for the new spot and time to expiry.
    """

    bs_logger.debug(
        f"simulate_iv called with strike={strike}, "
        f"flag={flag}, original_iv={original_iv}, original_price={original_price}, "
        f"original_spot={original_spot}, original_time_to_expiry={original_time_to_expiry}, "
        f"new_spot={new_spot}, new_time_to_expiry={new_time_to_expiry}, movement={movement}, "
        f"time_delta_minutes={time_delta_minutes}, time_delta={time_delta}, symbol={symbol}, "
        f"maximum_increase={maximum_increase}"
    )

    symbol = set_symbol(symbol)

    (
        original_iv,
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    ) = get_simulation_inputs(
        strike,
        flag,
        original_iv,
        original_price,
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
        movement,
        time_delta_minutes,
        time_delta,
    )

    bs_logger.debug(
        f"simulate_iv inputs condensed to: strike={strike}, original_iv={original_iv}, "
        f"original_spot={original_spot}, "
        f"original_time_to_expiry={original_time_to_expiry}, "
        f"new_spot={new_spot}, new_time_to_expiry={new_time_to_expiry}"
    )

    # Adjust the IV to ATM IV
    current_iv_multiple = iv_multiple_to_atm(
        original_time_to_expiry, original_spot, strike, symbol
    )
    atm_iv = original_iv / current_iv_multiple

    bs_logger.debug(
        f"simulate_iv: used iv_multiple_to_atm to get current_iv_multiple={current_iv_multiple}."
        f"used it to adjust original_iv={original_iv} to atm_iv={atm_iv}"
    )

    # Transforming the IV for the new time to expiry (mainly expiry day adjustments)
    if new_time_to_expiry < 0.0008:
        if (
            original_time_to_expiry > 0.0020
        ):  # If jumping from non-expiry day to expiry day
            atm_iv *= 1 + maximum_increase

        # Adjusting the IV on the expiry day
        new_atm_iv = adjust_iv_on_expiry_day(
            atm_iv, new_time_to_expiry, maximum_increase
        )

    else:
        new_atm_iv = atm_iv

    bs_logger.debug(
        f"simulate_iv: adjusted atm_iv={atm_iv} to new_atm_iv={new_atm_iv} "
        f"based on proximity to expiry day."
    )

    iv_multiple_post_move = iv_multiple_to_atm(
        new_time_to_expiry, new_spot, strike, symbol
    )

    bs_logger.debug(
        f"simulate_iv: used iv_multiple_to_atm to get iv_multiple_post_move={iv_multiple_post_move}."
        f"used it to adjust new_atm_iv={new_atm_iv} to new_iv={new_atm_iv * iv_multiple_post_move}"
    )
    return new_atm_iv * iv_multiple_post_move


def simulate_price(
    strike: int | float,
    flag: str,
    original_iv: float = None,
    original_price: float = None,
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
    retain_original_iv: bool = False,
    symbol: str = None,
    maximum_increase_on_expiry_day: float = 0.8,
) -> float:
    """
    Extension of transform_iv function to simulate the option price.
    """

    symbol = set_symbol(symbol)
    flag = flag.lower()[0]

    (
        original_iv,
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    ) = get_simulation_inputs(
        strike,
        flag,
        original_iv,
        original_price,
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
        movement,
        time_delta_minutes,
        time_delta,
    )

    # Set the new IV
    if retain_original_iv:
        new_iv = original_iv
    else:
        new_iv = simulate_iv(
            strike=strike,
            original_iv=original_iv,
            original_spot=original_spot,
            original_time_to_expiry=original_time_to_expiry,
            new_spot=new_spot,
            new_time_to_expiry=new_time_to_expiry,
            symbol=symbol,
            maximum_increase=maximum_increase_on_expiry_day,
        )

    price_func = call if flag == "c" else put

    bs_logger.debug(
        f"simulate_price: calling price_func={price_func.__name__} with strike={strike}, "
        f"new_spot={new_spot}, new_time_to_expiry={new_time_to_expiry}, new_iv={new_iv}"
    )
    new_price = price_func(new_spot, strike, new_time_to_expiry, 0.06, new_iv)

    return max(new_price, 0.05)


def iv_curve_adjustor(
    movement,
    time_to_expiry,
    iv: int | tuple = 1,
    spot=100,
    strike=100,
    symbol="NIFTY",
    time_delta_minutes=None,
    print_details=False,
):
    """
    This function returns the adjusted implied volatility accounting for the curve effect.
    :param movement: movement of the underlying in percentage with sign
    :param time_to_expiry: time to expiry in years
    :param iv: implied volatility of the strike
    :param spot: spot price
    :param strike: strike price
    :param symbol: symbol for rhe random forest model
    :param time_delta_minutes: time delta in minutes
    :param print_details: print details of the adjustment
    :return: adjusted implied volatility for the strike after the movement
    """

    def get_iv_multiple_to_atm(tte, s, k, sym):
        # Model the IV curve using the random forest models
        return iv_multiple_to_atm(tte, s, k, sym)

    # Calculate the new spot price after the movement
    new_spot = spot * (1 + movement)

    # Get the IV multiple for the current displacement
    current_iv_multiple = get_iv_multiple_to_atm(time_to_expiry, spot, strike, symbol)

    # Normalize the given IV to the ATM level by dividing by the current IV multiple
    atm_iv = iv / current_iv_multiple

    # New time to expiry after the movement
    new_time_to_expiry = (
        time_to_expiry - (time_delta_minutes / 525600)
        if time_delta_minutes
        else time_to_expiry
    )

    if new_time_to_expiry < 0.000001:
        new_time_to_expiry = 0.000001

    # Apply the IV curve model to the new displacement
    premium_to_atm_iv = get_iv_multiple_to_atm(
        new_time_to_expiry, new_spot, strike, symbol
    )

    if (
        new_time_to_expiry < 0.0008
    ):  # On expiry day we need to adjust the vol as iv increases steadily as we approach expiry
        vol_multiple = 1 + (time_delta_minutes / 375)
        new_atm_iv = atm_iv * vol_multiple
    else:
        new_atm_iv = atm_iv

    # Scale the normalized ATM IV by the premium to get the new IV
    new_iv = new_atm_iv * premium_to_atm_iv

    if print_details:
        print(
            f"New IV: {new_iv} for Strike: {strike}\n"
            f"Starting IV: {iv}, ATM IV: {atm_iv}\nMovement {movement}\n"
            f"Spot after move: {new_spot}\n"
            f"Time to expiry: {new_time_to_expiry} from {time_to_expiry}"
        )

    return new_iv


def target_movement(
    flag,
    starting_price,
    target_price,
    starting_spot,
    strike,
    time_left,
    time_delta_minutes=None,
    symbol="NIFTY",
    print_details=False,
    backup_movement=None,
):
    """
    :param flag: 'c' or 'p'
    :param starting_price: current price of the option
    :param target_price: target price of the option
    :param starting_spot: current spot price
    :param strike: strike price
    :param time_left: time left to expiry in years
    :param time_delta_minutes: time delta in minutes
    :param print_details: print details of the adjustment
    :param symbol: symbol for the random forest model
    :param backup_movement: backup movement in case there is an IntrinsicValueError
    :return:
    """
    flag = flag.lower()[0]

    price_func = call if flag == "c" else put
    try:
        vol = implied_volatility(
            starting_price, starting_spot, strike, time_left, 0.06, flag
        )
    except IntrinsicValueError as e:
        if backup_movement is None:
            raise e
        else:
            return backup_movement
    new_time_left = (
        time_left - (time_delta_minutes / 525600) if time_delta_minutes else time_left
    )
    delta_ = delta(starting_spot, strike, new_time_left, 0.06, vol, flag)
    estimated_movement_points = (target_price - starting_price) / delta_
    estimated_movement = estimated_movement_points / starting_spot

    modified_vol = iv_curve_adjustor(
        estimated_movement,
        time_left,
        iv=vol,
        spot=starting_spot,
        strike=strike,
        symbol=symbol,
        time_delta_minutes=time_delta_minutes,
        print_details=print_details,
    )

    f = (
        lambda s1: price_func(s1, strike, new_time_left, 0.06, modified_vol)
        - target_price
    )

    # Setting the bounds for the brentq function
    if target_price > starting_price:
        if flag == "c":
            a = starting_spot * 0.1  # Remove hardcoded buffer
            b = 2 * starting_spot
        else:
            a = 0.05
            b = starting_spot * 2  # Remove hardcoded buffer
    else:
        if flag == "c":
            a = 0.05
            b = starting_spot * 2  # Remove hardcoded buffer
        else:
            a = starting_spot * 0.1  # Remove hardcoded buffer
            b = 2 * starting_spot

    target_spot = brentq(
        f, a=a, b=b, xtol=1e-15, rtol=1e-15, maxiter=1000, full_output=False
    )

    assert isinstance(target_spot, float)

    movement = (target_spot / starting_spot) - 1

    return movement
