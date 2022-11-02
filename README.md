# Plover touchscreen stenotype
On-screen touch stenotype plugin for Plover.

<!-- This nested embed will appear as a video on GitHub, but elsewhere it will embed the image -->
[
Demo recording (if below is playing slowly or not playing)<br /> <!-- <br /> used to resolve a spacing issue in the Plover Plugins Manager markdown renderer -->
![](https://user-images.githubusercontent.com/22846982/200047983-64c948df-cbca-4590-a6b7-c397ecff4724.gif)
](https://user-images.githubusercontent.com/22846982/199911422-0c08d1f0-7ce9-4d74-8658-8384142ab3ee.mp4)


## Additional setup / troubleshooting
Operating systems may have built-in touchscreen gestures that sometimes prevent the window from receiving touches.

On Windows 11: This works best after disabling 3- and 4-finger touch gestures in Settings (`Bluetooth & devices` > `Touch`, or navigate to `ms-settings:devices-touch` from the browser).

On Windows 10/11: The default touch keyboard can be stopped from automatically appearing whenever a textbox is touched (sometimes) by disabling “Show the touch keyboard when … there’s no keyboard attached” in the touch keyboard settings (under `Time & language` > `Typing` on Windows 11, `Devices` > `Typing` on Windows 10, or `ms-settings:typing` from the browser).

On Linux+GNOME: There are [GNOME extensions that can disable touch gestures](https://extensions.gnome.org/extension/1140/disable-gestures/), but there is additionally a delay before windows receive touch inputs, which will have to be dealt with as well (check `xinput` and `libinput`?).


## Notes

The key layout is currently based on the default English Stenotype system. This works best on touchscreens that support at least 10 simultaneous touch points. On Windows 10/11, the maximum number of touch points can be found alongside the device specifications in Settings (`System` > `About`, or navigate to `ms-settings:about` from the browser).

After the plugin is installed, Plover may need to be restarted for the plugin GUI button to appear in the toolbar.