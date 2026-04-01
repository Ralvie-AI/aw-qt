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
from sd_main.keychain_script import clear_keys
from sd_main.manager import Manager
from .config import AwQtSettings
from .sd_desktop.main import run_application
from sd_main.sd_desktop.monitor import start_exe, is_process_running
from sd_main.sd_desktop.util import check_server_status, credentials, retrieve_settings
from sd_main.sd_desktop.const import VERSION_DISPLAY, REMOTE_HOST, REMOTE_PROTOCOL


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

        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-main started'", shell=True)

        setup_logging("sd-main", log_file=True)
        logger.info("Started sd-main...")
        logger.info(f"VERSION => {VERSION_DISPLAY}")
        logger.info(f"REMOTE_HOST => {REMOTE_HOST}")
        logger.info(f"REMOTE_PROTOCOL => {REMOTE_PROTOCOL}")
        logger.info(f"env => {os.environ}")

        if platform.system() == "Darwin":
            subprocess.call("syslog -s 'sd-main successfully started logging'", shell=True)

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
            creds = credentials()
            results = retrieve_settings()
            process_running, afk_pid =  is_process_running("sd-watcher-afk")
            logger.info(f"results check_sd_watcher {results}")

            if not creds is None and creds.get("Authenticated"):
                logger.info(f"starting sd-watcher-window on check box")
                start_exe("sd-watcher-window")

            if not creds is None and creds.get("Authenticated") and not process_running and results.get('idle_time'):
                logger.info(f"starting sd-watcher-afk on check box")
                start_exe("sd-watcher-afk")
            

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
