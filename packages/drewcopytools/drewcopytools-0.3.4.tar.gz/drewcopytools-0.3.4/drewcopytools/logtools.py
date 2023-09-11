# Copyright 2021 drewCo Software, All Rights Reserved

from drewcopytools.filetools import get_sequential_file_path
import logging
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------------------
# REUSE
def init_logging(logPath_:str = "./log.runlog", level_ = logging.INFO, append:bool = True):
    """
    Initialize the logging system which will write to a file and to the console.
    """
    LOG_PATH = logPath_
    LOG_FORMAT = "%(asctime)s %(name)s:%(levelname)s:%(message)s"

    useMode = 'w'
    if append:
        useMode = 'a'



    # also this:
    # https://pythonhowtoprogram.com/logging-in-python-3-how-to-output-logs-to-file-and-console/
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamformat = logging.Formatter("%(message)s")
    streamHandler.setFormatter(streamformat)


    useHandlers = [ streamHandler ]
    if LOG_PATH is not None:
        fileHandler = logging.FileHandler(filename=LOG_PATH, encoding='utf-8', mode=useMode)
        useHandlers.append(fileHandler)

    # Thanks!  Since the docs give exmaples that dont work:
    # https://stackoverflow.com/questions/10706547/add-encoding-parameter-to-logging-basicconfig
    logging.basicConfig(handlers=useHandlers,
                        format=LOG_FORMAT, 
                        datefmt="%F %A %T",     # TODO: This format sux.  Do something about it later.  UTC+0 would be ideal.
                        level=level_)


# ----------------------------------------------------------------------------------------------------------------------------
# REUSE
def log_exception(ex):
    logging.critical("")
    logging.critical("Unhandled exception was encountered in __main__!")
    
    # Save the exception...
    exDataPath = get_sequential_file_path(Path("./.exception"), "exception", ".txt")
    logging.critical("Exception detail will be saved to: " + str(exDataPath))

    # tex = traceback.TracebackException.from_exception(ex, limit=10, lookup_lines=False, capture_locals=True)
    # sum = tex.stack
    import traceback
    fex = traceback.format_exception(ex.__class__, value=ex, tb=ex.__traceback__, limit=15)

    stackTrace = ''.join(fex)
    logging.critical(stackTrace)

    LINE = "-------------------------------------\n"
    content = LINE
    content += 'EXCEPTION LOG:\n'
    content += LINE + "\n"
    content += "Stack Trace:\n" + LINE
    content += stackTrace
    exDataPath.write_text(content)
