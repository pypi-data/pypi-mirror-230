import re
from datetime import date, datetime

from .base import BaseAPI, HtmlTableParser
from .exceptions import SymbolNotFound


class FinViz(BaseAPI):
    """
    FinViz.com
    """

    def get_price_ratings(self):
        """
        Returns price ratings a.k.a price targets
        by analysts.

        Returned rows are:

        - date
        - status
        - analyst
        - rating
        - target price

        :return: Rows as a list of tuples where each tuple has 5 items.
        :rtype: list
        """

        try:
            html = self._get(
                f"https://finviz.com/quote.ashx?t={self.symbol.upper()}&ty=c&ta=1&p=d",
                headers={"User-Agent": self.user_agent},
            )
        except Exception as e:
            raise SymbolNotFound from e

        finds = re.findall(
            r"<table[^>]*fullview-ratings-outer[^>]*>(.+?)</table>",
            html.text,
            re.DOTALL,
        )
        rows = []

        if finds:
            html = HtmlTableParser.fix_empty_cells(finds[0])
            parser = HtmlTableParser(columns=5)
            parser.feed(html)
            rows = parser.get_data()[1:]

        return rows

    def get_insider_trading(self):
        """
        Fetches insiders transactions (if available) as a
        list with following fields:

        - person
        - relationship
        - date
        - transaction
        - price
        - amount

        :return: Inriders transaction in reversed chronological order.
        :rtype: list
        """

        def parse_date(to_parse, last_date):
            year = last_date.year

            while True:
                possible_date = datetime.strptime(
                    f"{to_parse} {year}", "%b %d %Y"
                ).date()

                if possible_date > date.today():
                    year -= 1
                    continue

                return possible_date

        try:
            html = self._get(
                f"https://finviz.com/quote.ashx?t={self.symbol.upper()}&ty=c&ta=1&p=d",
                headers={"User-Agent": self.user_agent},
            )
        except Exception as e:
            raise SymbolNotFound from e

        rows = re.findall(r"<tr[^>]*insider-row*[^>]*>.+?<\/tr>", html.text, re.DOTALL)
        data = []

        if len(rows):
            parser = HtmlTableParser(columns=9)
            rows = "\n".join(rows)
            parser.feed(f"<table>{rows}</table>")
            last_date = date.today()

            for row in parser.get_data():
                parsed_date = parse_date(row[2], last_date)
                last_date = parsed_date
                data.append(
                    {
                        "person": row[0],
                        "relationship": row[1],
                        "date": parsed_date,
                        "transaction": row[3],
                        "price": float(row[4]),
                        "amount": int(row[5]),
                    }
                )

        return data
