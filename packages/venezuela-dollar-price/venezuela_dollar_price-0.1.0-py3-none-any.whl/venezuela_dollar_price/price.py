from datetime import datetime


class Price:
    """
    A class used to represent Price information

    ...

    Attributes
    ----------
    type : str
        a string representing the type of price (based on what), the values are bcv, epv, binance
    rate : float
        a float representing the exchange rate
    date : datetime
        a datetime object representing the date of the price

    Methods
    -------
    calculate_amount(value):
        calculates the amount from a given value using the provided exchange rate
    """

    def __init__(self, type: str, rate: float, date: datetime):
        """
        Constructs all the necessary attributes for the Price object.

        Parameters
        ----------
            type : str
                a string representing the type of price (based on what), the values are bcv, prom_epv, binance
            rate : float
                a float representing the exchange rate
            date : datetime
                a datetime object representing the date of the price
        """
        self.type = type
        assert type in [
            "bcv", "prom_epv",
            "binance"
        ], "type must be bcv, epv or binance"
        self.rate = rate
        self.date = date

    def calculate_amount(self, value: float) -> float:
        """
        calculates the amount from a given value using the provided exchange rate

        Parameters
        ----------
        value : float
            the value from which to calculate the amount

        Returns
        -------
        float
            returns the calculated amount
        """
        return value * self.rate