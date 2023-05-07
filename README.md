# Plover touchscreen stenotype
On-screen touch stenotype plugin for Plover.

<!-- This nested embed will appear as a video on GitHub, but elsewhere it will embed the image -->
[
Demo recording (if below is playing slowly or not playing)<br /> <!-- <br /> used to resolve a spacing issue in the Plover Plugins Manager markdown renderer -->
![](https://user-images.githubusercontent.com/22846982/236664546-8afe8d21-2dc6-48b4-8486-fc5be10a7be0.gif)
](https://user-images.githubusercontent.com/22846982/236663907-51b4064b-2925-4da0-8359-d7419302dd8b.mp4)


## Additional setup / troubleshooting
Operating systems may have built-in touchscreen gestures that sometimes prevent the window from receiving touches.

On Windows 11: This works best after disabling 3- and 4-finger touch gestures in Settings (`Bluetooth & devices` > `Touch`, or navigate to `ms-settings:devices-touch` from the browser).

On Windows 10/11: The default touch keyboard can be stopped from automatically appearing whenever a textbox is touched (sometimes) by disabling “Show the touch keyboard when … there’s no keyboard attached” in the touch keyboard settings (under `Time & language` > `Typing` on Windows 11, `Devices` > `Typing` on Windows 10, or `ms-settings:typing` from the browser).

On Linux+GNOME: There are [GNOME extensions that can disable touch gestures](https://extensions.gnome.org/extension/1140/disable-gestures/), but there is additionally a delay before windows receive touch inputs, which will have to be dealt with as well (check `xinput` and `libinput`?).


## Notes

The key layout is currently based on the default English Stenotype system. This works best on touchscreens that support at least 10 simultaneous touch points. On Windows 10/11, the maximum number of touch points can be found alongside the device specifications in Settings (`System` > `About`, or navigate to `ms-settings:about` from the browser).

After the plugin is installed, Plover may need to be restarted for the plugin GUI button to appear in the toolbar.