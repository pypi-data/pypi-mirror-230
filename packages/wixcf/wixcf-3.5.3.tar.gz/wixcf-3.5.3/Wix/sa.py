import pyautogui
import time

def func():
    time.sleep(8)
    pyautogui.write("1234")
    pyautogui.press("enter")

while True:
    func()