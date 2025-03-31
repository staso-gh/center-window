import sys
import winreg
import keyboard
import pygetwindow as gw

from PIL import Image
from pystray import Icon, MenuItem, Menu
from screeninfo import get_monitors


# Hotkey combination to re-center the active window
hotkey = 'ctrl+alt+shift+o'


# Invoke the application exit function when selecting the icon tray menu
def on_quit(icon):
    icon.stop()
    sys.exit()


# Check if the theme of the Windows system, default to light mode if catching an exception
def is_dark_mode():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
        return value == 0
    except Exception as e:
        return False


# Create the icon tray, load the appropriate image for the theme and add the context menu
def setup_tray_icon():
    theme = 'dark' if is_dark_mode() else 'light'
    image = Image.open(f'resize_{theme}.ico')
    menu = Menu(MenuItem('Exit', on_quit))
    icon = Icon('test', image, menu=menu)
    icon.run()


# Function for centering the actively selected window
# The window will be centered on the monitor it finds itself in
# First, the program will look at the top left corner dimensions of the program
# If the top left corner dimensions are outside the bounds of all monitors, try with the top right
def center_window():
    active_window = gw.getActiveWindow()
    if active_window is None:
        return

    for monitor in get_monitors():
        leftCorner = monitor.x <= active_window.topleft.x < (monitor.width + monitor.x)
        rightCorner = monitor.x <= active_window.topright.x < (monitor.width + monitor.x)
        if leftCorner or (not leftCorner and rightCorner):
            width = 1920 if monitor.width >= 1920 else monitor.width - 300
            active_window.resizeTo(width, monitor.height)
            x = int(monitor.width + monitor.x - width)
            active_window.moveTo(int(x - ((x - monitor.x) / 2)), int(monitor.y))
            break

# Add the listening event for the hotkey and appoint the function to be triggered
def listen_for_hotkeys():
    keyboard.add_hotkey(hotkey, center_window)
    # Block forever, waiting for hotkeys
    keyboard.wait()


def main():
    # Start the tray icon in a separate thread
    import threading
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.daemon = True
    tray_thread.start()

    # Start listening for hotkeys
    listen_for_hotkeys()

if __name__ == "__main__":
    main()
