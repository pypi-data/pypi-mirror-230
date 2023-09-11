"""Initialize additional modules."""
import logging
import requests
from uun_iot import UuAppClient

from .WeatherConditions import WeatherConditions
from .HealthCheck import HealthCheck
from uun_iot.UuAppClient import UuAppClient, UuCmdSession
from uun_iot.diagnostic import DiagnosticEvent

# module list in format { module_id: [module_instance, None], ... }
def init(config: dict, uuclient: UuAppClient):

    gconfig = config["gateway"]

    if "healthCheck" not in gconfig:
        def cmd_weatherconditions(storage):
            """ Send weather to uuApp and return entries that failed to be sent. Each entry is sent separately. """
            uucmd = config["uuApp"]['uuCmdList']['weatherConditionsAdd']
            s = UuCmdSession(uuclient, uucmd, http_error_level=logging.DEBUG)
            failed = []
            len_storage = 0
            len_failed = 0
            for dto_in in storage:
                len_storage += 1
                r, (ok, exc) = s.post(dto_in)
                if not ok:
                    len_failed += 1
                    failed.append(dto_in)
            return failed

        return [
            WeatherConditions(config=gconfig, uucmd=cmd_weatherconditions),
        ]

    healthcheck = HealthCheck(gconfig)
    notify = healthcheck.notifier("weatherConditions")

    loggerwc = logging.getLogger(__name__+".WeatherCondtionsUuCmd")
    def cmd_weatherconditions_healthcheck(storage):
        """ Send weather to uuApp and return entries that failed to be sent. Each entry is sent separately. """
        uucmd = config["uuApp"]['uuCmdList']['weatherConditionsAdd']
        s = UuCmdSession(uuclient, uucmd)
        failed = []
        len_storage = 0
        len_failed = 0
        for dto_in in storage:
            len_storage += 1
            try:
                r, ok = s.post(dto_in)
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                loggerwc.info("Error in server communication: %s", e)
                len_failed += 1
                failed.append(dto_in)

        notify(DiagnosticEvent.DATA_SEND_ATTEMPTED, len_storage)
        if failed == storage:
            notify(DiagnosticEvent.DATA_SEND_FAIL)
        elif failed == []:
            notify(DiagnosticEvent.DATA_SEND_OK)
        else:
            notify(DiagnosticEvent.DATA_SEND_PARTIAL, failed=len_failed, successful=len_storage-len_failed)

        return failed

    return [
        WeatherConditions(config=gconfig, uucmd=cmd_weatherconditions_healthcheck, notify=notify),
        healthcheck
    ]

