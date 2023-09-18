import sys
import signal
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QDialog
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer
from .ui.config_dialog import ConfigDialog
from .ui.tray_operations import update_tray_icon
from .api.fetch_times import read_config, write_config

ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")

def main():
    app = QApplication(sys.argv)
    
    # Create a system tray icon
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon(ICON_PATH))  # Set the icon for the system tray
    tray.setVisible(True)
    
    # Set the application icon
    app.setWindowIcon(QIcon(ICON_PATH))  

    # Create a context menu for the tray icon
    menu = QMenu()

    # Add a "Settings" option
    settings_action = QAction("Settings")
    settings_action.triggered.connect(show_settings)  # Connect to a function to show settings
    menu.addAction(settings_action)

    # Add an "Exit" option
    exit_action = QAction("Exit")
    exit_action.triggered.connect(app.exit)
    menu.addAction(exit_action)
    
    # Set the context menu for the tray icon
    tray.setContextMenu(menu)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.setQuitOnLastWindowClosed(False)

    # Set a timer to update the tray icon every minute
    timer = QTimer()
    timer.timeout.connect(lambda: update_tray_icon(tray))
    timer.start(60000)  # update every 60 seconds

    # Call update_tray_icon initially to set the first icon
    update_tray_icon(tray)

    sys.exit(app.exec())

def show_settings():
    dialog = ConfigDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        city = dialog.city_input.text()
        write_config({"city": city})

if __name__ == "__main__":
    main()
