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

ACPI_CMD = 'acpi'
TIMEOUT = 2
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
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect('activate', self.quit_app)
            menu.append(quit_item)
            
            menu.show_all()
            menu.popup(None, None, None, None, button, time)
        
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
            """Create a custom icon with battery percentage text"""
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
            
            # Draw solid colored background circle
            ctx.set_source_rgba(bg_color[0], bg_color[1], bg_color[2], 1.0)
            ctx.arc(12, 12, 11, 0, 2 * 3.14159)  # Circle centered at 12,12 with radius 11
            ctx.fill()
            
            # Draw border around circle
            ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)  # Black border
            ctx.set_line_width(2)
            ctx.arc(12, 12, 11, 0, 2 * 3.14159)
            ctx.stroke()
            
            # Add charging indicator if charging
            if is_charging:
                ctx.set_source_rgba(1.0, 1.0, 0.0, 1.0)  # Yellow lightning
                ctx.set_line_width(2)
                # Simple lightning bolt in top-right
                ctx.move_to(17, 6)
                ctx.line_to(19, 10)
                ctx.line_to(17, 10)
                ctx.line_to(19, 14)
                ctx.line_to(15, 10)
                ctx.line_to(17, 10)
                ctx.close_path()
                ctx.fill()
            
            # Prepare large, bold text
            text = f"{percentage}"
            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            
            # Use much larger font and center the text
            if percentage == 100:
                ctx.set_font_size(11)
                text_x, text_y = 2, 17
            elif percentage >= 10:
                ctx.set_font_size(13)
                text_x, text_y = 5, 17
            else:
                ctx.set_font_size(15)
                text_x, text_y = 8, 18
            
            # Draw white text with thick black outline for maximum contrast
            ctx.move_to(text_x, text_y)
            ctx.text_path(text)
            
            # Thick black outline
            ctx.set_line_width(4)
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

