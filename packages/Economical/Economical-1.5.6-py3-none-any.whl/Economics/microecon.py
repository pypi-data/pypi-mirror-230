#microeconomics sublibrary
from typing import Union

def index(givenperiodvalue, baseperiodvalue):
    """
    calculates the index number of any given period.

    :param givenperiodvalue:
    :param baseperiodvalue:
    :return: indexnumber
    """
    return ((abs(givenperiodvalue)) // (abs(baseperiodvalue))) * 100


class elasticity:

    @staticmethod
    def PriceEofDemand(q1,q2,p1,p2):
        """

        :param q1: quantity demanded 1
        :param q2: quantity demanded 2
        :param p1: price 1
        :param p2: price 2
        :return: E

        """
        #Percentage change in quantity demanded
        changeinQ = q2 - q1
        averageQ = (q1 + q2) / 2
        numerator = (changeinQ) / (averageQ)

        #percentage change in price
        changeinP = p2 - p1
        averageP = (p1 + p2) / 2
        denominator = (changeinP) / (averageP)

        #overall calculation
        E = numerator / denominator

        return E

    @staticmethod
    def PriceEofSupply(s1, s2, p1, p2):
        """

        :param s1: quantity supplied 1
        :param s2: quantity supplied 2
        :param p1: price 1
        :param p2: price 2
        :return: E

        """
        # Percentage change in quantity supplied
        changeinQ = s2 - s1
        averageQ = (s1 + s2) / 2
        numerator = (changeinQ) / (averageQ)

        # percentage change in price
        changeinP = p2 - p1
        averageP = (p1 + p2) / 2
        denominator = (changeinP) / (averageP)

        # overall calculation
        E = numerator / denominator

        return E

    @staticmethod
    def CrossEofDemand(q1x, q2x, p1y, p2y):
        """

        :param q1x: quantity demanded 1 of good x
        :param q2x: quantity demanded 2 of good x
        :param p1y: price 1 of good y
        :param p2y: price 2 of good y
        :return: E

        """
        # Percentage change in quantity demanded of good x
        changeinQ = q2x - q1x
        averageQ = (q1x + q2x) / 2
        numerator = (changeinQ) / (averageQ)

        # percentage change in price
        changeinP = p2y - p1y
        averageP = (p1y + p2y) / 2
        denominator = (changeinP) / (averageP)

        # overall calculation
        E = numerator / denominator

        return E



class cost:
    @staticmethod
    def average_total_cost(**kwargs: Union[int, None]):
        """

        :param kwargs: dictionary of parameters, to be passed as (atc = value, avc = value)
        to solve for a variable, provide two values and pass the variable to find with None as its value
        :return: ATCVAR, dictionary of values
        """
        if kwargs.get("afc") == None:
            valueafc = kwargs["atc"] - kwargs["avc"]
            resultkwargs = kwargs.update({"afc" : valueafc})
            return resultkwargs

        elif kwargs.get("avc") == None:
            valueavc = kwargs["atc"] - kwargs["afc"]
            resultkwargs = kwargs.update({"avc": valueavc})
            return resultkwargs

        elif kwargs.get("atc") == None:
            valueatc = kwargs["afc"] + kwargs["avc"]
            resultkwargs = kwargs.update({"atc": valueatc})
            return resultkwargs



    @staticmethod
    def marginal_cost(tc1: float,tc2: float,q1: float,q2: float):
        """

        :param tc1: totalcost 1
        :param tc2: totalcost 2
        :param q1: quantity 1
        :param q2: quantity 2
        :return: MC
        """

        #change in tc
        changetc = tc2 - tc1

        #change in q
        changeq = q2 - q1

        #overall calculation
        MC = (changetc)/(changeq)

        return MC

    @staticmethod
    def economic_profit(revenue: float, explicitcosts: float, implicitcosts: float):
        """

        :param revenue: income
        :param explicitcosts: costs from spending
        :param implicitcosts: costs in terms of oppurtunity cost
        :return: EP
        """

        #overall calculation
        EC = revenue - ((explicitcosts) + (implicitcosts))
        return EC


class definitions:
    def __init__(self):
        self.economics = " the study of the use of scarce resources to satisfy unlimited human wants"
        self.factors_of_production = "resources used to produce goods and services"
        self.labour = "mental and physics human resources"
        self.capital = "all manufactured aids to production such as tools machinery and buildings"
        self.opportunity_cost = """the value of the next best alternative that is forgone when one alternative is chosen.
Ratio of cost of obtaining one product to number of units that could have been obtained instead"""















