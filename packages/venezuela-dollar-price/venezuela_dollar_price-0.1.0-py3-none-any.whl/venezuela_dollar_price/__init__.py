__version__ = '0.1.0'

from .price import Price
import os
import requests
from datetime import datetime, timedelta, date
import re
import logging
from typing import Union

logger = logging.getLogger(__name__)

DOLLAR_API_URL = os.getenv(
    "DOLLAR_API_URL",
    "https://api.monitordolarvenezuela.com/dolarhoy"
)

DOLLAR_HISTORICAL_API_URL = os.getenv(
    "DOLLAR_HISTORICAL_API_URL",
    "https://api.monitordolarvenezuela.com/historialAnio/"
)

ACCEPTED_TYPES = {
    "bcv": "Banco Central de Venezuela",
    "prom_epv": "En Paralelo Venezuela",
    "binance": "Binance"
}


def __avg(max: str, min: str) -> float:
    """
    Calculates the average between two values

    Parameters
    ----------
    max : str
        a string representing the maximum value
    min : str
        a string representing the minimum value

    Returns
    -------
    float
        returns the average between the two values
    """
    if max in ["", None]:
        max = 0
    if min in ["", None]:
        min = 0

    return (float(max) + float(min)) / 2


def get_latest_price(type: str = "bcv") -> Union[Price, None]:
    """
    Gets the latest price from the API

    Parameters
    ----------
    type : str
        a string representing the type of price (based on what), the values are bcv, prom_epv, binance

    Returns
    -------
    Price
        returns a Price object with the latest price
    """
    assert type in ACCEPTED_TYPES.keys(), "type must be bcv, prom_epv or binance"
    try:
        response = requests.get(DOLLAR_API_URL)
        response.raise_for_status()
        data = response.json()
        return Price(
            type=type,
            rate=float(data["result"][0][type]),
            date=datetime.strptime(data["result"][0]["fecha"], "%Y-%m-%d")
        )
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Error getting latest price from API: %s" % err
        )
        return None
    except (KeyError, IndexError) as err:
        logger.error(
            "Error parsing latest price from API: %s" % err
        )
        return None


def get_historical_prices(
    start_date: Union[str, date] = (datetime.now() - timedelta(days=365)).date(),
    end_date: Union[str, date] = datetime.now().date()
):
    """
    Gets the historical prices from the API

    Parameters
    ----------
    start_date : datetime
        a datetime object representing the start date of the historical prices
    end_date : datetime
        a datetime object representing the end date of the historical prices

    Returns
    -------
    list
        returns a list of Price objects with the historical prices
    """
    if isinstance(start_date, str):
        # Check if the date is in the format YYYY-MM-DD
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date):
            raise ValueError(
                "start_date must be in the format YYYY-MM-DD"
            )
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        # Check if the date is in the format YYYY-MM-DD
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", end_date):
            raise ValueError(
                "end_date must be in the format YYYY-MM-DD"
            )
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Check if the start_date is before the end_date
    if start_date > end_date:
        raise ValueError(
            "start_date must be before end_date"
        )
    try:
        start_year = start_date.year
        end_year = end_date.year

        historical = []

        # iterate through the years
        for i in range(start_year, end_year + 1):

            response = requests.get(
                "%s/%s" % (
                    DOLLAR_HISTORICAL_API_URL,
                    i
                )
            )
            response.raise_for_status()
            data = response.json()

            results = data["result"][::-1]

            start_index = 0
            end_index = len(results)

            if i == start_year:

                # search for the start_date (get the index)
                start_index = next((index for (index, d) in enumerate(
                    results) if d["fecha"] == start_date.strftime("%d/%m/%Y")), None)

            if i == end_year:

                # search for the end_date (get the index)
                end_index = next(
                    (index for (index, d) in enumerate(results)
                     if d["fecha"] == end_date.strftime("%d/%m/%Y")),
                    None) + 1

            historical.extend(
                Price(
                    type="bcv",
                    rate=__avg(price["BcvMax"],price["BcvMin"]),
                    date=datetime.strptime(price["fecha"], "%d/%m/%Y")
                ) for price in results[start_index:end_index]
            )

        return historical

    except requests.exceptions.HTTPError as err:
        logger.error(
            "Error getting historical prices from API: %s" % err
        )
        return None
    except (KeyError, IndexError) as err:
        logger.error(
            "Error parsing historical prices from API: %s" % err
        )
        return None
