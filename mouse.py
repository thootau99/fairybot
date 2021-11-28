import pyautogui, sys
print('Press Ctrl-C to quit.')
try:
    while True:
    
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        color = pyautogui.pixel(x, y)
        print(positionStr, color, end='')
        print('\b' * len(positionStr)* len(color), end='', flush=True)
except KeyboardInterrupt:
    print('\n')