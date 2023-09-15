import json
import logging
import requests
from sqlalchemy import create_engine
import pandas as pd


class ProprietaryTrading:
    def __init__(self, proprietary_trading_end_point: str):

        self.proprietary_trading_end_point = proprietary_trading_end_point

    def update_signal(self, symbol: str, side: str,type:str):

        url = f"{self.proprietary_trading_end_point}/signals/send"

        payload = json.dumps({
        "side": side,
        "symbol": symbol,
        "type": type
        })

        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',        
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

