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

import time
k=ctypes.WinDLL('kernel32')
user32.GetForegroundWindow.restype=wintypes.HWND
user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype=wintypes.DWORD
user32.SetForegroundWindow.argtypes=[wintypes.HWND]
user32.AttachThreadInput.argtypes=[wintypes.DWORD,wintypes.DWORD,wintypes.BOOL]
name=sys.argv[1]
found=[(h,t) for h,t in windows if t=='RA4 '+name]
if len(found)!=1:raise RuntimeError(str(found))
hwnd,title=found[0]
fg=user32.GetForegroundWindow();tid=user32.GetWindowThreadProcessId(fg,None);my=k.GetCurrentThreadId()
user32.AttachThreadInput(my,tid,True)
try:user32.ShowWindow(hwnd,9);user32.SetForegroundWindow(hwnd)
finally:user32.AttachThreadInput(my,tid,False)
time.sleep(0.8)
if user32.GetForegroundWindow()!=hwnd:raise RuntimeError('Terminal no esta en primer plano')
r=wintypes.RECT();user32.GetWindowRect(hwnd,ctypes.byref(r))
im=ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom))
im.save('capturas/originales/'+name+'.png')
im.crop((8,42,im.width-8,im.height-8)).save('capturas/'+name+'.png')
print('Captura real:',title)
