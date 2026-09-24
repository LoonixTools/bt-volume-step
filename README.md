<p align="center">
  <img width="200" src="res/bt-volume-step.svg" alt="bt-volume-step">
</p>

<h1 align="center">bt-volume-step</h1>

<h3 align="center">Clean volume steps for Bluetooth headphones and speakers.</h3>

<p align="center">
  One press or swipe on your device becomes one clean step on your volume slider.
</p>

<h5 align="center">
  <a href="#install">Install</a> |
  <a href="#how-to-use">How to use</a> |
  <a href="https://github.com/LoonixTools/bt-volume-step/issues">Report a bug</a>
</h5>

<p align="center">
  <a href="https://ko-fi.com/felitendo"><img src="https://storage.ko-fi.com/cdn/kofi5.png?v=6" alt="Buy me a coffee on Ko-fi" height="48"></a>
</p>

| | Volume after each swipe on AirPods Pro |
|---|---|
| Before | 6 · 13 · 19 · 25 · 31 · 38 · 44 · 50 ... |
| After | 5 · 10 · 15 · 20 · 25 · 30 · 35 · 40 ... |

## Install

```bash
yay -S bt-volume-step
systemctl --user enable --now bt-volume-step
```

Needs PipeWire and Python 3.9 or newer.

## How to use

Connect your device and press volume up three or four times. Now it knows the device and every
step is clean.

```bash
bt-volume-step --show    # what it measured
bt-volume-step --reset   # forget it
```

## More

<details>
<summary>How it works</summary>

Many Bluetooth devices only know a few volume steps (AirPods Pro: 16), and they send the volume as a
number, not as "up" or "down". bt-volume-step only looks at which way the volume moved and sets a
clean step of its own. The device takes that new volume without a word, so nothing fights back.

It only steps in once it has seen the same jump three times. Until then it just watches.

</details>

<details>
<summary>Settings</summary>

On KDE Plasma the step comes from *System Settings → Audio → Volume step*, elsewhere it is 5 %.
To change more, use `systemctl --user edit bt-volume-step`:

| | |
|---|---|
| `BT_VOL_STEP` | Fixed step in percent |
| `BT_VOL_DEVSTEP` | Fixed device step, skips measuring |
| `BT_VOL_MAC` | Only this device (MAC with `_` instead of `:`) |
| `BT_VOL_MAX` | Highest volume in percent (default 100) |

</details>

<details>
<summary>Limits</summary>

- A volume change from somewhere else that happens to match one or two device steps can be read
  as a swipe.
- Devices that report their volume back are not supported. Set a volume and check after a few
  seconds with `pactl get-sink-volume`: if it moved on its own, this tool is not for that device.

</details>

<details>
<summary>Build from source</summary>

```bash
sudo make install
make check
```

`make install PREFIX=$HOME/.local` works without root.

</details>

BSD 3-Clause.
