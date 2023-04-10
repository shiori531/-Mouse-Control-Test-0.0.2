'''
這段代碼是使用Python編寫的，用於控制滑鼠的移動和點擊。
它使用了一些外部庫，例如 pyautogui、keyboard、tkinter。
代碼的主要功能是在按下特定熱鍵後，使滑鼠在當前位置附近隨機移動並點擊。

以下是代碼各部分的簡要說明：

1.導入所需的庫。
2.定義 random_move_and_click 函數，用於在給定的範圍內隨機移動滑鼠並點擊。
3.定義 update_status_label 函數，用於更新顯示狀態的標籤。
4.定義 main_loop 函數，它在無限循環中不斷調用 random_move_and_click 函數。
5.定義 start_main_loop 函數，用於創建一個執行 main_loop 函數的守護線程。
6.定義 exit_app 函數，用於退出應用程序。
7.創建一個 tkinter GUI，包括標籤、輸入框、下拉選單和按鈕，用於顯示程序狀態、設置滑鼠移動範圍、設定熱鍵以及退出程序。
8.定義 start_program 和 stop_program 函數，用於開始和暫停程序。這些函數會通過更新 running_state 變量來控制 main_loop 函數的執行。
9.為預設的 F10 和 F12 鍵添加熱鍵，分別用於開始和暫停程序。用戶可以通過下拉選單選擇新的熱鍵。
10.在表單中新增三個按鈕，分別用於框選範圍、執行點選範圍和清除，但目前尚未設計功能。
11.運行 tkinter GUI 的主循環。
'''

# region 1. 導入所需的庫
import ctypes
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

import pyautogui
import keyboard
import time
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from threading import Thread
from PIL import ImageGrab
from PIL import Image, ImageTk, ImageDraw
# endregion


# region 2. 定義 random_move_and_click 函數

def random_move_and_click(running_state, x_var, y_var, s_var):
    if not running_state():
        return

    current_x, current_y = pyautogui.position()
    x_range = int(x_var.get())
    y_range = int(y_var.get())
    new_x = current_x + random.randint(-x_range, x_range)
    new_y = current_y + random.randint(-y_range, y_range)
    pyautogui.moveTo(new_x, new_y, _pause=False)

    if not running_state():
        return

    pyautogui.click()
    time.sleep(float(s_var.get()))

# endregion


# region 3.0.2 測試功能
def on_select_area_click():
    def on_start_select(event):
        canvas.data["start"] = (event.x, event.y)

    def on_end_select(event):
        x1, y1 = canvas.data["start"]
        x2, y2 = event.x, event.y
        canvas.data["rect_coords"] = (x1, y1, x2, y2)
        draw_rectangle_on_screen(x1, y1, x2, y2)
        top.destroy()

    def draw_rectangle_on_screen(x1, y1, x2, y2):
        # Get a screenshot
        screenshot = ImageGrab.grab()
        draw = ImageDraw.Draw(screenshot)

        # Draw a semi-transparent rectangle
        draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0, 64))

        # Save the screenshot with the rectangle
        screenshot.save("selected_area.png")

    top = Toplevel(root)
    top.attributes("-fullscreen", True)
    top.bind("<Button-1>", on_start_select)
    top.bind("<ButtonRelease-1>", on_end_select)

    # Create a Canvas and display the screen capture
    screen_w, screen_h = top.winfo_screenwidth(), top.winfo_screenheight()
    screenshot = ImageGrab.grab()
    canvas = Canvas(top, width=screen_w, height=screen_h)
    canvas.pack(fill=BOTH, expand=YES)

    # Save the screenshot as a PhotoImage
    photo = ImageTk.PhotoImage(screenshot)
    canvas.create_image(0, 0, anchor=NW, image=photo)
    canvas.data = {"photo": photo}

    top.mainloop()

#endregion


# region 3. 定義其他輔助函數
def update_status_label(status_label, text):
    status_label.config(text=text)
    status_label.update()

def main_loop(status_label, running_state, root, x_var, y_var, s_var):
    while True:
        if running_state():
            random_move_and_click(running_state, x_var, y_var, s_var)

def start_main_loop(status_label, running_state, root, x_var, y_var, s_var):
    thread = Thread(target=main_loop, args=(status_label, running_state, root, x_var, y_var, s_var))
    thread.daemon = True
    thread.start()
    return thread

def exit_app():
    running_state.set(False)
    time.sleep(0.5)  # 等待主循環結束
    root.destroy()

def create_selection_window():
    selection_window = tk.Toplevel(root)
    selection_window.attributes('-fullscreen', True)
    selection_window.attributes('-alpha', 0.01)

    def on_click(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y

    def on_release(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        draw_rectangle()

    def draw_rectangle():
        screen = ImageGrab.grab()
        draw = ImageDraw.Draw(screen)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 64)
        draw.rectangle((start_x, start_y, end_x, end_y), fill=color, outline=color, width=1)
        screen.show()
        selection_window.destroy()

    start_x, start_y, end_x, end_y = 0, 0, 0, 0
    selection_window.bind('<Button-1>', on_click)
    selection_window.bind('<ButtonRelease-1>', on_release)

#endregion

# region 3.0.1表單設計
# 3.0.1 表单设计
root = tk.Tk()
root.title("滑鼠控制程式 - 程式已暫停")

style = ttk.Style()
style.configure('TLabel', font=("Arial", 14))
style.configure('TButton', font=("Arial", 14))

status_label = ttk.Label(root, text="按 F10 開始程式，按 F12 暫停程式")
status_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

x_label = ttk.Label(root, text="X軸變化範圍:")
x_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
x_entry = ttk.Entry(root)
x_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
x_entry.insert(0, "50")

y_label = ttk.Label(root, text="Y軸變化範圍:")
y_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
y_entry = ttk.Entry(root)
y_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
y_entry.insert(0, "50")

s_label = ttk.Label(root, text="滑鼠延遲秒數:")
s_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
s_entry = ttk.Entry(root)
s_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
s_entry.insert(0, "1")

# 创建两个下拉选项并设置其默认值
hotkey_options = ["F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
start_hotkey = tk.StringVar()
start_hotkey.set("F10")
stop_hotkey = tk.StringVar()
stop_hotkey.set("F12")

# 创建两个标签和下拉选项组件
start_hotkey_label = ttk.Label(root, text="開始熱鍵:")
start_hotkey_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
start_hotkey_combobox = ttk.Combobox(root, textvariable=start_hotkey, values=hotkey_options, state="readonly")
start_hotkey_combobox.grid(row=4, column=1, padx=10, pady=10, sticky="w")

stop_hotkey_label = ttk.Label(root, text="暫停熱鍵:")
stop_hotkey_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
stop_hotkey_combobox = ttk.Combobox(root, textvariable=stop_hotkey, values=hotkey_options, state="readonly")
stop_hotkey_combobox.grid(row=5, column=1, padx=10, pady=10, sticky="w")

running_state = tk.BooleanVar()
running_state.set(False)

thread = start_main_loop(status_label, running_state.get, root, x_entry, y_entry, s_entry)

# 框選範圍按鈕
select_area_button = ttk.Button(root, text="框選範圍")
select_area_button.grid(row=8, column=0, padx=10, pady=10)

# 執行點選範圍按鈕
execute_area_button = ttk.Button(root, text="執行點選範圍")
execute_area_button.grid(row=8, column=1, padx=10, pady=10)

# 清除按鈕
clear_button = ttk.Button(root, text="清除")
clear_button.grid(row=8, column=2, padx=10, pady=10)

#endregion




# region 4. 創建 tkinter GUI 和主循環

# 預設熱鍵
default_start_hotkey = "f10"
default_stop_hotkey = "f12"

def start_program():
    running_state.set(True)
    update_status_label(status_label, "程式執行中...")
    root.title("滑鼠控制程式 - 程式執行中...")

def stop_program():
    running_state.set(False)
    update_status_label(status_label, "程式已暫停")
    root.title("滑鼠控制程式 - 程式已暫停...")

keyboard.add_hotkey(default_start_hotkey, start_program)
keyboard.add_hotkey(default_stop_hotkey, stop_program)

# 使用新的 update_hotkeys 函数
def show_error_message():
    messagebox.showerror("错误", "开始和暂停热键不能相同，请选择不同的热键。")

def update_hotkeys():
    # 检查开始和暂停热键是否相同
    if start_hotkey.get() == stop_hotkey.get():
        error_thread = Thread(target=show_error_message)
        error_thread.start()
        return

    # 清除所有现有的热键
    for hotkey in (start_hotkey.get(), stop_hotkey.get()):
        try:
            keyboard.remove_hotkey(hotkey)
        except KeyError:
            pass

    # 为开始和暂停程序添加新的热键
    keyboard.add_hotkey(start_hotkey.get(), start_program)
    keyboard.add_hotkey(stop_hotkey.get(), stop_program)



# 添加一个按钮来更新热键
update_hotkeys_button = ttk.Button(root, text="更新熱鍵", command=update_hotkeys)
update_hotkeys_button.grid(row=6, column=0, columnspan=2, pady=10)

quit_button = ttk.Button(root, text="退出", command=exit_app)
quit_button.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()



# endregion