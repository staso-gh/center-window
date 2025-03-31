import threading
import winreg
import keyboard
import pygetwindow as gw
from PIL import Image
from pystray import Icon, MenuItem, Menu
from screeninfo import get_monitors

# Default hotkey combination
default_hotkey = 'ctrl+alt+shift'

# Function to load hotkey from config file
def load_hotkey():
    try:
        with open('hotkey.cfg', 'r') as file:
            for line in file:
                if line.startswith('hotkey ='):
                    return line.split('=')[1].strip().strip("'")
    except Exception:
        pass
    return default_hotkey

# Load hotkey from config file
hotkey = load_hotkey()

# Flag to control the hotkey listener thread
stop_hotkey_listener = threading.Event()

# Function to center the active window
def center_window():
    active_window = gw.getActiveWindow()
    if active_window is None:
        return

    for monitor in get_monitors():
        left_corner = monitor.x <= active_window.topleft.x < (monitor.width + monitor.x)
        right_corner = monitor.x <= active_window.topright.x < (monitor.width + monitor.x)
        if left_corner or (not left_corner and right_corner):
            width = 1920 if monitor.width >= 1920 else monitor.width - 300
            active_window.resizeTo(width, monitor.height)
            x = int(monitor.width + monitor.x - width)
            active_window.moveTo(int(x - ((x - monitor.x) / 2)), int(monitor.y))
            break

# Function to listen for hotkeys
def listen_for_hotkeys():
    keyboard.add_hotkey(hotkey, center_window)
    stop_hotkey_listener.wait()

# Function to check if Windows is in dark mode
def is_dark_mode():
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

# Function to create and run the system tray icon
def setup_tray_icon():
    theme = 'dark' if is_dark_mode() else 'light'
    image = Image.open(f'resize_{theme}.ico')
    menu = Menu(MenuItem('Exit', on_quit))
    icon = Icon('WindowManager', image, menu=menu)
    icon.run()

# Function to handle the "Exit" action from the tray icon menu
def on_quit(icon, item):
    stop_hotkey_listener.set()
    icon.stop()

# Main function
def main():
    # Start the hotkey listener in a separate thread
    hotkey_thread = threading.Thread(target=listen_for_hotkeys)
    hotkey_thread.start()

    setup_tray_icon()

    # Wait for the hotkey listener thread to finish
    hotkey_thread.join()

if __name__ == "__main__":
    main()
