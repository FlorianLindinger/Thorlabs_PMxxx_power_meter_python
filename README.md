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

## Upstream TLPMX.py

`TLPMX.py` in this repository is intentionally kept as a copied upstream file
from Thorlabs and should not be edited as part of the local wrapper code.

Official upstream repository and file path:

- Repository: `Thorlabs/Light_Analysis_Examples`
- Path: `Python/Thorlabs PMxxx Power Meters/TLPMX_dll/TLPMX.py`
- URL: https://github.com/Thorlabs/Light_Analysis_Examples/blob/main/Python/Thorlabs%20PMxxx%20Power%20Meters/TLPMX_dll/TLPMX.py

The surrounding wrapper code in this repo builds on top of that copied file.

## Requirements

- Windows
- Python 3.10+ recommended
- A Thorlabs PMxxx power meter supported by the TLPMX driver
- `TLPMX.py`
- `TLPMX_64.dll`

No third-party Python packages are required.

## Where To Get The Driver DLL

This project expects the 64-bit Thorlabs driver DLL `TLPMX_64.dll`.

The code supports either:

1. The default global install path:

```text
C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPMX_64.dll
```

2. A local copy in this repository folder:

```text
.\TLPMX_64.dll
```

Thorlabs states that the Optical Power Monitor software package installs the
drivers, utilities, and programming examples for supported power meters.

Official Thorlabs software page:

- https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=3341&partnumber=CAL-PM1

The upstream Thorlabs example repository for PMxxx meters is here:

- https://github.com/Thorlabs/Light_Analysis_Examples/tree/main/Python/Thorlabs%20PMxxx%20Power%20Meters/TLPMX_dll

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
        pm.final_shutdown()
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

## License

The original wrapper code in this repository is MIT licensed. The copied
`TLPMX.py` file and the vendor-provided `TLPMX_64.dll` are third-party files
that remain under their own included license terms. See `LICENSE`,
`LICENSE.md`, `TLPMX.py LICENSE.txt`, and `TLPMX_64.dll LICENSE.txt`.
