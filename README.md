# Froeling Lambdatronic Modbus

Home Assistant integration for Fröling Lambdatronic heating systems via Modbus. Currently supports Modbus TCP via a Serial-to-Ethernet bridge.

This fork adds corrected/combined solar-energy counters, a combined resettable pellet counter, Watt variants for the solar heat-meter power and rolling 5-minute / 10-minute average power sensors.

## 🚀 Features

With this integration, you can:

- Read real-time sensor data from your Fröling system (temperatures, states, pump speeds, consumption, etc.).
- Monitor boiler operation (e.g., Kesselzustand, Anlagenzustand).
- Configure parameters via writable Number entities, using input boxes.
- Control modes via Select entities (e.g., HK01/HK02 Betriebsart with Aus/Automatik/Extraheizen/Absenken/Dauerabsenken/Partybetrieb).
- Inspect the boiler error buffers.
- Read the Fröling solar heat-meter power in both **kW** and **W**.
- Use rolling **5-minute** and **10-minute** average solar power sensors to smooth short 0/peak jumps.
- Combine the Fröling solar MWh + kWh registers into one total-energy sensor.
- Combine the resettable pellet t + kg counters into one total kg sensor.

## ☀️ Fork-specific solar and pellet sensors

The entity IDs below assume the default device name `Froeling`. Home Assistant stores entity IDs in lowercase.

### Solar heat-meter power

| Entity | Unit | Description |
|---|---:|---|
| `sensor.froeling_aktuelle_leistung_des_solar_wmz` | kW | Original instantaneous value from register 32611 |
| `sensor.froeling_aktuelle_leistung_des_solar_wmz_w` | W | Instantaneous value converted to W |
| `sensor.froeling_aktuelle_leistung_des_solar_wmz_average_5minutes` | kW | Rolling average of successful samples from the last 5 minutes |
| `sensor.froeling_aktuelle_leistung_des_solar_wmz_average_5minutes_w` | W | Same 5-minute average in W |
| `sensor.froeling_aktuelle_leistung_des_solar_wmz_average_10minutes` | kW | Rolling average of successful samples from the last 10 minutes |
| `sensor.froeling_aktuelle_leistung_des_solar_wmz_average_10minutes_w` | W | Same 10-minute average in W |

The original Fröling value is read as:

```text
register 32611 / 100 = kW
```

For the rolling averages, a real `0 kW` sample is included. Failed Modbus reads are not added to the average. The rolling history is held in memory, so it starts filling again after a Home Assistant restart.

With the default 60-second update interval, the 5-minute sensor uses roughly the most recent 5 minutes of samples and the 10-minute sensor roughly the most recent 10 minutes.

### Solar total energy

Fröling exposes the total solar yield in two registers:

| Entity | Register | Unit |
|---|---:|---:|
| `sensor.froeling_solarthermie_mwh` | 32621 | MWh |
| `sensor.froeling_solarthermie_kwh` | 32622 | kWh |
| `sensor.froeling_solarthermie_gesamtertrag` | calculated | kWh |

The combined total is calculated as:

```text
solarthermie_gesamtertrag = solarthermie_mwh * 1000 + solarthermie_kwh
```

Example:

```text
56 MWh + 925 kWh = 56,925 kWh
```

### Resettable pellet counter

The existing resettable counters are kept and an additional combined kg sensor is provided:

| Entity | Register | Unit |
|---|---:|---:|
| `sensor.froeling_resetierbarer_kg_zahler` | 30082 | kg |
| `sensor.froeling_resetierbarer_t_zahler` | 30083 | t |
| `sensor.froeling_resetierbarer_kg_zahler_gesamt` | calculated | kg |

Calculation:

```text
resetierbarer_kg_zahler_gesamt = resetierbarer_t_zahler * 1000 + resetierbarer_kg_zahler
```

---

## 💻 Requirements

You need a Modbus-to-TCP device. This integration has been tested with the Waveshare RS232/RS485 to Ethernet Converter; other Serial-to-Ethernet adapters should work.

> ⚠️ **Important – RS232 & Nullmodem cable required**
>
> Fröling Lambdatronic systems communicate via **Modbus RTU over RS232** on **COM2**.
>
> - ❌ **RS485-only adapters will NOT work**
> - ✔ You must use an **RS232-capable Serial-to-Ethernet converter**
> - 🔁 A **nullmodem (crossed) RS232 cable** is required (direct / straight RS232 cables will not work)

### 🔧 Enabling Modbus RTU on the Boiler

To enable Modbus RTU on your Fröling boiler:

1. Click the user icon and enter code `-7`.
2. Adjust the following settings:
   - **Settings > General Settings > MODBUS Settings > Modbus Protokoll RTU** → `Set to 1`
   - **Settings > General Settings > MODBUS Settings > Use Modbus Protokoll 2014** → `Yes`
   - **Settings > General Settings > MODBUS Settings > Use COM2 as MODBUS Interface** → `Yes`

---

## 🛠️ Hardware Setup

Use a Serial-to-Ethernet converter between the boiler’s COM2 and your network.

### Example 1: Waveshare RS232/RS485 to Ethernet Converter

- Converter connected via RS232 to COM2 on the boiler.
- Example configuration screenshot:

  ![Waveshare RS232/RS485 to Ethernet Converter configuration](docs/image.png)

### Example 2: Waveshare RS232/485/422 TO POE ETH (B) Converter

- Converter connected via RS232 to COM2 on the boiler.
- Example configuration screenshot:

  ![Waveshare RS232/485/422 TO POE ETH (B) configuration](docs/Waveshare_RS232_485_422_TO_POE_ETH_B.png)

Other Serial-to-Ethernet converters should also work.

If you're looking for a way to power your Serial Ethernet converter directly from your Fröling board, check this out:
[Power Supply](docs/power_supply.md)

---

## 📦 Installation

### HACS – this fork

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=empi00&repository=ha_froeling_lambdatronic_modbus&category=integration)

- Ensure [HACS](https://hacs.xyz/) is installed.
- Add `https://github.com/empi00/ha_froeling_lambdatronic_modbus` as a **Custom repository** with category **Integration** if it is not listed automatically.
- Install **Froeling Lambdatronic Modbus**.
- Restart Home Assistant.
- Add the integration via **Settings → Devices & services → Add integration**.

### Manual

- Download this repository as ZIP: `https://github.com/empi00/ha_froeling_lambdatronic_modbus/archive/refs/heads/main.zip`
- Copy `custom_components/froeling_lambdatronic_modbus` into your Home Assistant `custom_components` folder.
- Restart Home Assistant.
- Add the integration via the Home Assistant UI.

---

## 🛠️ Setup

1. Settings → Integrations → “+ Add Integration”.
2. Select “Froeling Lambdatronic Modbus”.
3. Fill out the form:
   - Device name (Default: Froeling)
   - Hostname/IP of your Modbus TCP device
   - Port (Default: 502)
   - Update Interval (Default: 60s)
   - Select installed components on your unit, including **Solarthermie** and/or **Austragung** when the new calculated entities are required.
4. In the entity selection step, enable the desired calculated sensors as well as the normal Modbus sensors.
5. Submit and wait for entities to appear.

---

## 📊 Entities Overview

- Sensors:
  - Temperatures (e.g., Kesseltemperatur, Abgastemperatur, HK Vorlauf), loads, consumption, etc.
  - Solar heat-meter power in kW and W.
  - Solar 5-minute and 10-minute rolling average power sensors in kW and W.
  - Corrected combined solar total energy in kWh.
  - Combined resettable pellet counter in kg.
- Text Sensors:
  - Anlagenzustand, Kesselzustand (mapped from numeric states).
  - Boiler error buffers (20 slots)
- Numbers:
  - Writable setpoints and parameters (e.g., Kessel_Solltemperatur).
  - Proper step sizes and input box UI.
- Selects:
  - Betriebsart for heating circuits (e.g., HK01/HK02), options: Aus, Automatik, Extraheizen, Absenken, Dauerabsenken, Partybetrieb.

## 🧩 Visualization

- Lovelace: Checkout the Fröling Card (HACS): https://github.com/GyroGearl00se/lovelace-froeling-card
- Example:
  ![image](https://github.com/user-attachments/assets/077fbc1d-9ca0-475b-b266-77067cb2650f)

## 🧡 Contributing

Contributions are welcome!

1. **[Fork this repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo).**
2. Make changes within your fork.
3. **[Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).**

---

## Disclaimer

This project is not affiliated with or endorsed by Fröling. All trademarks are property of their respective owners.
