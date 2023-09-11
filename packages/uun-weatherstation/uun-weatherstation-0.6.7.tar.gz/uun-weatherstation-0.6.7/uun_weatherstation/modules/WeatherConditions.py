"""
modules.WeatherConditions

Store downloaded weaeher conditions from Davis Pro 2 and then send them to uuApp.
"""
import requests
from datetime import datetime
import json

from uun_iot.modules.Module import Module
from uun_iot.utils import get_iso_timestamp
from uun_iot import on
from uun_iot.diagnostic import DiagnosticEvent
from uun_weatherstation.utils import fahrenheit_to_celsius, mph_to_kph, inch_to_cm

import logging
logger = logging.getLogger(__name__)

class WeatherConditions(Module):
    def __init__(self, config, uucmd, notify=None):
        super().__init__(uucmd=uucmd, config=config)

        def dnotify(*args, **kwargs):
            if notify is not None:
                notify(*args, **kwargs)
        self._dnotify = dnotify
        self._dnotify_set = notify is not None

    def _get_data(self):
        url = '%s/%s' % (self._c('ipAddress'), self._c('endPointList')['currentConditions'])
        try:
            response = requests.get(url, timeout=self._c("timeout"))
        except requests.exceptions.Timeout as e: 
            logger.warning("Davis Pro 2 is unreachable (%s s timeout)", self._c("timeout"))
            return False

        except requests.exceptions.ConnectionError as e:
            logger.warning("Davis Pro 2 is unreachable (no route to host `%s`)", self._c("ipAddress"))
            return False

        raw_data = response.text
        try: 
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.warning("invalid JSON payload from Davis Pro 2")
            logger.debug("invalid response: %s", raw_data)
            return False

        logger.info("retrieved [%s] weather conditions from Davis Pro 2", len(data))
        return data['data']

    def _process_data(self, data):
        out = []
        for conditions in data['conditions']:
            if (conditions['data_structure_type'] == 1):
                dto_in = self.get_dto_in_for_type_1(data['did'], data['ts'], conditions)
            elif (conditions['data_structure_type'] == 2):
                dto_in = self.get_dto_in_for_type_2(data['did'], data['ts'], conditions)
            elif (conditions['data_structure_type'] == 3):
                dto_in = self.get_dto_in_for_type_3(data['did'], data['ts'], conditions)
            elif (conditions['data_structure_type'] == 4):
                dto_in = self.get_dto_in_for_type_4(data['did'], data['ts'], conditions)
            
            out.append(dto_in)

        return out

        # do not send right after acquiring - this would generate a lot of internet overhead
        # self.send_current_conditions()

    @on("tick", "get")
    def save_current_conditions(self):
        self._dnotify(DiagnosticEvent.TIMER_CALL, "get")

        data = self._get_data()
        if data:
            self._dnotify(DiagnosticEvent.DATA_RECEIVED, length=len(data))
        else:
            # logger.warning("Exception encountered in `save_current_conditions` when getting data.")
            return

        pdata = self._process_data(data)
        self._storage.merge(pdata)

    @on("tick", "send")
    def send_weather_conditions(self):
        if self._dnotify_set:
            self._dnotify(DiagnosticEvent.TIMER_CALL, "send")
            l = len(self._storage)
            if l > 0:
                self._dnotify(DiagnosticEvent.DATA_SEND_IMMINENT, length=l)

        self._send_storage()

    def get_dto_in_for_type_1(self, did, timestamp, data):
        dto_in = {
            "did": did,
            "timestamp": get_iso_timestamp(datetime.utcfromtimestamp(timestamp)),
            "lsid": data['lsid'],
            "type": data['data_structure_type'],
            "txid": data['txid'],
            "temp": fahrenheit_to_celsius(data['temp']),
            "hum": data['hum'],
            "dewPoint": fahrenheit_to_celsius(data['dew_point']),
            "wetBulb": fahrenheit_to_celsius(data['wet_bulb']),
            "heatIndex": fahrenheit_to_celsius(data['heat_index']),
            "windChill": fahrenheit_to_celsius(data['wind_chill']),
            "thwIndex": fahrenheit_to_celsius(data['thw_index']),
            "thswIndex": fahrenheit_to_celsius(data['thsw_index']),
            "windSpeedLast": mph_to_kph(data['wind_speed_last']),
            "windDirLast": data['wind_dir_last'],
            "windSpeedAvgLast1Min": mph_to_kph(data['wind_speed_avg_last_1_min']),
            "windDirScalarAvgLast1Min": data['wind_dir_scalar_avg_last_1_min'],
            "windSpeedAvgLast2Min": mph_to_kph(data['wind_speed_avg_last_2_min']),
            "windDirScalarAvgLast2Min": data['wind_dir_scalar_avg_last_2_min'],
            "windSpeedHiLast2Min": mph_to_kph(data['wind_speed_hi_last_2_min']),
            "windDirAtHiSpeedLast2Min": data['wind_dir_at_hi_speed_last_2_min'],
            "windSpeedAvgLast10Min": mph_to_kph(data['wind_speed_avg_last_10_min']),
            "windDirScalarAvgLast10Min": data['wind_dir_scalar_avg_last_10_min'],
            "windSpeedHiLast10Min": mph_to_kph(data['wind_speed_hi_last_10_min']),
            "windDirAtHiSpeedLast10Min": data['wind_dir_at_hi_speed_last_10_min'],
            "rainSize": data['rain_size'],
            "rainRateLast": data['rain_rate_last'],
            "rainRateHi": data['rain_rate_hi'],
            "rainfallLast15Min": data['rainfall_last_15_min'],
            "rainRateHiLast15Min": data['rain_rate_hi_last_15_min'],
            "rainfallLast60Min": data['rainfall_last_60_min'],
            "rainfallLast24Hr": data['rainfall_last_24_hr'],
            "rainStorm": data['rain_storm'],
            "solarRad": data['solar_rad'],
            "uvIndex": data['uv_index'],
            "rxState": data['rx_state'],
            "transBatteryFlag": data['trans_battery_flag'],
            "rainfallDaily": data['rainfall_daily'],
            "rainfallMonthly": data['rainfall_monthly'],
            "rainfallYear": data['rainfall_year'],
            "rainStormLast": data['rain_storm_last']
        }
        if (data['rain_storm_start_at'] is not None):
            dto_in["rainStormStartAt"] = get_iso_timestamp(datetime.utcfromtimestamp(data['rain_storm_start_at']))
        if (data['rain_storm_last_start_at'] is not None):
            dto_in["rainStormLastStartAt"] = get_iso_timestamp(datetime.utcfromtimestamp(data['rain_storm_last_start_at']))
        if (data['rain_storm_last_end_at'] is not None):
            dto_in["rainStormLastEndAt"] = get_iso_timestamp(datetime.utcfromtimestamp(data['rain_storm_last_end_at']))
        return dto_in

    def get_dto_in_for_type_2(self, did, timestamp, data):
        dto_in = {
            "did": did,
            "timestamp": get_iso_timestamp(datetime.utcfromtimestamp(timestamp)),
            "lsid": data['lsid'],
            "type": data['data_structure_type'],
            "txid": data['txid'],
            "temp1": fahrenheit_to_celsius(data['temp_1']),
            "temp2": fahrenheit_to_celsius(data['temp_2']),
            "temp3": fahrenheit_to_celsius(data['temp_3']),
            "temp4": fahrenheit_to_celsius(data['temp_4']),
            "moistSoil1": data['moist_soil_1'],
            "moistSoil2": data['moist_soil_2'],
            "moistSoil3": data['moist_soil_3'],
            "moistSoil4": data['moist_soil_4'],
            "wetLeaf1": data['wet_leaf_1'],
            "wetLeaf2": data['wet_leaf_2'],
            "rxState": data['rx_state'],
            "transBatteryFlag": data['trans_battery_flag']
        }
        return dto_in

    def get_dto_in_for_type_3(self, did, timestamp, data):
        dto_in = {
            "did": did,
            "timestamp": get_iso_timestamp(datetime.utcfromtimestamp(timestamp)),
            "lsid": data['lsid'],
            "type": data['data_structure_type'],
            "barSeaLevel": inch_to_cm(data['bar_sea_level']),
            "barTrend": inch_to_cm(data['bar_trend']),
            "barAbsolute": inch_to_cm(data['bar_absolute'])
        }
        return dto_in
        
    def get_dto_in_for_type_4(self, did, timestamp, data):
        dto_in = {
            "did": did,
            "timestamp": get_iso_timestamp(datetime.utcfromtimestamp(timestamp)),
            "lsid": data['lsid'],
            "type": data['data_structure_type'],
            "tempIn": fahrenheit_to_celsius(data['temp_in']),
            "humIn": data['hum_in'],
            "dewPointIn": fahrenheit_to_celsius(data['dew_point_in']),
            "heatIndexIn": fahrenheit_to_celsius(data['heat_index_in'])
        }
        return dto_in
        
