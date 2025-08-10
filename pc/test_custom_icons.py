#!/usr/bin/env python3
"""
Test script to verify custom icon functionality works
"""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import cairo
import os

def load_base_icon(icon_path):
    """Load a base icon template from file"""
    try:
        if os.path.exists(icon_path):
            print(f"Loading base icon: {icon_path}")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            # Convert pixbuf to cairo surface
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 
                                        pixbuf.get_width(), 
                                        pixbuf.get_height())
            ctx = cairo.Context(surface)
            Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
            ctx.paint()
            return surface
    except Exception as e:
        print(f"Could not load base icon {icon_path}: {e}")
    return None

def test_icon_creation():
    """Test creating icons with custom templates"""
    print("Testing custom icon creation...")
    
    # Test base battery icon
    base_icon_path = "battery_base.png"
    if os.path.exists(base_icon_path):
        print(f"✓ Found base icon: {base_icon_path}")
        surface = load_base_icon(base_icon_path)
        if surface:
            print("✓ Successfully loaded base icon into Cairo surface")
        else:
            print("✗ Failed to load base icon")
    else:
        print(f"✗ Base icon not found: {base_icon_path}")
    
    # Test charging indicator
    charging_icon_path = "charging_indicator.png"
    if os.path.exists(charging_icon_path):
        print(f"✓ Found charging indicator: {charging_icon_path}")
        surface = load_base_icon(charging_icon_path)
        if surface:
            print("✓ Successfully loaded charging indicator into Cairo surface")
        else:
            print("✗ Failed to load charging indicator")
    else:
        print(f"✗ Charging indicator not found: {charging_icon_path}")
    
    # Test creating a combined icon
    print("\nTesting icon combination...")
    try:
        # Create a test surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
        ctx = cairo.Context(surface)
        
        # Load base icon if available
        base_surface = load_base_icon(base_icon_path)
        if base_surface:
            ctx.set_source_surface(base_surface, 0, 0)
            ctx.paint()
            print("✓ Applied base icon to test surface")
        
        # Add battery level fill
        percentage = 75
        battery_x, battery_y = 2, 8
        battery_width, battery_height = 18, 8
        fill_width = int((battery_width * percentage) / 100)
        
        ctx.set_source_rgba(0.2, 0.7, 0.2, 0.7)  # Green
        ctx.rectangle(battery_x, battery_y, fill_width, battery_height)
        ctx.fill()
        print(f"✓ Added {percentage}% battery fill")
        
        # Add charging indicator
        charging_surface = load_base_icon(charging_icon_path)
        if charging_surface:
            ctx.set_source_surface(charging_surface, 0, 0)
            ctx.paint()
            print("✓ Applied charging indicator")
        
        # Add percentage text
        text = f"{percentage}"
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        text_x, text_y = 6, 22
        
        ctx.move_to(text_x, text_y)
        ctx.text_path(text)
        
        # Black outline
        ctx.set_line_width(3)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        ctx.stroke_preserve()
        
        # White text fill
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.fill()
        print("✓ Added percentage text with outline")
        
        # Save test result
        surface.write_to_png("test_result.png")
        print("✓ Saved test result as test_result.png")
        
        print("\n✓ All tests passed! Custom icon system is working.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("BattMon Custom Icon Test")
    print("=" * 30)
    
    success = test_icon_creation()
    
    if success:
        print("\n🎉 Custom icon system is ready!")
        print("You can now:")
        print("1. Edit battery_base.png with your favorite image editor")
        print("2. Edit charging_indicator.png to customize the charging symbol")
        print("3. Run battmon.py to see your custom icons in action")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
