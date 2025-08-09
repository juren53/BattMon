#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Pango, PangoCairo
import cairo
import subprocess
import os
import sys
import configparser
import datetime

ACPI_CMD = 'acpi'
TIMEOUT = 2
VERSION = '0.1'
config = False
config_path = os.path.expanduser('~/.battmon')

try:
    subprocess.check_output(ACPI_CMD)
except OSError:
    print("It seems like you have no acpi utility installed or it's not available through your PATH.")
    sys.exit(2)

try:
    with open(config_path) as f:
        config = configparser.ConfigParser({'command': 'None', 'icon': 'battery-full', 'charge_icon': 'battery-full-charging', 'percent': '100'})
        config.read(config_path)
        b = {}
        for key in config._sections:
            if key in ('empty', 'caution', 'low', 'fair', 'good', 'full'):
                b[key] = config._sections[key]
                b[key]['percent'] = int(b[key]['percent'])
except IOError:
    print("There must be a config file (~/.battmon) setup.  See the README.md for documentation.")
    sys.exit(2)

if config:
    class MainApp:
        def __init__(self):
            self.last_icon = {}
            self.icon = Gtk.StatusIcon()
            self.icon.set_visible(True)
            self.icon.connect('activate', self.left_click)
            self.icon.connect('popup-menu', self.right_click)
            self.update_icon()
            GLib.timeout_add_seconds(TIMEOUT, self.update_icon)
            print("BattMon started - system tray icon should be visible")
            print("Left-click to run command, Right-click for menu")

        def left_click(self, icon):
            info = self.get_battery_info()
            if config._sections['general']['command'] != 'None':
                os.system(config._sections['general']['command'])
            else:
                # Show detailed battery information
                notify = 'notify-send -i "battery" -t 5000 "Battery Status" "State: {state}\nCharge: {percentage}%{time_info}"'
                time_info = f"\nTime: {info['time']}" if info.get('time') else ""
                os.system(notify.format(
                    state=info['state'], 
                    percentage=info['percentage'],
                    time_info=time_info
                ))
        
        def right_click(self, icon, button, time):
            menu = Gtk.Menu()
            
            # Battery info item
            info = self.get_battery_info()
            info_item = Gtk.MenuItem(label=f"Battery: {info['percentage']}% ({info['state']})")
            info_item.set_sensitive(False)
            menu.append(info_item)
            
            # Separator
            menu.append(Gtk.SeparatorMenuItem())
            
            # About item
            about_item = Gtk.MenuItem(label="About BattMon")
            about_item.connect('activate', self.show_about)
            menu.append(about_item)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect('activate', self.quit_app)
            menu.append(quit_item)
            
            menu.show_all()
            menu.popup(None, None, None, None, button, time)
        
        def show_about(self, widget):
            """Show about dialog with version and update information"""
            try:
                # Get file modification time
                script_path = os.path.abspath(__file__)
                mtime = os.path.getmtime(script_path)
                update_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # Create about dialog
                dialog = Gtk.MessageDialog(
                    parent=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="About BattMon PC"
                )
                
                about_text = f"""BattMon PC - Battery Monitor for Linux

Version: {VERSION}
Last Updated: {update_date}

A modern Python 3 battery monitoring application that displays battery percentage directly in your system tray with a highly readable rectangular battery icon design.

Features:
• Ultra-readable battery percentage display
• Color-coded battery levels (Red/Orange/Green)
• Prominent charging indicator
• Interactive notifications and tooltips
• Lightweight with minimal resource usage

Developed with Python 3 + GTK3
License: GPL v2+"""
                
                dialog.format_secondary_text(about_text)
                dialog.set_title("About BattMon")
                
                # Show dialog and handle response
                response = dialog.run()
                dialog.destroy()
                
            except Exception as e:
                print(f"Error showing about dialog: {e}")
        
        def quit_app(self, widget):
            print("BattMon shutting down...")
            Gtk.main_quit()

        def get_battery_info(self):
            text = subprocess.check_output(ACPI_CMD).decode('utf-8').strip('\n')
            if not 'Battery' in text:
                return {
                    'state': "Unknown",
                    'percentage': 0,
                    'tooltip': ""
                }
            data = text.split(',')
            state = data[0].split(':')[1].strip(' ')
            percentage_str = data[1].strip(' %')
            percentage = int(percentage_str)
            time = '' if state in ('Full', 'Unknown') else data[2].split(' ')[1]
            tooltip = 'Battery is {state}' if state in ('Full', 'Unknown') else 'Battery is {state} ({percentage}%)\n {time} remaining'
            return {
                'state': state,
                'percentage': percentage,
                'tooltip': tooltip.format(state=state, percentage=percentage, time=time),
                'time': time,
            }

        def get_icon(self, state, percentage):
            icon = b['full']
            icon['state'] = 'icon'
            if state == 'Full':
                icon = config._sections['full_adapter']
                icon['state'] = 'icon'
                return icon
            closest_match = 0
            for key in b:
                if percentage >= b[key]['percent'] and b[key]['percent'] > closest_match:
                    closest_match = b[key]['percent']
                    icon = b[key]
                    icon['state'] = 'icon' if state == 'Discharging' else 'charge_icon'
            return icon

        def create_battery_icon_with_text(self, percentage, is_charging=False):
            """Create a custom rectangular battery icon with percentage text"""
            # Create a 24x24 surface for the icon
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
            ctx = cairo.Context(surface)
            
            # Set background to transparent
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)
            
            # Choose background color based on battery level
            if percentage > 75:
                bg_color = (0.2, 0.7, 0.2)  # Green
            elif percentage > 25:
                bg_color = (0.8, 0.6, 0.0)  # Orange
            else:
                bg_color = (0.8, 0.2, 0.2)  # Red
            
            # Draw rectangular battery body
            battery_x, battery_y = 2, 8
            battery_width, battery_height = 18, 8
            
            # Fill battery background with color
            ctx.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], 1.0)
            ctx.rectangle(battery_x, battery_y, battery_width, battery_height)
            ctx.fill()
            
            # Draw battery outline
            ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)  # Black outline
            ctx.set_line_width(2)
            ctx.rectangle(battery_x, battery_y, battery_width, battery_height)
            ctx.stroke()
            
            # Draw battery terminal (positive end)
            terminal_x = battery_x + battery_width
            terminal_y = battery_y + 2
            terminal_width, terminal_height = 2, 4
            
            ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)  # Black terminal
            ctx.rectangle(terminal_x, terminal_y, terminal_width, terminal_height)
            ctx.fill()
            
            # Add charging indicator if charging - make it more visible
            if is_charging:
                # Draw a prominent lightning bolt in the center-top area
                ctx.set_source_rgba(1.0, 1.0, 0.0, 1.0)  # Bright yellow lightning
                ctx.set_line_width(1)
                
                # Larger, more visible lightning bolt
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
                ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)  # White outline
                ctx.set_line_width(2)
                ctx.stroke()
            
            # Prepare large, bold text
            text = f"{percentage}"
            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            
            # Position text in the lower part of the icon
            if percentage == 100:
                ctx.set_font_size(9)
                text_x, text_y = 3, 22
            elif percentage >= 10:
                ctx.set_font_size(11)
                text_x, text_y = 6, 22
            else:
                ctx.set_font_size(13)
                text_x, text_y = 9, 22
            
            # Draw white text with thick black outline for maximum contrast
            ctx.move_to(text_x, text_y)
            ctx.text_path(text)
            
            # Thick black outline
            ctx.set_line_width(3)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)  # Black outline
            ctx.stroke_preserve()
            
            # White text fill
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)  # White text
            ctx.fill()
            
            # Convert cairo surface to GdkPixbuf
            # Write surface to a PNG in memory and load as pixbuf
            import io
            png_buffer = io.BytesIO()
            surface.write_to_png(png_buffer)
            png_buffer.seek(0)
            
            from gi.repository import Gio
            input_stream = Gio.MemoryInputStream.new_from_bytes(
                GLib.Bytes.new(png_buffer.getvalue())
            )
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
            
            return pixbuf
        
        def update_icon(self):
            info = self.get_battery_info()
            percentage = info['percentage']
            is_charging = info['state'] not in ('Discharging', 'Full', 'Unknown')
            
            # Check if battery state changed significantly
            if not hasattr(self, 'last_percentage'):
                self.last_percentage = percentage
                self.last_state = info['state']
                show_message = True
            else:
                # Only show message if percentage changed by 5% or state changed
                percentage_diff = abs(percentage - self.last_percentage)
                state_changed = info['state'] != self.last_state
                show_message = percentage_diff >= 5 or state_changed
                
                if show_message:
                    self.last_percentage = percentage
                    self.last_state = info['state']
            
            try:
                # Create custom icon with percentage
                pixbuf = self.create_battery_icon_with_text(percentage, is_charging)
                self.icon.set_from_pixbuf(pixbuf)
                if show_message:
                    print(f"Battery: {percentage}% {info['state']}")
            except Exception as e:
                print(f"Failed to create custom icon: {e}")
                # Fallback to regular icon method
                icon = self.get_icon(info['state'], percentage)
                icon_name = icon[icon['state']]
                try:
                    self.icon.set_from_icon_name(icon_name)
                    if show_message:
                        print(f"Battery: {percentage}% {info['state']} - Using fallback icon: {icon_name}")
                except:
                    self.icon.set_from_stock(Gtk.STOCK_DIALOG_WARNING)
                    print("Using stock warning icon as last resort")
            
            # Set tooltip with battery info
            tooltip = f"Battery: {percentage}% ({info['state']})"
            if info.get('time'):
                tooltip += f"\nTime: {info['time']}"
            self.icon.set_tooltip_text(tooltip)
            return True
      
    if __name__ == "__main__":
        try:
            MainApp()
            Gtk.main()
        except KeyboardInterrupt:
            pass

