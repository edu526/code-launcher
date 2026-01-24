#!/usr/bin/env python3
"""
VSCode Project Launcher - Entry Point
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
import os
import fcntl
import subprocess
import logging

# Importar módulos locales
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.core.config import LOCK_FILE, CONFIG_DIR


# Configurar logging
LOG_FILE = os.path.join(CONFIG_DIR, "vscode-launcher.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application"""
    logger.info("Starting VSCode Project Launcher")

    # Crear directorio de configuración si no existe
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)

    # Intentar obtener el lock
    try:
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Lock file acquired successfully")
    except BlockingIOError:
        logger.warning("Another instance is already running")
        # Ya hay una instancia corriendo, traerla al frente
        try:
            subprocess.run(
                ['wmctrl', '-a', 'VSCode Project Launcher'],
                check=False,
                stderr=subprocess.DEVNULL
            )
            logger.info("Brought existing window to front")
        except FileNotFoundError:
            logger.error("wmctrl not installed")
            print("wmctrl no está instalado. Instala wmctrl con 'sudo apt install wmctrl' "
                  "para activar la ventana existente.")
        lock_file.close()
        return
    except Exception as e:
        logger.error(f"Error creating lock file: {e}")
        print(f"Error al crear el lock file: {e}")
        return

    # Crear ventana
    from src.ui.window import FinderStyleWindow
    window = FinderStyleWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    logger.info("Main window created and shown")

    try:
        Gtk.main()
    finally:
        logger.info("Application shutting down")
        lock_file.close()
        try:
            os.unlink(LOCK_FILE)
            logger.info("Lock file removed")
        except:
            pass


if __name__ == "__main__":
    main()
