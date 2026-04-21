import os
import sys
import logging
import subprocess
import platform
import signal
import threading
from datetime import datetime
from time import sleep

from sd_core.log import setup_logging
from sd_core.util import get_running_path, start_exe
from sd_core.os_util import is_windows
from sd_qt.keychain_script import clear_keys
# from sd_qt.manager import Manager
# from .config import AwQtSettings
from .sd_desktop.main import run_application
from sd_qt.sd_desktop.const import VERSION_DISPLAY
from sd_qt.sd_desktop.util import check_server_status

logger = logging.getLogger(__name__)

# Wait for the server to become available
def wait_until_server_is_up():
    for _ in range(60):
        try:
            # logger.info(f"check_server_status() {check_server_status()}")
            if check_server_status() == False:
                now = datetime.now()
                logger.info(f"check_server_status() time {now}")
                sleep(1)
            else:
                return True
        except:
            sleep(1)
            
    return False


def main() -> None:
    """
    The main function of the application.
    """
    try:        
        setup_logging("sd-qt", log_file=True)
        clear_keys()
        if is_windows():
            # if get_window_version() == 10:
            #     os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --disable-webgl'

            if getattr(sys, 'frozen', False):
                running_path = get_running_path()
                sd_server_exe = os.path.join(running_path, "sd-server.exe")
                threading.Thread(target=start_exe, args=(sd_server_exe,), daemon=True).start()
                logger.info("starting sd-server")

                logger.info(f"running path {running_path}")
                frozen_path = os.path.join(running_path, "PySide6")
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
        
        #config = AwQtSettings()
        # manager = Manager()        
        # manager.autostart(["sd-server"])

        if wait_until_server_is_up():
            run_application()
        else:
            logger.info(f"server not running..... ")

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
