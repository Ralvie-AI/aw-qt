import os
import sys
import logging
import subprocess
import platform
import signal
import threading
import requests
from time import sleep
from datetime import datetime

from sd_core.log import setup_logging
from sd_qt.keychain_script import clear_keys
from sd_qt.manager import Manager
from .config import AwQtSettings
from .sd_desktop.main import run_application
from sd_qt.sd_desktop.monitor import start_exe
from sd_qt.sd_desktop.util import check_server_status

logger = logging.getLogger(__name__)


# Wait for the server to become available
def wait_until_server_is_up():
    for _ in range(60):
        try:
            logger.info(f"check_server_status() {check_server_status()}")
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
        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-qt started'", shell=True)

        setup_logging("sd-qt", log_file=True)
        logger.info("Started sd-qt...")

        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-qt successfully started logging'", shell=True)

        if sys.platform != "win32":
            try:
                os.setpgrp()
            except PermissionError:
                logger.warning("Permission denied when trying to set process group")

        clear_keys()
        logger.info("before main starting sd-server")
        threading.Thread(target=start_exe, args=("sd-server",), daemon=True).start()
        logger.info("after main starting sd-server")

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
                # manager.stop_all()
                sys.exit(0)

            signal.signal(signal.SIGTERM, handle_signal)
            signal.signal(signal.SIGINT, handle_signal)
            signal.pause()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
