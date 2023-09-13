from time import ctime

from pyhamlib import __version__


def run():
    cur_time = ctime()
    text = f"""
    # pyhamlib
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
