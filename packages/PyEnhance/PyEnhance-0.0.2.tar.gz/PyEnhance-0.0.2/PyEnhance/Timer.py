import time
import threading
from Stamps import *

def TimeFormat(Counter=None):

    TestCounter = Counter[0]
    TestCounter = str(TestCounter)

    Counter = Counter[0] / 60
    Counter = str(Counter)
    Counter = Counter[:5]
    DotIndex = Counter.index('.')
    #print(f"Counter: {Counter}")
    #print(f"Dot Index: {DotIndex}")
    if DotIndex == 2:
        #print("DotIndex: 2")
        OutputMin = f"{Counter[:DotIndex]}"
        OutputSec = f"{Counter[DotIndex + 1:]}"
        if OutputMin >= '60':
            #print("Over 60")
            OutputMin = int(OutputMin)
            OutputHours = (int(OutputMin / 60))
            OutputMin = (OutputMin - (int(OutputMin / 60) * 60))
            print(f"{Stamp.Output} {Stamp.Output} {OutputHours}:{OutputMin}:{OutputSec}")
        else:
            OutputMin = f"{Counter[:DotIndex]}"
            OutputSec = f"{Counter[DotIndex + 1:]}"
            OutputMin = int(OutputMin)
            OutputSec = int(OutputSec)
            OutputMin = (OutputMin + (int(OutputSec / 60)))
            OutputSec = (OutputSec - (int(OutputSec / 60) * 60))
            if len(str(OutputSec)) == 1:
                OutputSec = f"{OutputSec}"
            print(f"{Stamp.Output} Time Elapsed: {OutputMin}:{OutputSec}")
    if DotIndex == 3 or 4:
        #print("DotIndex: 3")
        OutputMin = f"{Counter[:DotIndex]}"
        OutputSec = f"{Counter[DotIndex + 1:]}"
        OutputMin = int(OutputMin)
        if OutputMin >= 60:
            OutputMin = int(OutputMin)
            OutputHours = (int(OutputMin / 60))
            OutputMin = (OutputMin - (int(OutputMin / 60) * 60))
            if len(OutputSec) == 1:
                OutputSec = f"0{OutputSec}"
            print(f"{Stamp.Output} Time Elapsed: {OutputHours}:{OutputMin}:{OutputSec}")
            print(f"{Stamp.Output} Time Elapsed: {OutputHours} Hours {OutputMin} Minutes {OutputSec} Seconds")
    if len(TestCounter) == 1:
        #print("Len: 1")
        print(f"{Stamp.Output} Time Elapsed: {TestCounter} seconds")
    if len(TestCounter) == 2:
        #print("Len: 2")
        print(f"{Stamp.Output} Time Elapsed: {TestCounter} seconds")
    if len(TestCounter) == 3:
        #print("Len: 3")
        OutputMin = f"{Counter[:DotIndex]}"
        OutputSec = f"{Counter[DotIndex + 1:]}"
        OutputMin = int(OutputMin)
        OutputSec = int(OutputSec)
        print(f"min: {OutputMin}")
        print(f"Sec: {OutputSec}")
        OutputMin = (OutputMin + (int(OutputSec / 60)))
        OutputSec = (OutputSec - (int(OutputSec / 60) * 60))
        if len(str(OutputSec)) == 1:
            OutputSec = f"0{OutputSec}"
        print(f"{Stamp.Output} Time Elapsed: {OutputMin}:{OutputSec}")

class timer:
    def __init__(self):
        self.stop_flag = True
        self.thread = None
        self.counter = 0
    def counterlist(self):
        return self.counterlist

    def _run(self):

        while not self.stop_flag:
            time.sleep(1)
            self.counter += 1

    def start(self):

        if self.thread is None or not self.start:
            self.stop_flag = False
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
            print(f"{Stamp.Info} Timer Started")
        else:
            print(f"{Stamp.Error} Timer already running")

    def stop(self):

        if self.thread and self.thread.is_alive():
            self.stop_flag = True
            self.thread.join()
            print(f"{Stamp.Info} Timer Stopped")
            global Counter
            Counter = self.counter
            self.counterlist = []

            if self.stop_flag is True:

                self.counterlist.append(self.counter)
                Counter = self.counterlist

                TimeFormat(Counter)

        else:
            print(f"{Stamp.Error} Timer not running")

timer = timer()





