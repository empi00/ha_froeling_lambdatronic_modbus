"""Additional calculated entities for the Fröling Lambdatronic Modbus integration.

The additions are applied to the upstream ENTITY_DEFINITIONS at package import
without modifying the large upstream entity_definitions.py file.
"""

from __future__ import annotations

from typing import Any


def apply_custom_entity_definitions(
    entity_definitions: dict[str, dict[str, dict[str, Any]]],
) -> None:
    """Add/replace the custom solar and pellet sensor definitions."""

    austragung = entity_definitions["austragung"]
    austragung["resetierbarer_kg_zaehler_gesamt"] = {
        "name": "Resetierbarer kg Zähler Gesamt",
        "unit": "kg",
        "device_class": "weight",
        "state_class": "total_increasing",
        "type": "sensor",
        "calculation": {
            "operation": "weighted_sum",
            "sources": {
                "resetierbarer_t_zaehler": 1000,
                "resetierbarer_kg_zaehler": 1,
            },
        },
    }

    solarthermie = entity_definitions["solarthermie"]

    # Keep the original Modbus value in kW and explicitly mark it as an
    # instantaneous power measurement.
    solarthermie["aktuelle_leistung_des_solar_wmz"]["state_class"] = "measurement"

    # Current power converted from kW to W.
    solarthermie["aktuelle_leistung_des_solar_wmz_w"] = {
        "name": "Aktuelle Leistung des Solar WMZ W",
        "unit": "W",
        "decimals": 0,
        "device_class": "power",
        "state_class": "measurement",
        "type": "sensor",
        "calculation": {
            "operation": "weighted_sum",
            "sources": {
                "aktuelle_leistung_des_solar_wmz": 1000,
            },
        },
    }

    # 5-minute rolling average in kW.
    solarthermie["aktuelle_leistung_des_solar_wmz_average_5minutes"] = {
        "name": "Aktuelle Leistung des Solar WMZ Average 5minutes",
        "unit": "kW",
        "decimals": 2,
        "device_class": "power",
        "state_class": "measurement",
        "type": "sensor",
        "calculation": {
            "operation": "rolling_average",
            "source": "aktuelle_leistung_des_solar_wmz",
            "window_seconds": 300,
        },
    }

    # 5-minute rolling average converted to W.
    solarthermie["aktuelle_leistung_des_solar_wmz_average_5minutes_w"] = {
        "name": "Aktuelle Leistung des Solar WMZ Average 5minutes W",
        "unit": "W",
        "decimals": 0,
        "device_class": "power",
        "state_class": "measurement",
        "type": "sensor",
        "calculation": {
            "operation": "rolling_average",
            "source": "aktuelle_leistung_des_solar_wmz",
            "window_seconds": 300,
            "multiplier": 1000,
        },
    }

    # 10-minute rolling average in kW.
    solarthermie["aktuelle_leistung_des_solar_wmz_average_10minutes"] = {
        "name": "Aktuelle Leistung des Solar WMZ Average 10minutes",
        "unit": "kW",
        "decimals": 2,
        "device_class": "power",
        "state_class": "measurement",
        "type": "sensor",
        "calculation": {
            "operation": "rolling_average",
            "source": "aktuelle_leistung_des_solar_wmz",
            "window_seconds": 600,
        },
    }

    # 10-minute rolling average converted to W.
    solarthermie["aktuelle_leistung_des_solar_wmz_average_10minutes_w"] = {
        "name": "Aktuelle Leistung des Solar WMZ Average 10minutes W",
        "unit": "W",
        "decimals": 0,
        "device_class": "power",
        "state_class": "measurement",
        "type": "sensor",
        "calculation": {
            "operation": "rolling_average",
            "source": "aktuelle_leistung_des_solar_wmz",
            "window_seconds": 600,
            "multiplier": 1000,
        },
    }

    # The Fröling solar total is split across two registers:
    # 32621 = whole MWh, 32622 = remaining kWh.
    solarthermie["solarthermie_mwh"] = {
        "name": "Solarthermie MWh",
        "register": 32621,
        "unit": "MWh",
        "scaling": 1,
        "device_class": "energy",
        "type": "sensor",
    }

    solarthermie["solarthermie_kwh"] = {
        "name": "Solarthermie kWh",
        "register": 32622,
        "unit": "kWh",
        "scaling": 1,
        "device_class": "energy",
        "type": "sensor",
    }

    # Replace the upstream sensor that exposed only register 32622.
    solarthermie["solarthermie_gesamtertrag"] = {
        "name": "Solarthermie Gesamtertrag",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "type": "sensor",
        "calculation": {
            "operation": "weighted_sum",
            "sources": {
                "solarthermie_mwh": 1000,
                "solarthermie_kwh": 1,
            },
        },
    }
