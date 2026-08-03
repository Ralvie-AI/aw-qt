from pathlib import Path
import os

from setuptools import setup, Extension
from Cython.Build import cythonize

BASE = Path(__file__).resolve().parent
os.chdir(BASE)

extensions = [
    Extension("keychain_script", ["keychain_script.py"]),
    Extension("main", ["main.py"]),
    Extension("util", ["util.py"]),
    Extension("manager", ["manager.py"]),

    Extension("sd_desktop.const", ["sd_desktop/const.py"]),
    Extension("sd_desktop.dashboard", ["sd_desktop/dashboard.py"]),
    Extension("sd_desktop.network_client", ["sd_desktop/network_client.py"]),
    Extension("sd_desktop.toggleSwitch", ["sd_desktop/toggleSwitch.py"]),
    Extension("sd_desktop.widget", ["sd_desktop/widget.py"]),
    Extension("sd_desktop.language", ["sd_desktop/language.py"]),
    Extension("sd_desktop.main", ["sd_desktop/main.py"]),
    Extension("sd_desktop.onboard", ["sd_desktop/onboard.py"]),
    Extension("sd_desktop.signin", ["sd_desktop/signin.py"]),
    Extension("sd_desktop.util", ["sd_desktop/util.py"]),
    Extension("sd_desktop.worker", ["sd_desktop/worker.py"]),
    
]


setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",           
        },
        
    )
)