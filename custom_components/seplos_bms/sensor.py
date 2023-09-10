import logging
import json
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from .seplos_helper import SeplosHelper
from .const import DOMAIN
from .seplos_helper import BMSDataCoordinator
from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=5)

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
        SeplosBMSSensor("SeplosBMS - Number of Cells", data_coordinator, "NoCells"),
        SeplosBMSSensor("SeplosBMS - Highest Cell Value", data_coordinator, "HighestCell", "mV"),
        SeplosBMSSensor("SeplosBMS - Lowest Cell Value", data_coordinator, "LowestCell", "mV"),
        SeplosBMSSensor("SeplosBMS - Cell Difference", data_coordinator, "CellDifference", "mV"),
        SeplosBMSSensor("SeplosBMS - Environment Temperature", data_coordinator, "EnvTemp", "°C"),
        SeplosBMSSensor("SeplosBMS - Power Temperature", data_coordinator, "PowerTemp", "°C"),
        SeplosBMSSensor("SeplosBMS - Current", data_coordinator, "Current", "A"),
        SeplosBMSSensor("SeplosBMS - Voltage", data_coordinator, "Voltage", "V"),
        SeplosBMSSensor("SeplosBMS - Capacity Remaining", data_coordinator, "CapRemain", "Ah"),
        SeplosBMSSensor("SeplosBMS - Capacity in Wh Remaining", data_coordinator, "CapwHRemain", "Wh"),
        SeplosBMSSensor("SeplosBMS - Total Capacity", data_coordinator, "Cap", "Ah"),
        SeplosBMSSensor("SeplosBMS - State of Charge (SOC)", data_coordinator, "SOC", "%"),
        SeplosBMSSensor("SeplosBMS - Total Capacity", data_coordinator, "Capacity", "Ah"),
        SeplosBMSSensor("SeplosBMS - Number of Cycles", data_coordinator, "Cycles"),
        SeplosBMSSensor("SeplosBMS - State of Health (SOH)", data_coordinator, "SOH", "%"),
        SeplosBMSSensor("SeplosBMS - Port Voltage", data_coordinator, "PortV", "V"),
        SeplosBMSSensor("SeplosBMS - Temperature 1", data_coordinator, "Temp1", "°C"),
        SeplosBMSSensor("SeplosBMS - Temperature 2", data_coordinator, "Temp2", "°C"),
        SeplosBMSSensor("SeplosBMS - Temperature 3", data_coordinator, "Temp3", "°C"),
        SeplosBMSSensor("SeplosBMS - Temperature 4", data_coordinator, "Temp4", "°C"),    ]

    # Dynamically add cell sensors
    for i in range(1, 17):  # 16 cells
        sensors.append(SeplosBMSSensor(f"SeplosBMS - Cell {i} Voltage", data_coordinator, f"C{i}", "mV"))

    async_add_entities(sensors, True)
