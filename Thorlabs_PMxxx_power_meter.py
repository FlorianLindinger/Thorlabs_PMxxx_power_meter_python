"""Python wrapper for Thorlabs PMxxx power meters using the TLPMX driver.

Example:
    wavelength_nm = 1980
    device_index = -1
    auto_power_range = True
    dll_path = r".\\TLPMX_64.dll"

    pm = power_meter_handler(dll_path)
    pm.connect(device_index)
    pm.set_auto_range(auto_power_range)
    pm.set_wavelength_nm(wavelength_nm)
    power_W = pm.read_power_W()
    print(power_W)
"""

import atexit
import os
import time
import traceback
from ctypes import (
    byref,
    c_bool,
    c_char_p,
    c_double,
    c_int,
    c_int16,
    c_long,
    c_uint16,
    c_uint32,
    cdll,
    create_string_buffer,
)

from TLPMX import (
    TLPM_DEFAULT_CHANNEL,
    TLPMX,
)

################


def error_print(message, max_wrapper_len=20, wrapper_symbol="=", middle_symbol="-"):
    """Print an error banner and the active traceback, if one exists."""
    msg_len = len(message)
    if msg_len > max_wrapper_len:
        msg_len = max_wrapper_len
    print(wrapper_symbol * msg_len)
    print(message)
    error = traceback.format_exc()
    if error.strip() != "NoneType: None":
        print(middle_symbol * msg_len)
        print(error, end="")
    print(wrapper_symbol * msg_len)


class TLPMX_with_dll_path(TLPMX):
    """Small TLPMX subclass that loads the 64-bit DLL from a chosen path."""

    def __init__(self, dll_path=r".\TLPMX_64.dll"):
        """dll_path is the path to TLPMX_64.dll. By default it checks for the dll in the current folder. If dll_path==None it uses the normal global dll install path for the Thorlabs dlls."""
        if dll_path is None:
            dll_path="C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPMX_64.dll"
        else:
            dll_path = os.path.abspath(dll_path)
        # __init__ has same attributes defined as in TLPMX.__init__():
        self.dll = cdll.LoadLibrary(dll_path)
        self.devSession = c_long()
        self.devSession.value = 0


class power_meter_handler:
    """High-level interface for reading power from Thorlabs PMxxx meters."""

    pm: TLPMX_with_dll_path | None

    def __init__(
        self,
        dll_path="C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPMX_64.dll",
        sleep_time_after_connecting_s: float | None = 0.1,
    ):
        """Create a power meter handler.

        Args:
            dll_path: Path to `TLPMX_64.dll`. If `None`, the default global
                Thorlabs install path is used.
            sleep_time_after_connecting_s: Delay after opening the device to
                let the driver settle before the first command.
        """
        self.sleep_time_after_connecting_s = sleep_time_after_connecting_s
        self.device_index = None
        self.pm = None
        if dll_path is None:
            dll_path="C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPMX_64.dll"
        self.dll_path = dll_path
        # initialized C variables:
        self._C_deviceCount = c_uint32()
        self._C_resourceName = create_string_buffer(1024)
        self._C_power = c_double()
        self._C_wavelength_nm = c_double()
        self._C_auto_range = c_int16()
        # run on exit:
        atexit.register(self.disconnect)

    def set_wavelength_nm(self, wavelength_nm, print_error=True) -> bool:
        """Set the wavelength in nanometers for the active power meter."""
        if self.pm is not None:
            try:
                success = self.pm.setWavelength(c_double(wavelength_nm), TLPM_DEFAULT_CHANNEL) == 0
                return success
            except Exception as e:
                if print_error:
                    error_print(f"[Error] Failed to set wavelength for Thorlabs power meter: {e}")
                return False
        else:
            return False

    def get_auto_range(self) -> None | bool:
        """Return the current auto-range state, or `None` on failure."""
        if self.pm is not None:
            success = self.pm.getPowerAutorange(byref(self._C_auto_range), c_uint16(1)) == 0
            if success:
                return bool(self._C_auto_range)
            else:
                return None
        else:
            return None

    def get_wavelength_nm(self) -> None | float:
        """Return the configured wavelength in nanometers."""
        if self.pm is not None:
            success = self.pm.getWavelength(c_int16(0), byref(self._C_wavelength_nm), c_uint16(0)) == 0
            if success:
                return float(self._C_wavelength_nm)
            else:
                return None
        else:
            return None

    def get_available_devices(self, print_error=True) -> list[str] | None:
        """Return the VISA resource names of discoverable Thorlabs meters."""
        try:
            pm_tmp = TLPMX_with_dll_path(self.dll_path)
            pm_tmp.findRsrc(byref(self._C_deviceCount))

            out = []
            for i in range(self._C_deviceCount.value):
                pm_tmp.getRsrcName(c_int(i), self._C_resourceName)
                out.append(str(c_char_p(self._C_resourceName.raw).value))
            return out
        except Exception as e:
            if print_error:
                error_print(f"[Error] Failed to get available Thorlabs power meter devices: {e}")
            return None
        finally:
            try:
                pm_tmp.close()  # type:ignore
            except Exception:
                pass

    def connect(self, device_index: int, print_error=True) -> bool:
        """Connect to the selected device index and configure watt output."""

        self.disconnect()

        # Find connected power meter devices.
        try:
            pm_tmp = TLPMX_with_dll_path(self.dll_path)
            pm_tmp.findRsrc(byref(self._C_deviceCount))
            if self._C_deviceCount.value == 0:
                print(
                    "[Warning] No Thorlabs power meter of series PMxxx found. Aborting Thorlabs power meter connection."
                )
                return False
            elif (device_index > self._C_deviceCount.value - 1) or (
                (device_index < 0) and (abs(device_index) > self._C_deviceCount.value)
            ):
                print(
                    f"[Warning] Device index {device_index} out of range of available number {self._C_deviceCount.value}. Aborting Thorlabs power meter connection."
                )
                print("Available connection:")
                print(self.get_available_devices())
                print("")
                return False
            else:
                if device_index < 0:  # negative indexing
                    device_index = self._C_deviceCount.value + device_index
                # get name of target device -> resourceName
                pm_tmp.getRsrcName(c_int(device_index), self._C_resourceName)
                # resourceName -> Connect to target device
                pm = TLPMX_with_dll_path(self.dll_path)
                pm.open(self._C_resourceName, c_bool(True), c_bool(True))
                if self.sleep_time_after_connecting_s is not None:
                    time.sleep(self.sleep_time_after_connecting_s)
                # Set power unit to Watt.
                # 0 -> Watt
                # 1 -> dBm
                pm.setPowerUnit(c_int16(0), TLPM_DEFAULT_CHANNEL)

                self.pm = pm
                self.device_index = device_index
                return True

        except Exception as e:
            try:
                pm.close()  # type:ignore
            except Exception:
                pass
            if print_error:
                error_print(f"[Error] Connection to Thorlabs power meter failed: {e}")
            return False
        finally:
            try:
                pm_tmp.close()  # type:ignore
            except Exception:
                pass

    def set_auto_range(self, on, print_error=True):
        """Enable or disable automatic power range selection."""
        if self.pm is not None:
            try:
                success = self.pm.setPowerAutoRange(c_int16(int(on)), TLPM_DEFAULT_CHANNEL) == 0
                return success
            except Exception as e:
                if print_error:
                    error_print(f"[Error] Failed to set auto range: {e}")
                return False
        else:
            return False

    def disconnect(self):
        """Close the active device session, if one exists."""
        if self.pm is not None:
            try:
                self.pm.close()
            except Exception:
                pass

            self.device_index = None
            self.pm = None

    def read_power_W(self, print_error=True) -> float | None:
        """Read the current power in watts, or `None` on failure."""
        if self.pm is None:
            print("[Warning] Connect power meter before measurement.")
            return None
        else:
            try:
                self.pm.measPower(byref(self._C_power), TLPM_DEFAULT_CHANNEL)
                power_W = self._C_power.value
                return power_W
            except Exception as e:
                if print_error:
                    error_print(f"[Error] Failed to read Thorlabs power meter: {e}")
                return None

    def is_connected(self) -> bool:
        """Return `True` when an active device session exists."""
        return self.pm is not None

