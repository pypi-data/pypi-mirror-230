from abc import ABC
from typing import TypeVar

from wwtp.api.settings import IScenarioSettings

SS = TypeVar('SS', bound=IScenarioSettings)


class ProcessUnit(ABC):

    def __init__(
            self,
            scenario_settings: SS,
    ):
        self.scenario_settings = scenario_settings
