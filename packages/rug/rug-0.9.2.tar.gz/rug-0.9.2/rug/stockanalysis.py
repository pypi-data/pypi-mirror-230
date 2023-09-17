import re

from .base import BaseAPI, HtmlTableParser
from .exceptions import DataException, SymbolNotFound


class StockAnalysis(BaseAPI):
    ...
    # def get_etf_holdings(self):
    #     """
    #     Fetches ETF holdings table with following columns:
    #
    #     - No.
    #     - Symbol
    #     - Name
    #     - % Weight
    #     - Shares
    #     """
    #
    #     try:
    #         html = self._get(
    #             f"https://stockanalysis.com/etf/{self.symbol.lower()}/holdings/"
    #         )
    #     except Exception as e:
    #         raise SymbolNotFound from e
    #
    #     finds = re.findall(r"<table.*?>.*?</table>", html.text, re.DOTALL)
    #
    #     # Check if the HTML contains only one table.
    #     if 0 == len(finds):
    #         raise SymbolNotFound
    #     if 1 < len(finds):
    #         raise DataException(
    #             "More that one table found in HTML - don't know what to do now"
    #         )
    #
    #     parser = HtmlTableParser(columns=5)
    #     # monkey patch - fixing the case where table header is
    #     # improperly parsed  - "%" has it's own column and the
    #     # last "shares" column is then not parsed.
    #     parser.feed(finds[0])
    #     parser.data[:6] = ("No.", "Symbol", "Name", "% Weight", "Shares")
    #
    #     return parser.get_data()

    # def get_current_price_change(self):
    #     """
    #     Fetches current market price inc. pre/post market
    #     prices/percent/value changes. Also returns current
    #     market state (pre-market, open, post-market, closed).
    #
    #     Fetched stucture has following fields:
    #
    #     - state (pre-market, open, post-market, closed)
    #     - pre_market
    #         - change
    #             - percents
    #             - value
    #         - value
    #     - current_market
    #         - change
    #             - percents
    #             - value
    #         - value
    #     - post_market
    #         - change
    #             - percents
    #             - value
    #         - value
    #
    #     Returned dict looks like:
    #
    #     .. code-block:: python
    #
    #         {
    #             "state": "open",
    #             "pre_market": {
    #                 "change": {
    #                     "percents": -1.32476,
    #                     "value": -1.42001
    #                 },
    #                 "value": 105.77
    #             },
    #             "current_market": {
    #                 "change": {
    #                     "percents": -1.6046284000000002,
    #                     "value": -1.7200012
    #                 },
    #                 "value": 105.47
    #             },
    #             "post_market": {
    #                 "change": {
    #                     "percents": 0.0,
    #                     "value": 0.0
    #                 },
    #                 "value": 0.0
    #             }
    #         }
    #
    #     :return: Current/Pre/Post market numbers (all are floats).
    #     :rtype: dict
    #     """
    #
    #     def get_state(data):
    #         """
    #         Returns one of following market states:
    #
    #         - open
    #         - closed
    #         - pre-market
    #         - post-market
    #         """
    #
    #         # Is state "extended" (meaning closed)?
    #         if not data["e"]:
    #             return data["ms"].lower()
    #         else:
    #             # Converts "After-hours" to "post-market".
    #             if "after-hours" == data["es"].lower():
    #                 return "post-market"
    #
    #             return data["es"].lower()
    #
    #     try:
    #         response = self._get(
    #             f"https://stockanalysis.com/api/quotes/s/{self.symbol.lower()}"
    #         )
    #     except Exception as e:
    #         raise SymbolNotFound from e
    #
    #     data = response.json()["data"]
    #     state = get_state(data)
    #     to_return = {
    #         "state": state,
    #     }
    #
    #     # Pre-market data.
    #     if "pre-market" == state:
    #         to_return["pre_market"] = {
    #             "change": {
    #                 "percents": data["ecp"],
    #                 "value": data["ec"],
    #             },
    #             "value": data["ep"],
    #         }
    #     else:
    #         to_return["pre_market"] = {
    #             "change": {
    #                 "percents": 0,
    #                 "value": 0,
    #             },
    #             "value": 0,
    #         }
    #
    #     # Market to_return.
    #     if "open" == data["ms"]:
    #         to_return["current_market"] = {
    #             "change": {
    #                 "percents": data["cp"],
    #                 "value": data["c"],
    #             },
    #             "value": data["p"],
    #         }
    #
    #     else:
    #         to_return["current_market"] = {
    #             "change": {
    #                 "percents": 0,
    #                 "value": 0,
    #             },
    #             "value": 0,
    #         }
    #
    #     # Post-market data.
    #     if "post-market" == state:
    #         to_return["post_market"] = {
    #             "change": {
    #                 "percents": data["ecp"],
    #                 "value": data["ec"],
    #             },
    #             "value": data["ep"],
    #         }
    #
    #     else:
    #         to_return["post_market"] = {
    #             "change": {
    #                 "percents": 0,
    #                 "value": 0,
    #             },
    #             "value": 0,
    #         }
    #
    #     return to_return
