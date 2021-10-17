from enum import Enum
from pathlib import Path
from tkinter import *
from tkinter.font import Font

import os
import cv2
import imutils
import time
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import numpy as np

# TODO : image capture (에지 이미지 가져오기)
# TODO : video 정상 스트리밍 확인
# TODO : 에지탐지 모델, 파라미터 개발
# TODO : capture_lb 너비 넓히기, 스크롤 추가

OUTPUT_PATH = Path(__file__).parent
SAVED_IMAGES_PATH = OUTPUT_PATH / Path("saved_images")


def draw_histogram(img):
    fig.clear()
    fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0, 255]))
    hist_area.draw_idle()


def canny_edge_detection(grey_image, low, high):
    img_blur = cv2.GaussianBlur(grey_image, (5, 5), 0)
    # cv2.Canny: image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None
    res = cv2.Canny(img_blur, low, high)
    return res


def snapshot():
    # Warning:
    # 같은 이름으로 저장된다면 실제디렉토리엔 하나만 저장되지만, capture_lb엔 계속 추가된다.
    img = cv2.imread("saved_images/cat.PNG")
    filename = "frame-" + time.strftime("%Y-%d-%m-%H-%M-%S") + ".jpg"
    dir = "saved_images/" + filename

    cv2.imwrite(dir, img)
    capture_lb.insert(END, filename)


def popup_saved_image(filename):
    FILE_DIR = SAVED_IMAGES_PATH / Path(filename)
    popup_toplevel = Toplevel()
    popup_toplevel.minsize(width=250, height=250)
    popup_toplevel.title(filename)
    popup_label = Label(popup_toplevel, width=400, height=400, bg="cyan")
    popup_label.pack()
    img = Image.open(FILE_DIR)
    img = ImageTk.PhotoImage(image=img)
    popup_label.img = img
    popup_label.configure(image=img)


# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)


def cam_thread():
    # ret, color = cap.read()

    # ------웹캠이 없어 임의로 추가------#
    color = cv2.imread("saved_images/cat.PNG")
    # -------------------------------#
    # 컬러
    color_image = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    color_image = Image.fromarray(color_image)  # ndarray -> tkinter용 이미지로 변환
    color_image = ImageTk.PhotoImage(color_image)
    video00.img = color_image
    video00.configure(image=color_image)

    # 그레이스케일
    grey_image = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    grey_image_label = Image.fromarray(grey_image)  # ndarray -> tkinter용 이미지로 변환
    grey_image_label = ImageTk.PhotoImage(grey_image_label)
    video01.img = grey_image_label
    video01.configure(image=grey_image_label)

    # 히스토그램
    draw_histogram(grey_image)

    # 에지
    edge_image = canny_edge_detection(grey_image, low_scale.get(), high_scale.get())  # 캐니에지검출
    edge_image = Image.fromarray(edge_image)  # ndarray -> tkinter용 이미지로 변환
    edge_image = ImageTk.PhotoImage(edge_image)

    video10.img = edge_image
    video10.configure(image=edge_image)

    video10.after(1000, cam_thread)


# -------------tkinter-----------------
window = Tk()

# 창을 screen 중간에 열기
w = 1200  # width for the Tk root
h = 650  # height for the Tk root

ws = window.winfo_screenwidth()  # width of the screen
hs = window.winfo_screenheight()  # height of the screen

x = (ws / 2) - (w / 2)
y = (hs / 2) - (h / 2)

window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.minsize(w, h)
window.configure(bg="#FFFFFF")
window.title("캡스톤디자인 NETFLEX팀 경계검출")
window.bind('<Escape>', lambda e: window.quit())  # esc로 창 종료
window.resizable(True, True)

# Canvas 3x2
canvas_frame = Frame(window, width=w, height=h)
canvas_frame.pack(fill=BOTH, expand=YES)
canvas_frame.columnconfigure(0, weight=3)
canvas_frame.columnconfigure(1, weight=3)
canvas_frame.rowconfigure(0, weight=4)
canvas_frame.rowconfigure(1, weight=4)
canvas_frame.rowconfigure(2, weight=1)

# Top layout
video00 = Label(canvas_frame, bg="blue", text="원본영상")
video01 = Label(canvas_frame, bg="darkblue", text="흑백영상")
video10 = Label(canvas_frame, bg="cyan", text="에지영상")
video11 = Frame(canvas_frame, bg="navy")  # toolbar frame

video00.grid(row=0, column=0, sticky=NSEW)
video01.grid(row=0, column=1, sticky=NSEW)
video10.grid(row=1, column=0, sticky=NSEW)
video11.grid(row=1, column=1, sticky=NSEW)

fig = Figure(figsize=(2, 2), dpi=100)  # histogram
hist_area = FigureCanvasTkAgg(fig, master=video11)
hist_area.get_tk_widget().pack(side="top", fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(hist_area, video11)

# right layout
buttonFont = Font(family='Tahoma', size=12, weight='bold', underline=1)
scaleFont = Font(family='Tahoma', size=12, weight='bold')

bottom_layout = Frame(canvas_frame, bg="ivory")
bottom_layout.grid(row=2, columnspan=2, sticky=NSEW)
bottom_layout.columnconfigure(0, weight=3)
bottom_layout.columnconfigure(1, weight=2)
bottom_layout.rowconfigure(0, weight=1)
bottom_layout.rowconfigure(1, weight=4)

# Detector layout
detector_layout = Frame(bottom_layout, height=20)
detector_layout.grid(row=0, column=0, sticky=NSEW)
detector_layout.rowconfigure(0, weight=1)
detector_layout.columnconfigure(0, weight=1)
detector_layout.columnconfigure(1, weight=1)
detector_layout.columnconfigure(2, weight=1)
detector_layout.columnconfigure(3, weight=1)

radioValue = IntVar()  # 같은 값을 공유해야 하나의 Radio button 세트로 인식됨
radio_btn0 = Radiobutton(detector_layout, bg="yellow", font=scaleFont, text="Canny", value=0, variable=radioValue)
radio_btn1 = Radiobutton(detector_layout, bg="orange", font=scaleFont, text="Canny", value=1, variable=radioValue)
radio_btn2 = Radiobutton(detector_layout, bg="cornsilk", font=scaleFont, text="Canny", value=2, variable=radioValue)
radio_btn3 = Radiobutton(detector_layout, bg="burlywood", font=scaleFont, text="Canny", value=3, variable=radioValue)
radio_btn0.grid(row=0, column=0, sticky=NSEW)
radio_btn1.grid(row=0, column=1, sticky=NSEW)
radio_btn2.grid(row=0, column=2, sticky=NSEW)
radio_btn3.grid(row=0, column=3, sticky=NSEW)

# Parameter layout
parameter_layout = Frame(bottom_layout)
parameter_layout.grid(row=1, column=0, sticky=NSEW)
parameter_layout.rowconfigure(0, weight=1)
parameter_layout.rowconfigure(1, weight=1)
parameter_layout.columnconfigure(0, weight=1)
parameter_layout.columnconfigure(1, weight=1)

colors = ["darkgreen", "darkcyan", "darkslategray", "darkolivegreen"]
scale_name = ["low_scale", "high_scale"]
c_index = 0
for i in range(2):
    tmp_frame = Frame(parameter_layout, bg=colors[c_index])
    c_index = c_index + 1
    tmp_frame.grid(row=i, column=0, sticky=NSEW)
    low_label = Label(tmp_frame, text="Low Threshold", fg="#4535AA", font=scaleFont, bg="white")
    low_label.pack(padx=3)

    low_scale = Scale(tmp_frame, length="200", from_=0, to=255, bg="white", orient=HORIZONTAL)
    low_scale.set(100)
    low_scale.pack(padx=3)

    tmp_frame2 = Frame(parameter_layout, bg=colors[c_index])
    c_index = c_index + 1
    tmp_frame2.grid(row=i, column=1, sticky=NSEW)
    high_label = Label(tmp_frame2, text="High Threshold", fg="#4535AA", font=scaleFont, bg="white")
    high_label.pack(padx=3)

    high_scale = Scale(tmp_frame2, length="200", from_=0, to=255, bg="white", orient=HORIZONTAL)
    high_scale.set(100)
    high_scale.pack(padx=3)

# Capture layout
capture_layout = Frame(bottom_layout, bg="cyan")
capture_layout.grid(row=0, column=1, rowspan=2, sticky="NSEW")

capture_btn = Button(capture_layout,
                     text="Save Image",
                     font=buttonFont,
                     fg="white",
                     bg="#4535AA",
                     activeforeground="#009888",
                     borderwidth=3,
                     command=lambda: snapshot(),
                     relief="groove")
capture_btn.pack(pady=3)

capture_lb = Listbox(capture_layout)
capture_lb['bg'] = "darkgrey"
capture_lb['fg'] = "lime"
capture_lb.pack(pady=3)
capture_lb.bind("<<ListboxSelect>>", lambda x: popup_saved_image(capture_lb.get(capture_lb.curselection())))
for file in os.listdir(SAVED_IMAGES_PATH):
    capture_lb.insert(END, file)

if __name__ == "__main__":
    print("start")
    cam_thread()
    window.mainloop()
    print("end")
