# Thorlabs_PMxxx_power_meter_python

Python wrapper for Thorlabs PMxxx power meters using the `TLPMX` driver API on
Windows.

This repository provides:

- A small Python API for connecting to compatible Thorlabs PMxxx meters.
- A lightweight wrapper around the upstream `TLPMX.py` example class.
- An example script that logs measured power to `test.csv`.

## What This Repo Does

The main module, `Thorlabs_PMxxx_power_meter.py`, exposes the
`power_meter_handler` class. It can:

- Discover connected PMxxx devices.
- Connect to a selected device by index.
- Set and read wavelength.
- Enable or disable auto range.
- Read current power in watts.

## Backend code copies from Thorlabs: TLPMX.py and TLPMX_64.dll

Both files are allowed copies from Thorlabs and fall under their repective licenses (see LICENSE.md):
- TLPMX.py is a copy from Thorlabs' repo https://github.com/Thorlabs/Light_Analysis_Examples/blob/main/Python/Thorlabs%20PMxxx%20Power%20Meters/TLPMX_dll/TLPMX.py
- TLPMX_64.dll is a dll from Thorlabs that gets usually installed under C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPMX_64.dll when running Thorlabs installer from https://media.thorlabs.com/contentassets/012d23129bc54ff2bfdbf4c6d4a306fa/thorlabs.opticalparametermonitor.7.0.5320.947.zip?v=0325122421 (webside: https://www.thorlabs.com/software-pages/opm/)

## Requirements

- Windows
- A Thorlabs PMxxx power meter supported by the TLPMX driver

## Basic Usage

```python
from Thorlabs_PMxxx_power_meter import power_meter_handler

pm = power_meter_handler(dll_path=None)

if pm.connect(device_index=-1):
    try:
        pm.set_auto_range(True)
        pm.set_wavelength_nm(1980)
        power_W = pm.read_power_W()
        print(power_W)
    finally:
        pm.disconnect()
```

## Example Script

`test_run.py` shows a simple logging workflow. It:

- Connects to the selected PMxxx device.
- Optionally sets wavelength and auto range.
- Reads power repeatedly.
- Appends timestamped measurements to `test.csv`.

Run it from the repository directory:

```powershell
python .\test_run.py
```
