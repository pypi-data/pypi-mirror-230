from MyOverlay.funcs import myfunctions


def InnitOverlay():
    return myfunctions.StartOverlay()


def settext(text: str, PosX: int, PosY: int, font: str = 'Segoe UI Semibold', size: int = 30, opx: int = 2):
    myfunctions.settext(text, PosX, PosY, font, size, opx)


def KillOverlay():
    myfunctions.KillOverlay()


def StatusOverlay():
    return myfunctions.StatusOverlay()


def GetJobDirectory(JobName: str):
    return myfunctions.GetJobDirectory(JobName)


def GetJob(JobName: str):
    return myfunctions.GetJob(JobName)