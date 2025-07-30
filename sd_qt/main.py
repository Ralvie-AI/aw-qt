import os
import sys
import logging
import subprocess
import platform
import signal
import threading
from time import sleep

from sd_core.log import setup_logging
from sd_qt.keychain_script import clear_keys
from sd_qt.manager import Manager
from .config import AwQtSettings
from .sd_desktop.main import run_application
from sd_qt.sd_desktop.util import (get_window_version, is_windows)
from sd_qt.sd_desktop.const import VERSION_DISPLAY

logger = logging.getLogger(__name__)


def get_running_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def main() -> None:
    """
    The main function of the application.
    """
    try:
        
        setup_logging("sd-qt", log_file=True)

        if is_windows():
            # if get_window_version() == 10:
            #     os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --disable-webgl'

            if getattr(sys, 'frozen', False):
                logger.info(f"running path {get_running_path()}")
                frozen_path = os.path.join(get_running_path(), "PySide6")
                logger.info(f"running path of QtWebEngineProcess {frozen_path}")
                os.environ['QTWEBENGINEPROCESS_PATH'] = os.path.join(frozen_path, "QtWebEngineProcess.exe")    
                os.environ['QTWEBENGINE_RESOURCES_PATH'] = os.path.join(frozen_path, "resources")  

            os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --disable-webgl'

            logger.info(f"VERSION => {VERSION_DISPLAY}")
            logger.info(f"env => {os.environ}")

        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-qt started'", shell=True)
        
        logger.info("Started sd-qt...")

        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-qt successfully started logging'", shell=True)

        if sys.platform != "win32":
            try:
                os.setpgrp()
            except PermissionError:
                logger.warning("Permission denied when trying to set process group")

        clear_keys()

        config = AwQtSettings()

        manager = Manager()
        
        manager.autostart(["sd-server"])
        run_application()

        if sys.platform == "win32":
            try:
                sleep(threading.TIMEOUT_MAX)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping...")
        else:
            def handle_signal(signum, frame):
                logger.info(f"Signal {signum} received, stopping...")
                manager.stop_all()
                sys.exit(0)

            signal.signal(signal.SIGTERM, handle_signal)
            signal.signal(signal.SIGINT, handle_signal)
            signal.pause()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
