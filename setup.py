from setuptools import setup
APP = ['auto_buy_ui.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'packages': ['pyautogui', 'pynput', 'tkinter', 'threading', 'json', 'os', 'time']}
setup(app=APP, data_files=DATA_FILES, options={'py2app': OPTIONS}, setup_requires=['py2app'])
