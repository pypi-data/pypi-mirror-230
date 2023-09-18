import os
import pickle
from utils.log import logger


def load_file_lock():
    def lock(file, flags):
        pass

    def unlock(file):
        pass

    return

    # TODO: pywin install fail
    if os.name == 'nt':
        import win32con, win32file, pywintypes

        LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
        LOCK_SH = 0  # The default value
        LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
        __overlapped = pywintypes.OVERLAPPED()

        def lock(file, flags):
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.LockFileEx(hfile, flags, 0, 0xffff0000, __overlapped)

        def unlock(file):
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)
    elif os.name == 'posix':
        from fcntl import flock, LOCK_UN

        def lock(file, flags):
            flock(file.fileno(), flags)

        def unlock(file):
            flock(file.fileno(), LOCK_UN)
    else:
        raise RuntimeError("File Locker only support NT and Posix platforms!")


load_file_lock()


def store(data, key):
    b = pickle.dumps(data)
    with open(key, "wb") as f:
        f.write(b)
    return

    # TODO: no fcntl
    try:
        f = open(key, "wb")
        fcntl.lockf(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.truncate(file_desc, 0)
        os.write(file_desc, b)
    except IOError as err:
        logger.error(err)
    finally:
        os.close(file_desc)
        logger.info(f"close file {file_desc}")


def get_data(key):
    # TODO: add file read lock
    # file_desc = os.open(key, os.O_RDWR)
    if not os.path.isfile(key):
        return None
    with open(key, "rb") as f:
        return pickle.load(f)
