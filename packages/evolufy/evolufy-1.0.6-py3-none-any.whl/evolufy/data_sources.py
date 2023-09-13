import glob
import os
import json
from darts import TimeSeries
import numpy as np
from evolufy.information import *
from dataclasses import dataclass
import asyncio
from dacite import from_dict

def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}
        
class DataService:
    async def request(self):
        try:
            return await self.fetch()
        except:
            return {}

@dataclass
class DataServices:
    data_services: List[DataService]
    information: type # type of AvailableInformation
    async def request(self):
        results = await asyncio.gather(*[ds.request() for ds in self.data_services])
        acc = {}
        for result in results:
            acc.update(result)
        return from_dict(data_class=self.information, data=acc)
        
# https://site.financialmodelingprep.com/login
class FinancialAPI(DataService):
    async def fetch(self):
        return {'inflation': {'inflation': []}}

class Filesystem(DataService):
    def __init__(self, *paths):
        if not paths:
            paths ["**/*.json"]
        self.paths = paths
    async def fetch(self):
        files = []
        for path in self.paths:
            files.extend(glob.glob(path))
        assets = [{"name": file.replace(".json", ""), "market_prices": self.process(read_json(file))} for file in files]
        return {'assets': assets}
    def process(self, entries):
        return TimeSeries.from_values(np.array([entry['price'] for entry in entries]))
        

class YahooFinance(DataService):
    async def fetch(self):
        return {'inflation': {'inflation': []}}

# https://databursatil.com/
class DataBursatil(DataService):
    async def fetch(self):
        return {'inflation': {'inflation': []}}