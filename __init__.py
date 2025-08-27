import pyautogui
import time

x,y = pyautogui.position()


for i in range(100):
    pyautogui.move(x+0.01, y+0.01)
    time.sleep(0.01)
