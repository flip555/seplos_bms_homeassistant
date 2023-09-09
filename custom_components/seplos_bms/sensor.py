class SeplosBMSSensor(Entity):
    def __init__(self, name, data_func, attr, unit=None):
        self._name = name
        self._data_func = data_func
        self._attr = attr
        self._unit = unit
        self._latest_data = {}

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    async def async_update_data(self):
        try:
            result = await self._data_func()
            if isinstance(result, str):
                self._latest_data = json.loads(result)
            else:
                self._latest_data = result
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self._latest_data
        for attr_part in self._attr.split('.'):
            if isinstance(data, dict) and attr_part in data:
                data = data[attr_part]
            else:
                return None
        return data

async def async_setup_entry(hass, entry, async_add_entities):
    usb_port = entry.data["usb_port"]
    async def get_data():
        return await hass.async_add_executor_job(fetch_data_from_bms, usb_port)

    sensors = [
        SeplosBMSSensor("Seplos BMS - Number of Cells", get_data, "NoCells"),
        SeplosBMSSensor("Seplos BMS - Highest Cell Value", get_data, "HighestCell", "V"),
        SeplosBMSSensor("Seplos BMS - Lowest Cell Value", get_data, "LowestCell", "V"),
        SeplosBMSSensor("Seplos BMS - Cell Difference", get_data, "CellDifference", "V"),
        SeplosBMSSensor("Seplos BMS - Environment Temperature", get_data, "EnvTemp", "°C"),
        SeplosBMSSensor("Seplos BMS - Power Temperature", get_data, "PowerTemp", "°C"),
        SeplosBMSSensor("Seplos BMS - Current", get_data, "Current", "A"),
        SeplosBMSSensor("Seplos BMS - Voltage", get_data, "Voltage", "V"),
        SeplosBMSSensor("Seplos BMS - Capacity Remaining", get_data, "CapRemain", "Ah"),
        SeplosBMSSensor("Seplos BMS - Capacity in Wh Remaining", get_data, "CapwHRemain", "Wh"),
        SeplosBMSSensor("Seplos BMS - Total Capacity", get_data, "Cap", "Ah"),
        SeplosBMSSensor("Seplos BMS - State of Charge (SOC)", get_data, "SOC", "%"),
        SeplosBMSSensor("Seplos BMS - Total Capacity", get_data, "Capacity", "Ah"),
        SeplosBMSSensor("Seplos BMS - Number of Cycles", get_data, "Cycles"),
        SeplosBMSSensor("Seplos BMS - State of Health (SOH)", get_data, "SOH", "%"),
        SeplosBMSSensor("Seplos BMS - Port Voltage", get_data, "PortV", "V")
        SeplosBMSSensor("Seplos BMS - Temperature 1", get_data, "Temp1", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 2", get_data, "Temp2", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 3", get_data, "Temp3", "°C"),
        SeplosBMSSensor("Seplos BMS - Temperature 4", get_data, "Temp4", "°C"),
    ]

    # Dynamically add cell sensors
    for i in range(1, 17):  # 16 cells
        sensors.append(SeplosBMSSensor(f"Seplos BMS - Cell {i} Voltage", get_data, f"C{i}", "V"))

    async_add_entities(sensors, True)
