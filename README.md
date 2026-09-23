<p align="center">
  <img width="200" src="res/bt-volume-step.svg" alt="bt-volume-step">
</p>

<h1 align="center">bt-volume-step</h1>

<h3 align="center">Fixed volume steps for Bluetooth audio devices on PipeWire.</h3>

<p align="center">
  One press or swipe on your earbuds or speaker becomes one clean step on your volume slider.
</p>

<h5 align="center">
  <a href="#usage">How to use</a> |
  <a href="#installation">Install</a> |
  <a href="https://buymeacoffee.com/felitendo">☕ Buy Me a Coffee</a>
</h5>

## The problem

Many Bluetooth devices carry a coarse internal volume grid. AirPods Pro expose
only 16 AVRCP steps, so every swipe on the stem moves the system volume by
6.25 %, and the on-screen display walks through

```
6 · 13 · 19 · 25 · 31 · 38 · 44 · 50 · 56 · 63 · 69 · 75 · 81 · 88 · 94 · 100
```

instead of clean multiples of five. A speaker's volume buttons do the same
thing with whatever grid that speaker happens to use.

This is not a desktop misconfiguration. KDE's own volume step is already
exactly 5 %. The grid lives in the device firmware, and it cannot be changed:
the device sends *absolute* volume values over AVRCP, not increments.

## What this does

`bt-volume-step` watches for device-initiated volume changes, takes only their
*direction* into account, and applies a clean step of its own instead. One
press or swipe on the device becomes one step on your desktop's grid.

It works because such devices adopt a volume written back over AVRCP silently,
without reporting it, so there is no feedback loop. As a side effect the
device's internal position follows the corrected value, which keeps it from
running into the end of its own scale.

## Requirements

- PipeWire with `pactl` (`libpulse`)
- Python 3.9 or newer
- Optional: `kreadconfig6` (KDE Plasma) to follow the desktop's own step size
- Optional: `bluez-utils` for device names in `--show`

## Installation

### Arch Linux

```bash
yay -S bt-volume-step
```

### From source

```bash
sudo make install
```

`make install` honours `PREFIX` and `DESTDIR`; for a per-user install use
`make install PREFIX=$HOME/.local`.

## Usage

Enable it for your user session:

```bash
systemctl --user enable --now bt-volume-step
```

That is the whole setup. Connect a Bluetooth device and use its volume
control.

## Calibration

The daemon measures each device's grid on its own. **While a device's grid is
unknown it does not intervene at all**, it only watches. Once the same jump
has repeated three times, that jump is accepted as the device step and
remembered, and corrections start from then on. In practice: press volume-up
three or four times on a new device and it is set up.

Show what has been measured:

```bash
bt-volume-step --show
```

```
file: /home/you/.local/state/bt-volume-step/devsteps.json
  AirPods Pro (30_0E_43_04_52_19) = 6.25 % (16 steps)
```

Discard a measurement (all devices, or one MAC):

```bash
bt-volume-step --reset
bt-volume-step --reset 30_0E_43_04_52_19
```

To keep the daemon from calibrating itself onto keyboard input, jumps that
match the desktop's own step size are excluded from measurement, as are jumps
below 1.5 % or above 20 %. A device whose grid happens to equal the desktop
step therefore never calibrates, and is left alone.

## Configuration

On KDE Plasma the step size comes from *System Settings → Audio → Volume step*
(`plasmaparc [General] VolumeStep`, read through `kreadconfig6` so KDE's
configuration cascade applies). Changes take effect within two seconds, with
no restart. On other desktops, or without `kreadconfig6`, it falls back to
5 %.

Everything can be overridden through the environment. Put these in a drop-in
(`systemctl --user edit bt-volume-step`):

| Variable | Effect |
|---|---|
| `BT_VOL_STEP` | fixed step size in percent; ignores the desktop setting |
| `BT_VOL_DEVSTEP` | fixed device grid in percent; skips measurement |
| `BT_VOL_MAC` | only watch this device (MAC with `_` instead of `:`) |
| `BT_VOL_MAX` | upper limit in percent (default 100) |

The daemon handles several connected Bluetooth devices at once, keeping state
and calibration per device.

## Localisation

Messages follow `LC_ALL` / `LC_MESSAGES` / `LANG`. English and German are
included; other languages fall back to English. To add one, extend
`TRANSLATIONS` in the script. English strings are the keys.

## Limitations

**Foreign volume changes can be misread.** PipeWire events carry no
information about where a change came from, so a jump that happens to match
one or two device steps is indistinguishable from a button press. The daemon
accepts at most two steps per event to keep that window narrow, but it cannot
close it entirely.

**Devices that report their volume back are not supported.** The approach
assumes a device accepts a written volume silently. One that echoes a snapped
value back would oscillate. To check, set a volume and watch it for a few
seconds:

```bash
pactl set-sink-volume bluez_output.XX_XX_XX_XX_XX_XX.1 40%
sleep 5 && pactl get-sink-volume bluez_output.XX_XX_XX_XX_XX_XX.1
```

If the value drifts on its own, this tool is the wrong approach; disabling
hardware volume (`bluez5.enable-hw-volume = false` in WirePlumber) is the
alternative, at the cost of the device's own control.

## Tests

```bash
make check
```

Covers the decision logic and the measurement, including simulated devices
with 8, 16 and 32 steps.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
