import evdev

print evdev.list_devices()

devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

for device in devices:
    print device.fn, device.name, device.phys
