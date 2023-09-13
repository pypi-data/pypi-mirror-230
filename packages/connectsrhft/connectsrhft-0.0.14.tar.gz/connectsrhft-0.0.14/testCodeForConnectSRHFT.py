from .app.connectsrhft.src.connectsrhft import ConnectSRHFT_API
import json


class Test(ConnectSRHFT_API) :

    def __init__(self):
        data = {
                "apikey":"78fb717d49a88ff046708c8f922675f3a8043373a8cfab777faf233b0531e314",
                "secretkey":'0b3786c4671b3f7cdad873b28ee457c1',
                "baseURL":"http://52.66.127.232:8006/cosmicconnect" ,
                "wsURL":"ws://52.66.127.232:8006/api/cosmicconnect"   
            }
        super().__init__(data)

        # # for _getNetPositions
        # data=self._getNetPositions()
        # print(data)

        # # for _getTradebook
        # data=self._getTradebook()
        # print(data)

        # # for _getOrderLogs
        # data=self._getOrderLogs()
        # print(data)

        # # for _getOrderErrorLogs
        # data=self._getOrderErrorLogs()
        # print(data)

        # # for _getContracts
        # data=self._getContracts()
        # print(data)

        # # # for _getContracts
        # data=self._getTokenFeed('47244684767')
        # print(data)

        # # # for _getHistoricalData
        # # {"exchange":"N","segment":"C","token":"999920000","from":"2023-08-01","to":"2023-08-07"}
        # data=self._getHistoricalData({"exchange":"N","segment":"C","token":"999920000","candle_size":"1m","from":"2023-08-01","to":"2023-08-07"})
        # print(data)


Test()