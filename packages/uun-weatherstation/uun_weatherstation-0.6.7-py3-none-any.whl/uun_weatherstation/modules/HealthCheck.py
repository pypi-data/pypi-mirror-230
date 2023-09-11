from uun_iot.modules import BaseHealthCheck
from uun_iot import on
import datetime

class HealthCheck(BaseHealthCheck):
    def __init__(self, config):
        super().__init__(config)

    @on("tick", "weatherConditions")
    def check_weatherconditions(self):
        now = datetime.datetime.now()
        mid = "weatherConditions"
        self._act_if_data_not_sent(mid, send_leeway=self._leeways[mid], now=now)

