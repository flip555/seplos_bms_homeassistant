import logging
import json
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from .seplos_helper import SeplosHelper
from .const import DOMAIN
from .seplos_helper import BMSDataCoordinator

_LOGGER = logging.getLogger(__name__)


class SeplosBMSSensor(Entity):
    def __init__(self, name, data_coordinator, attr, unit=None):
        self._name = name
        self._data_coordinator = data_coordinator
        self._attr = attr
        self._unit = unit
        self._latest_data = {}

    async def async_update(self):
        await self._data_coordinator.fetch_data(self.hass)
        self._latest_data = self._data_coordinator.data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self._latest_data
        if isinstance(data, str):
            data = json.loads(data)
        _LOGGER.debug("Dat: %s", data)
        for attr_part in self._attr.split('.'):
            if isinstance(data, dict) and attr_part in data:
                data = data[attr_part]
            else:
                return None
        return data

        

async def async_setup_entry(hass, entry, async_add_entities):
    usb_port = entry.data["usb_port"]
    data_coordinator = BMSDataCoordinator(usb_port)

    sensors = [
        SeplosBMSSensor("Seplos BMS - Number of Cells", data_coordinator, "NoCells"),
        SeplosBMSSensor("Seplos BMS - Highest Cell Value", data_coordinator, "HighestCell", "V"),
        SeplosBMSSensor("Seplos BMS - Lowest Cell Value", data_coordinator, "LowestCell", "V"),
        SeplosBMSSensor("Seplos BMS - Cell Difference", data_coordinator, "CellDifference", "V"),
        SeplosBMSSensor("Seplos BMS - Environment Temperature", data_coordinator, "EnvTemp", "°C"),
        SeplosBMSSensor("Seplos BMS - Power Temperature", data_coordinator, "PowerTemp", "°C"),
        SeplosBMSSensor("Seplos BMS - Current", data_coordinator, "Current", "A"),
        SeplosBMSSensor("Seplos BMS - Voltage", data_coordinator, "Voltage", "V"),
        SeplosBMSSensor("Seplos BMS - Capacity Remaining", data_coordinator, "CapRemain", "Ah"),
        SeplosBMSSensor("Seplos BMS - Capacity in Wh Remaining", data_coordinator, "CapwHRemain", "Wh"),
        SeplosBMSSensor("Seplos BMS - Total Capacity", data_coordinator, "Cap", "Ah"),
        SeplosBMSSensor("Seplos BMS - State of Charge (SOC)", data_coordinator, "SOC", "%"),
        SeplosBMSSensor("Seplos BMS - Total Capacity", data_coordinator, "Capacity", "Ah"),
        SeplosBMSSensor("Seplos BMS - Number of Cycles", data_coordinator, "Cycles"),
        SeplosBMSSensor("Seplos BMS - State of Health (SOH)", data_coordinator, "SOH", "%"),
        SeplosBMSSensor("Seplos BMS - Port Voltage", data_coordinator, "PortV", "V"),
        SeplosBMSSensor("Seplos BMS - Temperature 1", data_coordinator, "Temp1", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 2", data_coordinator, "Temp2", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 3", data_coordinator, "Temp3", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 4", data_coordinator, "Temp4", "°C"),    ]

    # Dynamically add cell sensors
    for i in range(1, 17):  # 16 cells
        sensors.append(SeplosBMSSensor(f"Seplos BMS - Cell {i} Voltage", data_coordinator, f"C{i}", "V"))

    async_add_entities(sensors, True)
