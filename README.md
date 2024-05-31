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

On Windows 11 22H2: The default touch keyboard can be stopped from automatically appearing by setting “Show the touch keyboard” to “Never” in the “Touch keyboard” settings (under `Time & language` > `Typing` on Windows 11, or `ms-settings:typing` from the browser).
* On Windows 10 or older Windows 11: The default keyboard can be stopped from automatically appearing, to varying degrees of success, by disabling “Show the touch keyboard when … there’s no keyboard attached” in the “Touch keyboard” settings (under `Time & language` > `Typing` on Windows 11, `Devices` > `Typing` on Windows 10, or `ms-settings:typing` from the browser).

On Linux+GNOME: There are [GNOME extensions that can disable touch gestures](https://extensions.gnome.org/extension/1140/disable-gestures/), but there is additionally a delay before windows receive touch inputs. Unless dealt with (check `xinput` and `libinput`?), this will require users to hold down a stroke for a brief period of time (~200 ms?) before releasing; releasing early will cause each touch to be registered as a stroke individually.


## Entrypoints


### Tools
The `Touchscreen stenotype` tool is exposed. After the plugin is installed, Plover may need to be restarted for the plugin GUI button to appear in the toolbar.

The keyboard shortcut <kbd>Ctrl</kbd> + <kbd>S</kbd> opens the settings window (if the stenotype window is focused, which can be achieved by clicking the window's top bar).


### Commands
Some of these commands may be useful when the "Frameless" setting is enabled, since in frameless mode, various UI elements are hidden/inaccessible from the window and the window is not as easily focusable.

Command | Description
-|-
<!-- `{plover:touchscreen_stenotype.open}` | Opens the stenotype window. -->
`{plover:touchscreen_stenotype.close}` | Closes the stenotype window.
`{plover:touchscreen_stenotype.minimize}` | Minimizes the stenotype window.
`{plover:touchscreen_stenotype.open_settings}` | Opens the settings dialog.


### Machines
The `(None)` machine allows all hardware machines to be disabled, allowing only the touchscreen stenotype to provide strokes.


## Notes

The key layout is currently based on the default English Stenotype system. This works best on touchscreens that support at least 10 simultaneous touch points. On Windows 10/11, the maximum number of touch points can be found alongside the device specifications in Settings (`System` > `About`, or navigate to `ms-settings:about` from the browser).