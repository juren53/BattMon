# Running `battery_popup.py` on Linux (LMDE 6 / Debian-based)

This guide shows how to run the battery popup on Linux. It uses:
- Python 3
- PyQt6 (GUI)
- psutil (battery info)

The script is cross‑platform and should work on LMDE 6. Behavior of "always on top" and window placement can vary slightly by desktop environment and window manager.

## 1) Install dependencies

Option A: System packages (LMDE/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-psutil python3-pyqt6
```

Option B: Virtual environment (recommended if you prefer isolation)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install PyQt6 psutil
```

## 2) Verify psutil sees your battery (optional)

On some systems or in VMs/containers, battery info may be unavailable. Check quickly:

```bash
python3 -c "import psutil; print(psutil.sensors_battery())"
```

- If you see something like `sbattery(percent=..., secsleft=..., power_plugged=...)`, you’re good.
- If it prints `None`, psutil can’t find ACPI battery info on this system (common on desktops/VMs or unsupported hardware). The popup will still run but will show a default value.

## 3) Run the popup

From the repository root (or from `pc` folder):

One‑shot (single popup) for quick testing:

```bash
python3 pc/battery_popup.py --one --lifetime 10
```

Three‑popup sequence (10 seconds apart, exits after 3rd closes):

```bash
python3 pc/battery_popup.py
```

### Command‑line flags
- `--one` — show exactly one popup and exit when it closes
- `--lifetime <seconds>` — auto‑close time for popups (default 10)

## 4) What to expect
- Window appears near the bottom‑right of the primary monitor
- Large percentage is centered; click anywhere to close
- Status line shows:
  - "AC Power Connected" (default color)
  - "Running on Battery" (red)
- Always‑on‑top is requested; some desktop environments may not strictly enforce it

## 5) Wayland/X11 tips
If you’re on Wayland and encounter issues launching Qt apps, try forcing X11 for the session:

```bash
QT_QPA_PLATFORM=xcb python3 pc/battery_popup.py --one --lifetime 10
```

## 6) Fonts
The script uses a Linux‑friendly font stack:

```
system-ui, "Noto Sans", Ubuntu, Cantarell, "Segoe UI", sans-serif
```

Your desktop will pick the first available font. No extra font packages are required on LMDE 6.

## 7) Troubleshooting
- psutil shows `None` on a laptop:
  - Ensure the system exposes `/sys/class/power_supply/BAT*` and ACPI is enabled.
  - Running inside certain VMs/containers may hide battery info.
- The window appears on a different monitor:
  - The script currently targets the primary screen. We can add a flag to choose a screen if needed.
- The popup appears behind other windows:
  - Always‑on‑top is requested, but some DEs may override. Check your window manager rules.

## 8) Minimal usage recap

```bash
# System packages
sudo apt update && sudo apt install -y python3 python3-pip python3-psutil python3-pyqt6

# Single popup test
python3 pc/battery_popup.py --one --lifetime 10

# Full 3‑popup run
python3 pc/battery_popup.py
```

If you want optional Linux fallbacks for battery (e.g., `upower` or `acpi`) when `psutil` returns `None`, we can add them—just ask.

