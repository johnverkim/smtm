"""거래 데이터를 클라우드에서 가져오고, 저장해서 제공
"""
import requests
from .log_manager import LogManager
from .date_converter import DateConverter


class DataRepository:
    def __init__(self):
        self.logger = LogManager.get_logger(__class__.__name__)

    def get_data(self, start, end, period=60, market="BTC", trader="Upbit"):
        """거래 데이터를 제공"""

    def _query(self, start, end, period, market, trader):
        """데이터베이스에서 데이터 조회"""

    def _update(self, data):
        """데이터베이스 데이터 업데이트"""

    def _update_from_server(self, start, end, period, market, trader):
        """거래소 서버에서 데이터 조회해서 데이터베이스 업데이트"""

    def _fetch_from_upbit(self, start, end, period, market):
        """업비트 서버에서 n번 데이터 조회해서 최종 결과를 반환
        1회 조회시 갯수 제한이 있기 때문에 여러번 조회해서 합쳐야함
        업비트는 현재 공식적으로 최대 200개까지 조회 가능
        """

    def _fetch_from_upbit_up_to_200(self, start, end, period, market):
        """업비트 서버에서 최대 200개까지 데이터 조회해서 반환"""

        if period not in [60, 180, 300, 900, 600, 1800, 3600, 14400]:
            raise UserWarning("Fail get data from sever: invalid period")

        minutes = int(period / 60)
        URL = f"https://api.upbit.com/v1/candles/minutes/{minutes}"
        date_info = DateConverter.to_end_min(start=start, end=end)
        to = DateConverter.from_kst_to_utc_str(date_info[0]) + "Z"
        query_string = {"market": market, "to": to, "count": date_info[1]}

        try:
            response = requests.get(URL, params=query_string)
            response.raise_for_status()
            data = response.json()
            data.reverse()
            final_data = []
            for item in data:
                final_data.append(
                    {
                        "market": item["market"],
                        "date_time": item["candle_date_time_kst"],
                        "opening_price": float(item["opening_price"]),
                        "high_price": float(item["high_price"]),
                        "low_price": float(item["low_price"]),
                        "closing_price": float(item["trade_price"]),
                        "acc_price": float(item["candle_acc_trade_price"]),
                        "acc_volume": float(item["candle_acc_trade_volume"]),
                    }
                )
            return final_data

        except ValueError as error:
            self.logger.error("Invalid data from server")
            raise UserWarning("Fail get data from sever") from error
        except requests.exceptions.HTTPError as error:
            self.logger.error(error)
            raise UserWarning("Fail get data from sever") from error
        except requests.exceptions.RequestException as error:
            self.logger.error(error)
            raise UserWarning("Fail get data from sever") from error

    def _fetch_from_bithumb(self, start, end, period, market):
        """빗썸 서버에서 데이터 조회"""