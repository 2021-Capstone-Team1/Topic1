import os
import time
from ctypes import windll
from enum import Enum
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter.font import Font

import cv2
import numpy as np
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
from pyscreenshot import grab


class Blur(Enum):
    GAUSSIAN = "GAUSSIAN"
    MEDIAN = "MEDIAN"
    BILATERAL = "BILATERAL"
    NONE = "NONE"


class Detector(Enum):
    CANNY = "CANNY"
    LAPLACIAN = "LAPLACIAN"
    SOBEL = "SOBEL"
    PREWITT = "PREWITT"
    NONE = "NONE"


Path('saved_images').mkdir(exist_ok=True)  # 스크린샷 저장할 경로 생성
SAVED_IMAGES_PATH = os.getcwd() / Path("saved_images")
SELECTED_BLUR = Blur.GAUSSIAN
SELECTED_DETECTOR = Detector.CANNY


def set_selected_blur(event):
    global SELECTED_BLUR
    SELECTED_BLUR = Blur(blur_combo.get())
    print(SELECTED_BLUR, SELECTED_DETECTOR)
    for w in blur_param_frame.winfo_children():
        w.grid_forget()
    if SELECTED_BLUR == Blur.GAUSSIAN:
        ksize_label.grid(row=0, column=0, sticky=NSEW)
        ksize_spinbox.grid(row=0, column=1, sticky=NSEW)
        sigmaX_label.grid(row=1, column=0, sticky=NSEW)
        sigmaX_spinbox.grid(row=1, column=1, sticky=NSEW)
    elif SELECTED_BLUR == Blur.MEDIAN:
        ksize_label.grid(row=0, column=0, sticky=NSEW)
        ksize_spinbox.grid(row=0, column=1, sticky=NSEW)
    elif SELECTED_BLUR == Blur.BILATERAL:
        d_label.grid(row=0, column=0, sticky=NSEW)
        d_spinbox.grid(row=0, column=1, sticky=NSEW)
        sigmaColor_label.grid(row=1, column=0, sticky=NSEW)
        sigmaColor_entry.grid(row=1, column=1, sticky=NSEW)
        sigmaSpace_label.grid(row=2, column=0, sticky=NSEW)
        sigmaSpace_entry.grid(row=2, column=1, sticky=NSEW)


def set_selected_detector(event):
    global SELECTED_DETECTOR
    SELECTED_DETECTOR = Detector(detector_combo.get())
    print(SELECTED_BLUR, SELECTED_DETECTOR)
    for w in detector_param_frame.winfo_children():
        w.grid_forget()
    if SELECTED_DETECTOR == Detector.CANNY:
        low_label.grid(row=0, column=0, sticky=NSEW)
        low_scale.grid(row=0, column=1, sticky=NSEW)
        high_label.grid(row=0, column=2, sticky=NSEW)
        high_scale.grid(row=0, column=3, sticky=NSEW)
        norm_label.grid(row=1, column=0, sticky=NSEW)
        norm_combobox.grid(row=1, column=1, sticky=NSEW)
    elif SELECTED_DETECTOR == Detector.LAPLACIAN:
        ksize_d_label.grid(row=0, column=0, sticky=NSEW)
        ksize_d_spinbox.grid(row=0, column=1, sticky=NSEW)
    elif SELECTED_DETECTOR == Detector.SOBEL:
        ksize_d_label.grid(row=0, column=0, sticky=NSEW)
        ksize_d_spinbox.grid(row=0, column=1, sticky=NSEW)
        dx_label.grid(row=1, column=0, sticky=NSEW)
        dx_spinbox.grid(row=1, column=1, sticky=NSEW)
        dy_label.grid(row=1, column=2, sticky=NSEW)
        dy_spinbox.grid(row=1, column=3, sticky=NSEW)
    elif SELECTED_DETECTOR == Detector.PREWITT:
        print("PREWITT")


# pipeline
def edge_detection(img, blur, detector):
    img = execute_blur(img, blur)
    img = execute_detector(img, detector)
    return img


# parameter를 가져온다.
def execute_blur(img, blur):
    if blur == Blur.GAUSSIAN:
        # sigmaY=0(기본)
        get_ksize = int(ksize_spinbox.get())
        if 1 <= get_ksize and get_ksize <= 31:
            img = cv2.GaussianBlur(img, ksize=(int(ksize_spinbox.get()), int(ksize_spinbox.get())),
                                   sigmaX=int(sigmaX_spinbox.get()))
        else:
            print("1~31의 홀수만 넣어주세요")
    elif blur == Blur.MEDIAN:
        # ksize: 커널크기
        img = cv2.medianBlur(img, ksize=int(ksize_spinbox.get()))
    elif blur == Blur.BILATERAL:
        img = cv2.bilateralFilter(img, d=int(d_spinbox.get()), sigmaColor=int(sigmaColor_entry.get()),
                                  sigmaSpace=int(sigmaSpace_entry.get()))
    return img


# parameter를 가져온다.
def execute_detector(img, detector):
    if detector == Detector.CANNY:
        # L2gradient(bool): L2-norm으로 방향성 그레이디언트를 정확하게 계산 vs 정확성은 떨어지지만 속도가 더 빠른 L1-norm
        norm_type = FALSE if norm_combobox.get() == "L1" else TRUE
        img = cv2.Canny(img, low_scale.get(), high_scale.get(), L2gradient=norm_type)
    elif detector == Detector.LAPLACIAN:
        img = cv2.Laplacian(img, ddepth=cv2.CV_8U, ksize=int(ksize_d_spinbox.get()))
    elif detector == Detector.SOBEL:
        # ksize: 홀수값 사용, 최대 31
        img = cv2.Sobel(img, cv2.CV_8U, int(dx_spinbox.get()), int(dy_spinbox.get()), ksize=int(ksize_d_spinbox.get()))
    elif detector == Detector.PREWITT:
        img = Prewitt(img)

    return img


def Prewitt(img):
    kernel_x = np.array([[-1, 0, 1],
                         [-1, 0, 1],
                         [-1, 0, 1]], np.float32)
    kernel_y = np.array([[-1, -1, -1],
                         [0, 0, 0],
                         [1, 1, 1]], np.float32)
    img_dx = cv2.filter2D(img, ddepth=-1, kernel=kernel_x)
    img_dy = cv2.filter2D(img, ddepth=-1, kernel=kernel_y)
    return img_dx + img_dy


def snapshot():
    # Warning:
    # 같은 이름으로 저장된다면 실제디렉토리엔 하나만 저장되지만, capture_lb엔 계속 추가된다.
    filename = SELECTED_DETECTOR.value + "-" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".png"
    dir = "saved_images/" + filename

    target_img = ImageTk.getimage(video10.img)
    target_img.save(dir)
    print("Screenshot Saved..", type(target_img))
    capture_lb.insert(END, filename)


def popup_saved_image(filename):
    print(filename)
    FILE_DIR = SAVED_IMAGES_PATH / Path(filename)
    img = Image.open(FILE_DIR)
    img = ImageTk.PhotoImage(image=img)
    video11.img = img
    video11.configure(image=img)


def draw_histogram(img):
    fig.clear()
    fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0, 255]))
    hist_area.draw_idle()

# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)


def cam_thread():
    global SELECTED_BLUR, SELECTED_DETECTOR
    ret, color = cap.read()

    # 컬러
    color_image = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    color_image = Image.fromarray(color_image)  # ndarray -> tkinter용 이미지로 변환
    color_image = ImageTk.PhotoImage(color_image)
    video00.img = color_image
    video00.configure(image=color_image)

    # 히스토그램
    grey_image = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    draw_histogram(grey_image)

    # 에지
    edge_image = edge_detection(grey_image, SELECTED_BLUR, SELECTED_DETECTOR)  # 캐니에지검출
    edge_image = Image.fromarray(edge_image)  # ndarray -> tkinter용 이미지로 변환
    edge_image = ImageTk.PhotoImage(edge_image)
    video10.img = edge_image
    video10.configure(image=edge_image)

    video10.after(10, cam_thread)


# -------------tkinter-----------------
window = Tk()

# 창을 screen 중간에 열기
w = 1500  # width for the Tk root
h = 800  # height for the Tk root

ws = window.winfo_screenwidth()  # width of the screen
hs = window.winfo_screenheight()  # height of the screen
print(ws, hs)
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
canvas_frame.rowconfigure(0, weight=3)
canvas_frame.rowconfigure(1, weight=3)
canvas_frame.rowconfigure(2, weight=1)

# Top layout
video00 = Label(canvas_frame, width=int(w/2), height=320, bg="lightslategray", text="원본영상", borderwidth=2, relief="ridge")
video01 = Frame(canvas_frame, width=int(w/2), height=320, bg="lightslategray", borderwidth=2, relief="ridge")  # toolbar frame
video10 = Label(canvas_frame, width=int(w/2), height=320, bg="lightslategray", text="에지영상", borderwidth=2, relief="ridge")
video11 = Label(canvas_frame, width=int(w/2), height=320, bg="lightslategray", borderwidth=2, relief="ridge")

video00.grid(row=0, column=0, sticky=NSEW)
video01.grid(row=0, column=1, sticky=NSEW)
video10.grid(row=1, column=0, sticky=NSEW)
video11.grid(row=1, column=1, sticky=NSEW)

fig = Figure(figsize=(2, 2), dpi=100)  # histogram
hist_area = FigureCanvasTkAgg(fig, master=video01)
hist_area.get_tk_widget().pack(side="top", fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(hist_area, video01)

# Bottom layout (parameter, capture영역으로 분할)
scaleFont = Font(family='Tahoma', size=10, weight='bold')

bottom_layout = Frame(canvas_frame, bg="white")
bottom_layout.grid(row=2, columnspan=2, sticky=NSEW)
bottom_layout.columnconfigure(0, weight=1)
bottom_layout.columnconfigure(1, weight=1)
bottom_layout.rowconfigure(0, weight=1)

# Parameter layout 2x2
param_layout = Frame(bottom_layout, width=int(w*0.7), height=120)
param_layout.grid(row=0, column=0, sticky=NSEW)
param_layout.rowconfigure(0, weight=1)
param_layout.rowconfigure(1, weight=3)
param_layout.columnconfigure(0, weight=1)
param_layout.columnconfigure(1, weight=7)

# row=0
blur_frame = Frame(param_layout, bg="white",borderwidth = 1, relief=SUNKEN)
blur_frame.grid(row=0, column=0, sticky=NSEW)
filter_frame = Frame(param_layout, bg="white",borderwidth = 1, relief=SUNKEN)
filter_frame.grid(row=0, column=1, sticky=NSEW)

blur_label = Label(blur_frame, text="Blur Type", fg="#4535AA",bg="white", font=scaleFont)
blur_label.pack(side="left", padx=3)
blur_combo = ttk.Combobox(blur_frame, state="readonly", font=scaleFont, values=[e.name for e in Blur])
blur_combo.pack(side="left", padx=3)
blur_combo.current(0)
blur_combo.bind("<<ComboboxSelected>>", set_selected_blur)

detector_label = Label(filter_frame, text="Edge Detection Type",fg="#4535AA", bg="white", font=scaleFont)
detector_label.pack(side="left", padx=3)
detector_combo = ttk.Combobox(filter_frame, state="readonly", font=scaleFont, values=[e.name for e in Detector])
detector_combo.pack(side="left", padx=3)
detector_combo.current(0)
detector_combo.bind("<<ComboboxSelected>>", set_selected_detector)

# row=1
blur_param_frame = Frame(param_layout, bg="white",borderwidth = 1, relief=SUNKEN)
blur_param_frame.grid(row=1, column=0, sticky=NSEW)
blur_param_frame.rowconfigure(0, weight=1)
blur_param_frame.rowconfigure(1, weight=1)
blur_param_frame.rowconfigure(2, weight=1)
blur_param_frame.columnconfigure(0, weight=1)
blur_param_frame.columnconfigure(1, weight=1)
detector_param_frame = Frame(param_layout, bg="white",borderwidth = 1, relief=SUNKEN)
detector_param_frame.grid(row=1, column=1, sticky=NSEW)
detector_param_frame.rowconfigure(0, weight=1)
detector_param_frame.rowconfigure(1, weight=1)
detector_param_frame.columnconfigure(0, weight=1)
detector_param_frame.columnconfigure(1, weight=1)
detector_param_frame.columnconfigure(2, weight=1)
detector_param_frame.columnconfigure(3, weight=1)

ksize_label = Label(blur_param_frame, text="ksize", font=scaleFont, bg="white")
sigmaX_label = Label(blur_param_frame, text="sigmaX", font=scaleFont, bg="white")
d_label = Label(blur_param_frame, text="diameter", font=scaleFont, bg="white")
sigmaColor_label = Label(blur_param_frame, text="sigmaColor", font=scaleFont, bg="white")
sigmaSpace_label = Label(blur_param_frame, text="sigmaSpace", font=scaleFont, bg="white")

default_value_ksize = StringVar(window)
default_value_ksize.set("3")
default_value_ksize_d = StringVar(window)
default_value_ksize_d.set("5")
default_value_d = StringVar(window)
default_value_d.set("9")
default_value_sigmaColor = StringVar(window)
default_value_sigmaColor.set("75")
default_value_sigmaSpace = StringVar(window)
default_value_sigmaSpace.set("75")
ksize_spinbox = Spinbox(blur_param_frame, from_=1, to=31, increment=2, state="readonly",
                        textvariable=default_value_ksize)
sigmaX_spinbox = Spinbox(blur_param_frame, from_=0, to=10, increment=1, state="readonly")
d_spinbox = Spinbox(blur_param_frame, from_=1, to=10, increment=1, state="readonly", textvariable=default_value_d)
sigmaColor_entry = Spinbox(blur_param_frame, from_=0, to=75, increment=1, state="readonly",
                           textvariable=default_value_sigmaColor)
sigmaSpace_entry = Spinbox(blur_param_frame, from_=0, to=75, increment=1, state="readonly",
                           textvariable=default_value_sigmaSpace)

ksize_d_label = Label(detector_param_frame, text="ksize",font=scaleFont, bg="white")
norm_label = Label(detector_param_frame, text="norm", font=scaleFont, bg="white")
dx_label = Label(detector_param_frame, text="dx",  font=scaleFont, bg="white")
dy_label = Label(detector_param_frame, text="dy", font=scaleFont, bg="white")
low_label = Label(detector_param_frame, text="Low Threshold",  font=scaleFont, bg="white")
high_label = Label(detector_param_frame, text="High Threshold",  font=scaleFont, bg="white")

ksize_d_spinbox = Spinbox(detector_param_frame, from_=1, to=31, increment=2, state="readonly",
                          textvariable=default_value_ksize_d)
norm_combobox = ttk.Combobox(detector_param_frame, state="readonly", values=["L1", "L2"])
norm_combobox.current(1)
dx_spinbox = Spinbox(detector_param_frame, from_=1, to=10, increment=1, state="readonly")
dy_spinbox = Spinbox(detector_param_frame, from_=1, to=10, increment=1, state="readonly")
low_scale = Scale(detector_param_frame, from_=0, to=255, bg="white", orient=HORIZONTAL)
low_scale.set(70)
high_scale = Scale(detector_param_frame, from_=0, to=255, bg="white", orient=HORIZONTAL)
high_scale.set(120)

# Capture layout
capture_layout = Frame(bottom_layout, bg="white", width=int(w*0.3), height=120)
capture_layout.grid(row=0, column=1, rowspan=2, sticky="NSEW")

capture_btn = Button(capture_layout,
                     text="Save Image",
                     font=scaleFont,
                     fg="white",
                     bg="#4535AA",
                     activeforeground="#009888",
                     borderwidth=3,
                     command=lambda: snapshot(),
                     relief="groove")
capture_btn.pack(pady=3)

scrollbar = Scrollbar(capture_layout)
scrollbar.pack(side="right", fill="y")

capture_lb = Listbox(capture_layout, yscrollcommand=scrollbar.set, exportselection=False)
capture_lb['bg'] = "black"
capture_lb['fg'] = "lime"
capture_lb['font'] = scaleFont
capture_lb.pack(pady=3, fill="x", expand="yes")
capture_lb.bind("<<ListboxSelect>>", lambda event: popup_saved_image(capture_lb.get(capture_lb.curselection())))

for file in os.listdir(SAVED_IMAGES_PATH):
    capture_lb.insert(END, file)

scrollbar["command"] = capture_lb.yview
# -----------------------------------

if __name__ == "__main__":
    print("start")
    # cam_thread()
    window.mainloop()
    print("end")
