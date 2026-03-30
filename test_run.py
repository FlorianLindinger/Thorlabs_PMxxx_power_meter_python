"""Example script for connecting to a Thorlabs PMxxx meter and logging power."""

import os
import sys
import time
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from Thorlabs_PMxxx_power_meter import error_print, power_meter_handler

def main():
    """Run a simple measurement loop and append readings to `test.csv`."""
    wavelength_nm = 1980  # None to not set
    device_idx = -1  # negative indexing allowed
    auto_range = True  # None to not set
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # move to folder of this file for relative import of dll_path
    dll_path = r".\TLPMX_64.dll"  # set None for globally installed one

    time_between_reads_s = 0.5
    log_path = "test.csv"
    num_reads = 3  # None for infinite

    try:
        pm = power_meter_handler(dll_path=dll_path)
        success = pm.connect(device_idx)
        if success == False:
            print("Failed to connect to PM. Aborting")
            sys.exit()

        success = pm.set_wavelength_nm(wavelength_nm)  # set wavelength
        if success == False:
            print("Failed to set wl. Aborting")
            sys.exit()

        success = pm.set_auto_range(auto_range)  # set auto range
        if success == False:
            print("Failed to set auto range. Aborting")
            sys.exit()

        if not os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("Date (Year.Month.Day)\tTime (Hour:Minute:Second)\tPower (Watt)\n")

        if num_reads is None:  # type:ignore
            infinite = True
            num_reads = 1
        else:
            infinite = False
        ran_once = False
        while (infinite == True) or (ran_once == False):
            for _ in range(num_reads):
                power = pm.read_power_W()
                if power is not None:
                    print(power)
                    ts = datetime.now().astimezone().strftime("%Y.%m.%d\t%H:%M:%S")
                    line = f"{ts}\t{power:.3f}\n"

                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(line)
                time.sleep(time_between_reads_s)
            ran_once = True

    except Exception as e:
        error_print(f"Except: {e}")
    finally:  # works also for keyborad interrupt
        try:
            pm.final_shutdown()  # type:ignore
        except Exception:
            pass


if __name__ == "__main__":
    main()
