from time import ctime

from pyhami import __version__


def run():
    cur_time = ctime()
    text = f"""
    # pyhami
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
