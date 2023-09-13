from time import ctime

from PyCyberGear import __version__


def run():
    cur_time = ctime()
    text = f"""
    # PyCyberGear
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
