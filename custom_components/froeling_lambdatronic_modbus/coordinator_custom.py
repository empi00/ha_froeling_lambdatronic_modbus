"""Custom coordinator extensions for calculated Fröling sensors."""

from __future__ import annotations

from collections import deque
from time import monotonic
from typing import Any

from .coordinator import FroelingDataUpdateCoordinator as BaseFroelingDataUpdateCoordinator
from .entity_definitions import ENTITY_DEFINITIONS


class FroelingDataUpdateCoordinator(BaseFroelingDataUpdateCoordinator):
    """Coordinator with support for calculated and rolling-average sensors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._rolling_histories: dict[str, deque[tuple[float, float]]] = {}
        super().__init__(*args, **kwargs)

    def _get_active_entity_definitions(self) -> dict[str, Any]:
        """Return enabled definitions plus dependencies of calculated sensors."""
        active = super()._get_active_entity_definitions()

        all_definitions = {
            entity_id: definition
            for category in ENTITY_DEFINITIONS.values()
            for entity_id, definition in category.items()
        }

        pending = list(active.values())
        while pending:
            definition = pending.pop()
            for source_id in self._get_calculation_source_ids(definition):
                if source_id in active:
                    continue

                source_definition = all_definitions.get(source_id)
                if source_definition is None:
                    continue

                active[source_id] = source_definition
                pending.append(source_definition)

        return active

    @staticmethod
    def _get_calculation_source_ids(definition: dict[str, Any]) -> list[str]:
        calculation = definition.get("calculation")
        if not calculation:
            return []

        operation = calculation.get("operation")
        if operation == "weighted_sum":
            return list(calculation.get("sources", {}))
        if operation == "rolling_average":
            source_id = calculation.get("source")
            return [source_id] if source_id else []
        return []

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch Modbus data with the upstream coordinator, then derive sensors."""
        data = await super()._async_update_data()
        self._apply_calculated_sensors(data)
        return data

    def _apply_calculated_sensors(self, data: dict[str, Any]) -> None:
        """Calculate virtual sensors from already processed source values."""
        now = monotonic()

        for entity_id, definition in self._entity_definitions.items():
            calculation = definition.get("calculation")
            if not calculation:
                continue

            operation = calculation.get("operation")
            calculated_value: float | None = None

            if operation == "weighted_sum":
                sources = calculation.get("sources", {})
                if sources:
                    total = 0.0
                    valid = True
                    for source_id, factor in sources.items():
                        source_value = data.get(source_id)
                        if not isinstance(source_value, (int, float)):
                            valid = False
                            break
                        total += float(source_value) * float(factor)
                    if valid:
                        calculated_value = total

            elif operation == "rolling_average":
                source_id = calculation.get("source")
                window_seconds = float(calculation.get("window_seconds", 600))
                multiplier = float(calculation.get("multiplier", 1))

                if source_id and window_seconds > 0:
                    history = self._rolling_histories.setdefault(entity_id, deque())
                    source_value = data.get(source_id)

                    # A real 0 kW sample is deliberately included in the average.
                    # Failed reads (None) are not added to the history.
                    if isinstance(source_value, (int, float)):
                        history.append((now, float(source_value)))

                    cutoff = now - window_seconds
                    while history and history[0][0] < cutoff:
                        history.popleft()

                    if history:
                        calculated_value = (
                            sum(value for _, value in history) / len(history)
                        ) * multiplier

            if calculated_value is None:
                data[entity_id] = None
                continue

            decimal_places = definition.get("decimals", 0)
            if decimal_places == 0:
                data[entity_id] = int(round(calculated_value))
            else:
                data[entity_id] = round(calculated_value, decimal_places)
