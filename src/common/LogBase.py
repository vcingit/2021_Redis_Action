import time
import logging
import os

LOG_PATH = "log"

# init log conf
def InitLog():
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    logFileName = time.strftime("local_%Y-%m-%d"), time.localtime(time.time())
    #logFileName = time.strftime("%Y-%m-%d_%H%M"), time.localtime(time.time())
    logFilePath = LOG_PATH + "/" + logFileName[0] + ".log"
    logLevel = logging.DEBUG
    logging.basicConfig(filename=logFilePath, format="[%(asctime)s][%(levelname)s]|%(filename)s, line %(lineno)d|%(message)s", level=logLevel)
