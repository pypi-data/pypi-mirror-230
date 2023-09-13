from time import ctime

from CyberGear import __version__


def run():
    cur_time = ctime()
    text = f"""
    # CyberGear
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
