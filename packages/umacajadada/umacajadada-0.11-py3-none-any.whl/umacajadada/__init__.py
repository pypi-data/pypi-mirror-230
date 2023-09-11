import asyncio
import os
import sys
import traceback
from time import sleep
import kthread


def _start_as_tread(file, mode, action, stoptrigger, encoding, errors):
    t = kthread.KThread(
        target=_read_file_async,
        kwargs={
            "file": file,
            "mode": mode,
            "action": action,
            "stoptrigger": stoptrigger,
            "encoding": encoding,
            "errors": errors,
        },
    )
    t.daemon = True
    t.start()
    return t


def pfehler():
    etype, value, tb = sys.exc_info()
    traceback.print_exception(etype, value, tb)


def _read_file_async(
    file,
    mode="r",
    action=lambda line: sys.stderr.write((str(line) + "\n")),
    stoptrigger: list | tuple = (False,),
    encoding: str = "utf-8",
    errors: str = "backslashreplace",
):
    while not os.path.exists(file):
        sleep(0.005)

    async def start_reading():
        async def rline(_file):
            _file.seek(0, 2)
            while not stoptrigger[-1]:
                line = _file.readline()
                if not line:
                    await asyncio.sleep(0.01)
                    continue
                yield line

        if "b" in mode:
            with open(file, mode) as f:
                reader_generator = rline(f)

                while not stoptrigger[-1]:
                    line = await anext(reader_generator)
                    action(line)
        else:
            with open(file, mode, encoding=encoding, errors=errors) as f:
                reader_generator = rline(f)

                while not stoptrigger[-1]:
                    line = await anext(reader_generator)
                    action(line)

    try:
        return asyncio.run(start_reading())
    except Exception:
        pfehler()


def read_async(
    file: str,
    asthread: bool = True,
    mode: str = "r",
    action=lambda line: sys.stderr.write((str(line) + "\n")),
    stoptrigger: list | tuple = (False,),
    encoding: str = "utf-8",
    errors: str = "backslashreplace",
):
    """
    Read a file asynchronously and process its content.

    Args:
        file (str): The path to the file to be read.
        asthread (bool, optional): If True, the function will start as a thread. Default is True.
        mode (str, optional): The mode in which the file is opened. Default is 'r' (read mode).
        action (function, optional): A function to be applied to each line of the file. Default is to write the line to stderr.
        stoptrigger (list | tuple, optional): A list or tuple (preferably a list) that triggers the function to stop reading when its last element is True. Default is [False].
        encoding (str, optional): The character encoding of the file. Default is 'utf-8'.
        errors (str, optional): How to handle encoding errors. Default is 'backslashreplace'.

    Returns:
        kthread.KThread or None: If as_thread is True, it returns a KThread object. Otherwise, it returns None.

    The advantage of this function is that it allows for real-time processing of the file while it is being written by another process.
    This is particularly useful in scenarios where the file is continuously updated, and the updates need to be processed immediately, such as in log monitoring or real-time data analysis.

    Example usage:
        from threading import Timer
        from time import time
        newfile = f'c:\\testfilex{str(time()).replace(".","_")}.txt'
        stoptrigger = [False,]
        t = read_async(
            file=newfile,
            as_thread=True,
            mode="r",
            action=lambda line: sys.stderr.write((str(line) + "\n")),
            stoptrigger=stoptrigger,
        )
        Timer(5, lambda: stoptrigger.append(True)).start() # Stops after 5 seconds and doesn't print anymore, but os.system goes on.
        os.system("ping 8.8.8.8 -n 10 > " + newfile + "")
    """
    if not asthread:
        return _read_file_async(
            file,
            mode=mode,
            action=action,
            stoptrigger=stoptrigger,
            encoding=encoding,
            errors=errors,
        )
    else:
        return _start_as_tread(file, mode, action, stoptrigger, encoding, errors)
