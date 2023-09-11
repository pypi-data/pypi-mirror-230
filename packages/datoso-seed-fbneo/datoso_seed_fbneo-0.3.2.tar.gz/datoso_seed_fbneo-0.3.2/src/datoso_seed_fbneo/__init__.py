"""
__init__.py
"""
__all__ = ["__version__", "__author__", "__description__"]
__version__ = "0.3.2"
__author__ = "Lacides Miranda"
__description__ = "Emulator for Arcade Games & Select Consoles."
__preffix__ = "fbneo"

from datoso.configuration import config
if not config.has_section('FBNEO'):
    config['FBNEO'] = {
        'FetchFull': True,
        'FetchLight': False,
    }
