# Custom Icons for BattMon

BattMon now supports using custom icon templates that you can create and modify to customize the appearance of your battery monitor.

## How It Works

BattMon can use two types of custom icons:

1. **Base Battery Icon** (`battery_base.png`) - The outline/shape of the battery
2. **Charging Indicator** (`charging_indicator.png`) - The lightning bolt overlay when charging

If these files don't exist, BattMon falls back to generating icons programmatically (the original behavior).

## Quick Start

1. **Generate base templates:**
   ```bash
   python3 create_base_icon.py
   ```

2. **Edit the icons** with any image editor (GIMP, Inkscape, etc.)

3. **Run BattMon** - it will automatically detect and use your custom icons

## Icon Specifications

### Battery Base Icon (`battery_base.png`)
- **Size:** 24x24 pixels
- **Format:** PNG with transparency support
- **Content:** Should contain the battery outline/shape only
- **Battery Fill Area:** Coordinates (2,8) to (20,16) - this area will be filled with color based on battery level

### Charging Indicator (`charging_indicator.png`)
- **Size:** 24x24 pixels
- **Format:** PNG with transparency support  
- **Content:** Lightning bolt or other charging symbol
- **Note:** This will be overlaid on top of the battery icon when charging

## Dynamic Features

Even with custom base icons, BattMon maintains these dynamic features:

- **Battery Level Fill:** The battery area is filled with color based on percentage
  - Green: >75%
  - Orange: 25-75%
  - Red: <25%

- **Percentage Text:** Bold white text with black outline showing the exact percentage

- **Charging Overlay:** Custom or generated lightning bolt when charging

## Example Workflow

1. **Create templates:**
   ```bash
   python3 create_base_icon.py
   ```

2. **Edit with image editor:**
   - Open `battery_base.png` in GIMP/Photoshop/etc.
   - Modify the battery shape, add decorations, change colors
   - Keep the inner area (2,8 to 20,16) relatively clear for the fill
   - Save as PNG with transparency

3. **Test:**
   ```bash
   python3 battmon.py
   ```

## Advanced Customization

### Multiple Battery Designs
You can create different base icons for different situations by modifying the `base_icon_path` in the code:

```python
# In create_battery_icon_with_text():
if percentage > 75:
    base_icon_path = "battery_base_green.png"
elif percentage > 25:
    base_icon_path = "battery_base_orange.png"
else:
    base_icon_path = "battery_base_red.png"
```

### Custom Charging Indicators
Create multiple charging indicators:
- `charging_indicator_slow.png` for slow charging
- `charging_indicator_fast.png` for fast charging
- `charging_indicator_full.png` for when battery is full but plugged in

## Troubleshooting

- **Icons not loading:** Check file permissions and make sure PNG files are valid
- **Icons look wrong:** Verify the battery fill area coordinates match your design
- **Performance issues:** Keep icon files small (24x24 pixels, optimized PNG)

## Fallback Behavior

If custom icons can't be loaded, BattMon automatically falls back to:
1. Programmatically generated icons (original behavior)
2. System theme icons (as configured in ~/.battmon)
3. Stock GTK warning icon (last resort)

This ensures BattMon always works, even if custom icons are corrupted or missing.
