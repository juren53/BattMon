#!/bin/bash
# Setup script for BattMon custom icons

echo "BattMon Custom Icon Setup"
echo "========================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

echo "✓ Python 3 found"

# Check if required Python modules are available
python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('GdkPixbuf', '2.0')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Required GTK/GdkPixbuf modules not available"
    echo "   Try: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    exit 1
fi

echo "✓ Required Python modules found"

# Create base icon templates if they don't exist
if [ ! -f "battery_base.png" ] || [ ! -f "charging_indicator.png" ]; then
    echo "🔧 Creating base icon templates..."
    python3 create_base_icon.py
    if [ $? -eq 0 ]; then
        echo "✓ Base icon templates created"
    else
        echo "❌ Failed to create base icon templates"
        exit 1
    fi
else
    echo "✓ Icon templates already exist"
fi

# Test the custom icon system
echo "🧪 Testing custom icon system..."
python3 test_custom_icons.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Custom icon system test passed"
else
    echo "❌ Custom icon system test failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "1. Edit your icons:"
echo "   • battery_base.png - The battery shape/outline"
echo "   • charging_indicator.png - The charging symbol"
echo ""
echo "2. Use any image editor you like:"
echo "   • GIMP: gimp battery_base.png"
echo "   • Inkscape: inkscape battery_base.png" 
echo "   • Or any other editor that supports PNG"
echo ""
echo "3. Run BattMon to see your custom icons:"
echo "   • python3 battmon.py"
echo ""
echo "4. View the test result:"
echo "   • test_result.png shows how your icons look combined"
echo ""
echo "📖 See CUSTOM_ICONS.md for detailed documentation"
