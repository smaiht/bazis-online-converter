import win32gui
import win32con

def resize_window(hwnd, width, height):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    win32gui.MoveWindow(hwnd, left, top, width, height, True)
    
    padding_left = 100 
    padding_top = 20
    win32gui.SetWindowPos(hwnd, 0, padding_left, padding_top, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

def list_all_windows():
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)

    for window in windows:
        print(f"HWND: {window[0]}, Title: {window[1]}")

list_all_windows()

# resize_window(657996, 768, 1280)