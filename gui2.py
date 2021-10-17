from enum import Enum
from pathlib import Path
from tkinter import *
from tkinter.font import Font

import os
import cv2
import imutils
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
from matplotlib import pyplot as plt


class VidMode(Enum):
    ORIGINAL = "원본 영상"
    EDGE = "경계 검출"


OUTPUT_PATH = Path(__file__).parent
SAVED_IMAGES_PATH = OUTPUT_PATH / Path("saved_images")
VMODE = VidMode.ORIGINAL


def switch_VMODE():
    global VMODE
    if VMODE == VidMode.ORIGINAL:
        VMODE = VidMode.EDGE
    elif VMODE == VidMode.EDGE:
        VMODE = VidMode.ORIGINAL


# def draw_histogram(img):
#     fig.clear()
#     fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0, 255]))
#     hist_area.draw_idle()
#
#
# def canny_edge_detection(img_gray, low, high):
#     img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
#     # cv2.Canny: image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None
#     res = cv2.Canny(img_blur, low, high)
#     return res
#
#
# # 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
# cap = cv2.VideoCapture(0)
#
#
# def cam_thread():
# global VMODE
# ret, color = cap.read()
# v_color = cv2.resize(color, dsize=(0, 0), fx=1.5, fy=1.5)
# g_color = cv2.resize(color, dsize=(0, 0), fx=0.5, fy=0.5)
#
# if VMODE == VidMode.ORIGINAL:
#     image = cv2.cvtColor(v_color, cv2.COLOR_BGR2RGB)
# elif VMODE == VidMode.EDGE:
#     image = cv2.cvtColor(v_color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일
#     g_image = cv2.cvtColor(g_color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일
#
#     draw_histogram(image)
#     image = canny_edge_detection(image, low_scale.get(), high_scale.get())  # 캐니에지검출
#
#     # 오른쪽 그레이스케일 이미지용
#     g_image = Image.fromarray(g_image)
#     g_image = ImageTk.PhotoImage(g_image)
#     greyscale_label.gimg = g_image
#     greyscale_label.configure(image=g_image)
#
# image = Image.fromarray(image)  # ndarray -> tkinter용 이미지로 변환
# imgtk = ImageTk.PhotoImage(image)
# video_label.imgtk = imgtk
# video_label.configure(image=imgtk)
# video_label.after(10, cam_thread)

def popup_saved_image(filename):
    FILE_DIR = SAVED_IMAGES_PATH / Path(filename)
    print(FILE_DIR)
    popup_toplevel = Toplevel()
    popup_toplevel.minsize(width=250, height=250)
    popup_toplevel.title(filename)
    popup_label = Label(popup_toplevel, width=400, height=400, bg="cyan")
    popup_label.pack()
    img = Image.open(FILE_DIR)
    img = ImageTk.PhotoImage(image=img)
    popup_label.img = img
    popup_label.configure(image=img)


# ------------------------------
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
canvas_frame.columnconfigure(0, weight=1)
canvas_frame.columnconfigure(1, weight=1)
canvas_frame.rowconfigure(0, weight=2)
canvas_frame.rowconfigure(1, weight=2)
canvas_frame.rowconfigure(2, weight=1)

# Top layout
video00 = Label(canvas_frame, bg="blue", text="원본영상")
video01 = Label(canvas_frame, bg="darkblue", text="에지영상")
video10 = Label(canvas_frame, bg="cyan", text="히스토그램")
video11 = Label(canvas_frame, bg="navy", text="흑백영상")

video00.grid(row=0, column=0, sticky=NSEW)
video01.grid(row=0, column=1, sticky=NSEW)
video10.grid(row=1, column=0, sticky=NSEW)
video11.grid(row=1, column=1, sticky=NSEW)

# Bottom layout
buttonFont = Font(family='Tahoma', size=12, weight='bold', underline=1)
scaleFont = Font(family='Tahoma', size=12, weight='bold')

bottom_layout = Frame(canvas_frame, bg="ivory")
bottom_layout.grid(row=2, columnspan=2, sticky=NSEW)
bottom_layout.columnconfigure(0, weight=3)
bottom_layout.columnconfigure(1, weight=2)
bottom_layout.rowconfigure(0, weight=1)
bottom_layout.rowconfigure(1, weight=5)

# Detector layout
detector_layout = Frame(bottom_layout)
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
c_index = 0
for i in range(2):
    for j in range(2):
        tmp_frame = Frame(parameter_layout, bg=colors[c_index])
        c_index = c_index + 1
        tmp_frame.grid(row=i, column=j, sticky=NSEW)
        low_label = Label(tmp_frame, text="Low Threshold", fg="#4535AA", font=scaleFont, bg="white")
        low_label.pack(side="left", padx=3)
        low_scale = Scale(tmp_frame, length="200", from_=0, to=255, bg="white", orient=HORIZONTAL)
        low_scale.set(100)
        low_scale.pack(side="right", padx=3)


# Capture layout
capture_layout = Frame(bottom_layout, bg="cyan")
capture_layout.grid(row=0, column=1, rowspan=2)

capture_btn = Button(capture_layout,
                     text="Save Image",
                     font=buttonFont,
                     fg="white",
                     bg="#4535AA",
                     activeforeground="#009888",
                     borderwidth=3,
                     command=switch_VMODE,
                     relief="groove")
capture_btn.pack()

capture_lb = Listbox(capture_layout)
capture_lb['bg'] = "darkgrey"
capture_lb['fg'] = "lime"
capture_lb.pack()
capture_lb.bind("<<ListboxSelect>>", lambda x: popup_saved_image(capture_lb.get(capture_lb.curselection())))
for file in os.listdir(SAVED_IMAGES_PATH):
    capture_lb.insert(END, file)



if __name__ == "__main__":
    print("start")
    # cam_thread()
    window.mainloop()
    print("end")
