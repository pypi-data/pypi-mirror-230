from dataclasses import dataclass
import numpy as np
from typing import List,Optional
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import MinMaxScaler
from darts.models import (
    RNNModel,
    TCNModel,
    TransformerModel,
    NBEATSModel,
    BlockRNNModel,
    VARIMA,
)

def calculate_returns_from_prices(prices):
    prices[prices == 0] = 1e-9
    returns = np.log10(prices[1:] / prices[:-1])
    return returns

@dataclass
class Asset:
    market_prices: TimeSeries
    weight: Optional[float]
    name: Optional[str]    
    def explore_returns(self):
        market_prices = self.market_prices.all_values().squeeze()
        returns = calculate_returns_from_prices(market_prices)
        return TimeSeries.from_values(returns)
    def plot(self, *keys):
         car = getattr(self, keys[0])
         car.plot(self.name)
    def preprocess(self):
        scaler = Scaler()
        series_scaled = scaler.fit_transform(self.market_prices)
        train, validation = series_scaled[:-50], series_scaled[-50:]
        return train,validation

@dataclass
class Inflation:
    inflation: List[float]

@dataclass
class AvailableInformation:
    assets:  List[Asset]
    inflation: Optional[Inflation]
    risk_level: float = 1
    def plot(self, *keys):
        car = getattr(self, keys[0])
        cdr = keys[1:]
        if not hasattr(car,'__iter__'):
            return car.plot()
        for entry in car:
             entry.plot(*cdr)
    def valuate(self):
        pass

@dataclass
class NaiveMarketValuation(AvailableInformation):
    def valuate(self):
        return np.array([asset.explore_returns().all_values().squeeze() for asset in self.assets])

@dataclass
class MarketForecast(AvailableInformation):
    model = NBEATSModel(input_chunk_length=24, output_chunk_length=12, n_epochs=40)
    n: int = 10
    verbose: bool = False
    def valuate(self):
        predictions = []
        for asset in self.assets:
            train, validation = asset.preprocess()
            self.model.fit(train, verbose=self.verbose)
            market_price_forecast = self.model.predict(n=self.n, verbose=self.verbose).all_values().squeeze()
            predictions.append(calculate_returns_from_prices(market_price_forecast))
        return np.array(predictions)


@dataclass
class DiscountedCashFlowValuation(AvailableInformation):
    def valuate(self):
        pass

@dataclass
class PiotroskiValuation(AvailableInformation):
    def valuate(self):
        pass

