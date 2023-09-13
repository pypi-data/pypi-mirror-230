from time import ctime

from hamlib import __version__


def run():
    cur_time = ctime()
    text = f"""
    # hamlib
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
