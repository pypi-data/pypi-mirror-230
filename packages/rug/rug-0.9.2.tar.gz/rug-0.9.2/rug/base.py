import re
from datetime import date, datetime
from html.parser import HTMLParser
from itertools import zip_longest

import httpx

from .exceptions import HttpException


class BaseAPI:
    timeout = 10
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
    )

    def __init__(self, symbol=None):
        """
        Constructor.

        :param str symbol: Symbol of te item we wanna get info about.
        """

        if symbol:
            self.symbol = str(symbol)

    def _get(self, *args, **kwargs):
        """
        Wraps https.get() method and raises custom exception
        in case of httpx expcetion.
        Also rises an exception for any non 2xx or 3xx status.
        """

        try:
            response = httpx.get(*args, timeout=self.timeout, **kwargs)
        except Exception as exc:
            raise HttpException(
                f"Couldn't perform GET request with args {args}"
            ) from exc

        response.raise_for_status()

        return response

    async def _aget(self, *args):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(*args, timeout=self.timeout)
            except Exception as exc:
                raise HttpException(
                    f"Couldn't perform GET request with args {args}"
                ) from exc

            response.raise_for_status()

            return response


class Data(dict):
    """
    Dict substitution which recursivelly handles
    non-existing keys.
    """

    def __getitem__(self, key):
        try:
            data = super().__getitem__(key)

            # If the data is dict we need to wrap it with
            # this class so it will carry this logic.
            if type(data) == dict:
                return self.__class__(data)

            # Data is not a dict so we return what we found.
            return data
        except:
            # In case of non existing key we return empty self
            # which makes sure another direct key demand will
            # copy this logic.
            return self.__class__()


class HtmlTableParser(HTMLParser):
    """
    Parses out all data from the given table and
    casts them into ``datetime.date`` or ``float``.

    Parsed data can be retrieved with ``get_data()`` method.
    """

    def __init__(self, columns, *args, **kwargs):
        """
        Constructor.

        :param int columns: Number of columns the given table has.
        """

        self.data = []
        self.columns = columns
        super().__init__(*args, **kwargs)

    def handle_data(self, data):
        if data := data.strip():
            self.data.append(self.parse_data(data))

    def parse_data(self, data):
        """
        Parses out all data from the given table and
        casts them into ``datetime.date`` or ``float``.
        """

        # Date in YYYY-MM-DD format.
        if re.match(r"\d{4}-\d{2}-\d{2}", data):
            try:
                return date.fromisoformat(data)
            except:
                pass

        # Date in MM-DD-YY where MM is short string
        # representation - like "May" or "Apr"
        if re.match(r"^[a-zA-Z]{3}-\d{2}-\d{2}$", data):
            try:
                return datetime.strptime(data, "%b-%d-%y").date()
            except:
                pass

        # Dollars (positive or negative floats).
        if re.match(r"^\$[+-]?([0-9]*[.])?[0-9]+$", data):
            try:
                return float(data[1:])
            except:
                pass

        # Int/float/percents (float or int with optional "%" sign as the last char).
        if re.match(r"^[0-9.,]+%?$", data):
            try:
                data = data.replace(",", "")
                return float(data[:-1] if "%" in data else data)
            except:
                pass

        if "--" == data:
            return 0.0

        return data

    def get_data(self, sort_by=0):
        """
        Splits data into ``self.columns`` list of lists
        and returns them.
        Rows are sorted chronologically.

        :param int sort_by: Column index to sort by. Use `None` to skip sorting.
        :return: Parsed, casted table data as rows.
        :rtype: list
        """

        data = list(zip_longest(*[iter(self.data)] * self.columns, fillvalue=""))

        if sort_by is not None:
            sorted_data = sorted(
                data[1:],
                key=lambda row: row[sort_by],
            )
            sorted_data.insert(0, data[0])

            return sorted_data
        return data

    @staticmethod
    def fix_empty_cells(html):
        """
        Fixes impty <td> cells and will substitude them with "--"
        which later gets recognized as 0.0 float.

        :param str html: HTML table to be fixed.
        :return: Fixed HTML.
        :rtype: str
        """
        return re.sub(r"<td([^>]*)><\/td>", "<td$1>--</td>", html, flags=re.DOTALL)


def strip_html_tags(text):
    """
    Removes HTML tags from the given string.

    :param str text: The string we want remove tags from.
    """

    return re.sub(r"<.*?>", "", text)
