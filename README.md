# Touchscreen stenotype
On-screen touch stenotype plugin for Plover.

## Recommended setup
Operating systems may have built-in touchscreen gestures that sometimes prevent the window from receiving touches.

Windows 10/11 users: This works best after disabling 3- and 4-finger touch gestures in Settings (`Bluetooth & devices` > `Touch`, or navigate to `ms-settings:devices-touch` from the browser).

Linux+GNOME users: There are [GNOME extensions that can disable touch gestures](https://extensions.gnome.org/extension/1140/disable-gestures/), but there is additionally a delay before windows receive touch inputs, which will have to be dealt with as well (check `xinput` and `libinput`?).