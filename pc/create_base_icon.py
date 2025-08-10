#!/usr/bin/env python3
"""
Create a base battery icon template that battmon.py can use
"""
import cairo
from gi.repository import GdkPixbuf
import os

def create_base_battery_icon():
    """Create a base battery icon template (outline only)"""
    # Create a 24x24 surface for the icon
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
    ctx = cairo.Context(surface)
    
    # Set background to transparent
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    
    # Draw battery outline (just the shape, no fill)
    battery_x, battery_y = 2, 8
    battery_width, battery_height = 18, 8
    
    # Draw battery outline
    ctx.set_source_rgba(0.0, 0.0, 0.0, 0.8)  # Semi-transparent black outline
    ctx.set_line_width(2)
    ctx.rectangle(battery_x, battery_y, battery_width, battery_height)
    ctx.stroke()
    
    # Draw battery terminal (positive end)
    terminal_x = battery_x + battery_width
    terminal_y = battery_y + 2
    terminal_width, terminal_height = 2, 4
    
    ctx.set_source_rgba(0.0, 0.0, 0.0, 0.8)  # Semi-transparent black terminal
    ctx.rectangle(terminal_x, terminal_y, terminal_width, terminal_height)
    ctx.fill()
    
    # Save as PNG
    surface.write_to_png("battery_base.png")
    print("Created battery_base.png - a base battery icon template")
    
    return surface

def create_charging_indicator_template():
    """Create a charging indicator template"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
    ctx = cairo.Context(surface)
    
    # Set background to transparent
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    
    # Draw lightning bolt
    ctx.set_source_rgba(1.0, 1.0, 0.0, 0.9)  # Bright yellow lightning
    ctx.set_line_width(1)
    
    # Lightning bolt shape
    ctx.move_to(10, 4)   # Start higher up
    ctx.line_to(14, 7)   # Down to right
    ctx.line_to(12, 7)   # Left point
    ctx.line_to(16, 10)  # Down to far right
    ctx.line_to(12, 7)   # Back to center
    ctx.line_to(14, 7)   # Right point
    ctx.close_path()
    ctx.fill()
    
    # Add a white outline to make it stand out more
    ctx.move_to(10, 4)
    ctx.line_to(14, 7)
    ctx.line_to(12, 7)
    ctx.line_to(16, 10)
    ctx.line_to(12, 7)
    ctx.line_to(14, 7)
    ctx.close_path()
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)  # White outline
    ctx.set_line_width(2)
    ctx.stroke()
    
    # Save as PNG
    surface.write_to_png("charging_indicator.png")
    print("Created charging_indicator.png - a charging indicator template")
    
    return surface

if __name__ == "__main__":
    import gi
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
    
    create_base_battery_icon()
    create_charging_indicator_template()
    print("\nBase icon templates created!")
    print("You can now edit battery_base.png and charging_indicator.png with any image editor.")
    print("Then update battmon.py to use these templates.")
