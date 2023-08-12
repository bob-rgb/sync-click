from pyautogui import position
flag = 1
while flag == 1:
    print("请将鼠标移动到目标位置\n然后输入任意值")
    x = input()
    p = position()
    print(f'屏幕坐标：{p}')
    print('----------------------------------------')


