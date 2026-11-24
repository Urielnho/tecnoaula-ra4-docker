import ctypes, sys
from ctypes import wintypes
from PIL import ImageGrab
from pathlib import Path
user32=ctypes.WinDLL('user32',use_last_error=True)
user32.GetWindowTextLengthW.argtypes=[wintypes.HWND];user32.GetWindowTextLengthW.restype=ctypes.c_int
user32.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
user32.IsWindowVisible.argtypes=[wintypes.HWND];user32.IsWindowVisible.restype=wintypes.BOOL
callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
windows=[]
def callback(hwnd,lparam):
 if user32.IsWindowVisible(hwnd):
  length=user32.GetWindowTextLengthW(hwnd);buffer=ctypes.create_unicode_buffer(length+1);user32.GetWindowTextW(hwnd,buffer,length+1)
  if buffer.value:windows.append((hwnd,buffer.value))
 return True
cb=callback_type(callback);user32.EnumWindows(cb,0)
if len(sys.argv)<3:
 print(windows);sys.exit()
found=[(h,t) for h,t in windows if (str(h)==sys.argv[1] if sys.argv[1].isdigit() else sys.argv[1] in t)]
if len(found)!=1:raise RuntimeError(str(found))
hwnd,title=found[0]
if len(sys.argv)>3 and sys.argv[3]=='activar':
 import time
 user32.ShowWindow(hwnd,6)
 user32.ShowWindow(hwnd,9)
 user32.SwitchToThisWindow(hwnd,True)
 user32.SetForegroundWindow(hwnd)
 time.sleep(0.8)
 sys.argv[3]='screen'
if len(sys.argv)>3 and sys.argv[3]=='screen':
 user32.GetForegroundWindow.restype=wintypes.HWND
 if user32.GetForegroundWindow()!=hwnd:raise RuntimeError('La ventana no esta en primer plano.')
 rect=wintypes.RECT();user32.GetWindowRect(hwnd,ctypes.byref(rect))
 ImageGrab.grab(bbox=(rect.left,rect.top,rect.right,rect.bottom)).save(sys.argv[2])
else:
 ImageGrab.grab(window=hwnd).save(sys.argv[2])
print('Captura real guardada:',title)


