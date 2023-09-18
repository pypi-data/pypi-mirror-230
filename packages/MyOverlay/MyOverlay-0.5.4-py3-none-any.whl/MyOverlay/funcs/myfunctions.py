from win32api import GetSystemMetrics
import pygame
import win32api
import win32con
import win32gui
import ctypes
from thefuzz import fuzz

white = (255, 255, 255)
black = (0, 0, 0)
fuchsia = (255, 0, 128)
rec_w = 0
rec_h = 0
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def render(text, font, opx=2):
    global w
    global h
    textsurface = font.render(text, True, white).convert_alpha()
    if w < textsurface.get_width() + 2 * opx:
        w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, False, black).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf


def StartOverlay():
    if not pygame.display.get_active():
        global text
        global textRect
        global screen
        screen_width = GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = GetSystemMetrics(win32con.SM_CYSCREEN)
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
        hwnd = pygame.display.get_wm_info()["window"]
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        style = style & ~WS_EX_APPWINDOW
        style = style | WS_EX_TOOLWINDOW
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        style = style & ~WS_EX_APPWINDOW
        style = style | WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd,
                                                      win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, screen_width, screen_height, 0)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
        screen.fill(fuchsia)
        pygame.display.update()
        return True
    else:
        return False


def settext(text: str, PosX: int, PosY: int, font: str = 'Segoe UI Semibold', size: int = 30, opx: int = 2):
    if pygame.display.get_active():
        global rect
        global rect_w
        global rect_h
        global screen
        global w
        pygame.event.pump()
        font = pygame.font.SysFont(font, size, False)
        screen.fill(fuchsia)  # Transparent background
        lines = str(text).splitlines()
        w = 0
        for i, l in enumerate(lines):
            screen.blit(render(l, font, opx), (PosX // 2, PosY // 2 + size * i))
        try:
            rect
        except NameError:
            rect_w = w
            rect_h = (PosY // 2 + size * i) - PosY // 2 + h
            rect = pygame.Rect(PosX // 2, PosY // 2, rect_w, rect_h)
        pygame.display.update(rect)
        if rect_w != w or rect_h != (PosY // 2 + size * i) - PosY // 2 + h:
            rect_w = w
            rect_h = (PosY // 2 + size * i) - PosY // 2 + h
            rect = pygame.Rect(PosX // 2, PosY // 2, rect_w, rect_h)
            pygame.display.update(rect)


def KillOverlay():
    pygame.display.quit()


def StatusOverlay():
    return pygame.display.get_active()


def GetJob(JobName: str):
    database = ['Airline Pilot', 'Bus Driver', 'Business', 'Cargo Pilot', 'EMS', 'Farmer', 'Firefighter', 'Fisherman',
                'Gambling', 'Garbage', 'Helicopter Pilot', 'Hunter', 'Mechanic', 'Miner', 'Player', 'Racer', 'Strength',
                'Train Conductor', 'Trucking', 'PostOP']
    score = -1
    for f in database:
        tempscore = fuzz.partial_ratio(f, JobName)
        if tempscore > score:
            score = tempscore
            AJobName = f
    return AJobName


def GetJobDirectory(JobName: str):
    match GetJob(JobName):
        case 'Airline Pilot':
            return 'piloting piloting'
        case 'Bus Driver':
            return 'train bus'
        case 'Business':
            return 'business business'
        case 'Cargo Pilot':
            return 'piloting cargos'
        case 'EMS':
            return 'ems ems'
        case 'Farmer':
            return 'farming farming'
        case 'Firefighter':
            return 'ems fire'
        case 'Fisherman':
            return 'farming fishing'
        case 'Gambling':
            return 'casino casino'
        case 'Garbage':
            return 'trucking garbage'
        case 'Helicopter Pilot':
            return 'piloting heli'
        case 'Hunter':
            return 'hunting skill'
        case 'Mechanic':
            return 'trucking mechanic'
        case 'Miner':
            return 'farming mining'
        case 'Player':
            return 'player player'
        case 'Racer':
            return 'player racing'
        case 'Strength':
            return 'physical strength'
        case 'Train Conductor':
            return 'train train'
        case 'Trucking':
            return 'trucking trucking'
        case 'PostOP':
            return 'trucking postop'
    return None
