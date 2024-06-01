"""
Python wrapper for the USB Relay Device library, created by ChatGPT from the header file
"""

import ctypes
from ctypes import c_int, c_char_p, c_uint, c_void_p, POINTER, Structure

dll_path = "./usb_relay_device.dll"

# Load the DLL
usb_relay_lib = ctypes.CDLL(dll_path)


# Define the usb_relay_device_info structure
class UsbRelayDeviceInfo(Structure):
    pass


UsbRelayDeviceInfo._fields_ = [
    ("serial_number", c_char_p),
    ("device_path", c_char_p),
    ("type", c_void_p),
    ("next", POINTER(UsbRelayDeviceInfo)),
]

# Initialize the USB Relay Library
usb_relay_init = usb_relay_lib.usb_relay_init
usb_relay_init.restype = c_int

# Finalize the USB Relay Library
usb_relay_exit = usb_relay_lib.usb_relay_exit
usb_relay_exit.restype = c_int

# Enumerate the USB Relay Devices
usb_relay_device_enumerate = usb_relay_lib.usb_relay_device_enumerate
usb_relay_device_enumerate.restype = POINTER(UsbRelayDeviceInfo)

# Free an enumeration Linked List
usb_relay_device_free_enumerate = usb_relay_lib.usb_relay_device_free_enumerate
usb_relay_device_free_enumerate.argtypes = [POINTER(UsbRelayDeviceInfo)]

# Open device with serial number
usb_relay_device_open_with_serial_number = (
    usb_relay_lib.usb_relay_device_open_with_serial_number
)
usb_relay_device_open_with_serial_number.restype = c_void_p
usb_relay_device_open_with_serial_number.argtypes = [c_char_p, c_uint]

# Open a USB relay device
usb_relay_device_open = usb_relay_lib.usb_relay_device_open
usb_relay_device_open.restype = c_void_p
usb_relay_device_open.argtypes = [POINTER(UsbRelayDeviceInfo)]

# Close a USB relay device
usb_relay_device_close = usb_relay_lib.usb_relay_device_close
usb_relay_device_close.argtypes = [c_void_p]

# Turn ON a relay channel on the USB-Relay-Device
usb_relay_device_open_one_relay_channel = (
    usb_relay_lib.usb_relay_device_open_one_relay_channel
)
usb_relay_device_open_one_relay_channel.restype = c_int
usb_relay_device_open_one_relay_channel.argtypes = [c_void_p, c_int]

# Turn ON all relay channels on the USB-Relay-Device
usb_relay_device_open_all_relay_channel = (
    usb_relay_lib.usb_relay_device_open_all_relay_channel
)
usb_relay_device_open_all_relay_channel.restype = c_int
usb_relay_device_open_all_relay_channel.argtypes = [c_void_p]

# Turn OFF a relay channel on the USB-Relay-Device
usb_relay_device_close_one_relay_channel = (
    usb_relay_lib.usb_relay_device_close_one_relay_channel
)
usb_relay_device_close_one_relay_channel.restype = c_int
usb_relay_device_close_one_relay_channel.argtypes = [c_void_p, c_int]

# Turn OFF all relay channels on the USB-Relay-Device
usb_relay_device_close_all_relay_channel = (
    usb_relay_lib.usb_relay_device_close_all_relay_channel
)
usb_relay_device_close_all_relay_channel.restype = c_int
usb_relay_device_close_all_relay_channel.argtypes = [c_void_p]

# Get state of all channels of the USB-Relay-Device
usb_relay_device_get_status = usb_relay_lib.usb_relay_device_get_status
usb_relay_device_get_status.restype = c_int
usb_relay_device_get_status.argtypes = [c_void_p, POINTER(c_uint)]


def initialize_relay_device():
    if usb_relay_init() != 0:
        raise Exception("Failed to initialize the USB relay library")
    devices = usb_relay_device_enumerate()
    if not devices:
        raise Exception("No USB relay devices found")
    device = devices.contents
    handle = usb_relay_device_open(ctypes.byref(device))
    if not handle:
        raise Exception("Failed to open the USB relay device")
    print(f"Device {device.serial_number.decode()} opened successfully")
    return handle, devices


def finalize_relay_device(handle, devices):
    usb_relay_device_close(handle)
    usb_relay_device_free_enumerate(devices)
    if usb_relay_exit() != 0:
        raise Exception("Failed to finalize the USB relay library")
    print("Relay device closed successfully")


def relay_on(handle, channel=1):
    result = usb_relay_device_open_one_relay_channel(handle, channel)
    if result != 0:
        raise Exception(f"Failed to turn on relay channel {channel}, error code: {result}")


def relay_off(handle, channel=1):
    result = usb_relay_device_close_one_relay_channel(handle, channel)
    if result != 0:
        raise Exception(f"Failed to turn off relay channel {channel}, error code: {result}")
