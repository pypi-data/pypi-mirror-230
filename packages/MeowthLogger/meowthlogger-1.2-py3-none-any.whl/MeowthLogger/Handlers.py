from logging import LogRecord
import logging.handlers
import time
import os
import colorama

_MIDNIGHT = 3600
DEBUG_DELTA = 0
LOGS_PATH = "Logs"

def prepareHourToStr(hour: int) -> str:
    if hour >= 24 or hour < 0:
        raise ValueError("Hour can be more then 0 and less then 24.")
    
    if (hour <= 9):
        return f"0{hour}"

    return f"{hour}"

def prepareNextHour(current_hour: int) -> (int, int):
    
    if current_hour >= 24 or current_hour < 0:
        raise ValueError("Hour can be more then 0 and less then 24.")
    next_hour = current_hour + 1
    if next_hour == 24:
        next_hour = 0

    return next_hour

def preparePreviousHour(current_hour: int) -> (int, int):
    
    if current_hour >= 24 or current_hour < 0:
        raise ValueError("Hour can be more then 0 and less then 24.")
    previous_hour = current_hour - 1
    if previous_hour == -1:
        previous_hour = 23
    return previous_hour

def prepareLogFileName(current_hour: int) -> str:
    previous_hour = preparePreviousHour(current_hour)

    return f"{prepareHourToStr(previous_hour)}.00-{prepareHourToStr(current_hour)}.00" + ".log" 

class CustomHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, *args, **kwargs):
        filename = os.path.join(LOGS_PATH, filename)

        if not os.path.exists(LOGS_PATH):
            os.mkdir(LOGS_PATH)
        super().__init__(filename, *args, **kwargs)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())

        Meowth_DT = time.localtime(currentTime)
        new_folder_name = f"{Meowth_DT.tm_year}-{Meowth_DT.tm_mon}-{Meowth_DT.tm_mday}"

        new_folder_name = os.path.join(LOGS_PATH, new_folder_name)

        if not os.path.exists(new_folder_name):
            os.mkdir(new_folder_name)
        
        new_filename = prepareLogFileName(Meowth_DT.tm_hour)
        new_filename = os.path.join(new_folder_name, new_filename)
        
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        dfn = self.rotation_filename(new_filename)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        
        if not self.delay:
            self.stream = self._open()
            
        
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

    def computeRollover(self, currentTime: int) -> int:
        result = currentTime + self.interval
        t = time.localtime(currentTime)

        currentMinute = t[4]
        currentSecond = t[5]

        rotate_ts = _MIDNIGHT
        r = rotate_ts - (currentMinute * 60 + currentSecond)
        
        if r < 0:
            r += _MIDNIGHT
        
        r = r - DEBUG_DELTA

        result = currentTime + r
        return result

    def shouldRollover(self, record):
        t = int(time.time())
        if t >= self.rolloverAt:
            if os.path.exists(self.baseFilename) and not os.path.isfile(self.baseFilename):
                self.rolloverAt = self.computeRollover(t)
                return False
            return True
        return False