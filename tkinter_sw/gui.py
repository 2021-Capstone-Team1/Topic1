from pathlib import Path
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import imutils
from enum import Enum
import threading
import datetime
import os
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
import numpy as np


class VidMode(Enum):
    ORIGINAL = 0
    EDGE = 1


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")
VMODE = VidMode.ORIGINAL


def switch_VMODE():
    global VMODE
    if VMODE == VidMode.ORIGINAL:
        VMODE = VidMode.EDGE
    elif VMODE == VidMode.EDGE:
        VMODE = VidMode.ORIGINAL


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def draw_histogram(img):
    fig.clear()
    fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0,255]))
    hist_area.draw_idle()


# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)
def cam_thread():
    global VMODE
    ret, color = cap.read()
    color = imutils.resize(color, width=1000)
    if VMODE == VidMode.ORIGINAL:
        image = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    elif VMODE == VidMode.EDGE:
        image = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        draw_histogram(image)

    image = Image.fromarray(image)  # ndarray -> tkinter용 이미지로 변환
    imgtk = ImageTk.PhotoImage(image)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, cam_thread)


# ------------------------------
window = Tk()

# 창을 screen 중간에 열기
w = 800  # width for the Tk root
h = 650  # height for the Tk root

ws = window.winfo_screenwidth()  # width of the screen
hs = window.winfo_screenheight()  # height of the screen

x = (ws / 2) - (w / 2)
y = (hs / 2) - (h / 2)

window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.minsize(w, h)
window.configure(bg="#FFFFFF")
window.title("캡스톤디자인1팀 경계검출")
window.bind('<Escape>', lambda e: window.quit())  # esc로 창 종료
window.resizable(True, True)

# frame = window.Frame()  # TODO 위젯 정렬해주기

# 캔버스-------------------
video_label = Label(
    master=window,
    bg="#454545",
    width=int(ws*3/4),  #w,
    height=int(hs*3/4)  #h
)
video_label.pack(side="left", expand=True)

# frame-------------------
wframe = Frame(window, bg="#342211", relief='solid', bd=1, width=1000, height=500)
wframe.pack(side="right", expand=True)

# '경계검출' 버튼------------

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    wframe,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=switch_VMODE,
    relief="flat"
)
button_1.place(
    # x=20.0,
    y=957.0,
    width=159.0,
    height=57.0,
    relx=0.3
)

# '사진업로드' 버튼----------
button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    wframe,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    # x=120.0,
    y=957.0,
    width=159.0,
    height=57.0,
    relx=0.5
)

# '원본영상' 버튼----------
button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    wframe,
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=switch_VMODE,
    relief="flat"
)
button_3.place(
    # x=220.0,
    y=957.0,
    width=159.0,
    height=57.0,
    relx=0.7
)

# 히스토그램-------------------
fig = Figure(figsize=(5, 4), dpi=100)
hist_area = FigureCanvasTkAgg(fig, master=window)
hist_area.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(hist_area, window)

# FIXME: Thread 설정만 하면 tkinter 창이 안 뜸
# Thread 설정
# thread_img = threading.Thread(target=cam_thread(), args=())
# thread_img.daemon = True
# thread_img.start()
cam_thread()
window.mainloop()
