import pyautogui

# 
def start_play():
    button_location = pyautogui.locateOnScreen('StartButton.png',grayscale=True)
    if button_location is not None:
        button_center = pyautogui.center(button_location)
        pyautogui.click(button_center)
        pyautogui.move(100,100)
    else:
        print('Image not found on screen')
        
def finish_play():
    button_location = pyautogui.locateOnScreen('FinishButton.png',grayscale=True)
    if button_location is not None:
        button_center = pyautogui.center(button_location)
        pyautogui.click(button_center)
        pyautogui.move(100,100)
    else:
        print('Image not found on screen')

def click_position(x,y):
    pyautogui.click(x,y)
    print(f'点击({x},{y})完成')
