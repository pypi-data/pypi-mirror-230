from time import ctime

from hami import __version__


def run():
    cur_time = ctime()
    text = f"""
    # hami
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
