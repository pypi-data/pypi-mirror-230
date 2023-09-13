import pytest

from evolufy.agents import *
from dataclasses import dataclass
from injector import Module, provider, Injector, inject, singleton
from typing import List
from darts.utils.timeseries_generation import (
    gaussian_timeseries,
    linear_timeseries,
      sine_timeseries,
)

import torch

torch.manual_seed(1)
np.random.seed(1)


__author__ = "sanchezcarlosjr"
__copyright__ = "sanchezcarlosjr"
__license__ = "MIT"

class MockFilesystem(DataService):
    def __init__(self):
        np.random.seed(0)
        self.fs = {
            'assets': 
            [
                {
                  'market_prices': TimeSeries.from_values(np.random.randn(1000) * 0.02)
                },
                {
                  'market_prices': TimeSeries.from_values(np.random.randn(1000) * 0.02)
                }
            ], 
            'inflation': {'inflation': []}
       }
    async def request(self):
        return self.fs


fs = MockFilesystem()
def configure_for_testing(binder):
    binder.bind(InvestmentStrategy,to=ModernPortfolioTheory)
    binder.bind(GBMPlus,to=GBMPlus)
    binder.multibind(List[DataService], to=[fs])

async def test_should_check_fake_agent_request():
    injector = Injector([configure_for_testing])
    agent = injector.get(Agent)
    response = await agent.request()
    assert await agent.request() == MarketValuation(
        assets=[Asset(market_prices=fs.fs['assets'][0]['market_prices'],weight=None),Asset(market_prices=fs.fs['assets'][1]['market_prices'],weight=None)], 
        inflation=Inflation(inflation=[]),
        primal_objective=None
    )

async def test_should_check_fake_agent_actuation():
    injector = Injector([configure_for_testing])
    agent = injector.get(Agent)
    solution = await agent.act()
    assert solution.assets[0].weight == -0.826608380109433
    assert solution.assets[1].weight == 1.8266083801094304
    assert solution.primal_objective == 0.48429719758604844