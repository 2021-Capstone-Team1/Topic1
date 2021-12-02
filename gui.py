import os
import time
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
        blur_frame0.pack(fill=BOTH, expand=YES)
        blur_frame1.pack(fill=BOTH, expand=YES)
        blur_frame2.pack_forget()
        blur_frame3.pack_forget()
        blur_frame4.pack_forget()
    elif SELECTED_BLUR == Blur.MEDIAN:
        blur_frame0.pack(fill=BOTH, expand=YES)
        blur_frame1.pack_forget()
        blur_frame2.pack_forget()
        blur_frame3.pack_forget()
        blur_frame4.pack_forget()
    elif SELECTED_BLUR == Blur.BILATERAL:
        blur_frame0.pack_forget()
        blur_frame1.pack_forget()
        blur_frame2.pack(fill=BOTH, expand=YES)
        blur_frame3.pack(fill=BOTH, expand=YES)
        blur_frame4.pack(fill=BOTH, expand=YES)


def set_selected_detector(event):
    global SELECTED_DETECTOR
    SELECTED_DETECTOR = Detector(detector_combo.get())
    print(SELECTED_BLUR, SELECTED_DETECTOR)
    for w in detector_param_frame.winfo_children():
        w.grid_forget()
    if SELECTED_DETECTOR == Detector.CANNY:
        detector_frame1.pack(fill=BOTH, expand=YES)
        detector_frame4.pack(fill=BOTH, expand=YES)
        detector_frame5.pack(fill=BOTH, expand=YES)
        detector_frame0.pack_forget()
        detector_frame2.pack_forget()
        detector_frame3.pack_forget()
    elif SELECTED_DETECTOR == Detector.LAPLACIAN:
        detector_frame0.pack(fill=BOTH, expand=YES)
        detector_frame1.pack_forget()
        detector_frame2.pack_forget()
        detector_frame3.pack_forget()
        detector_frame4.pack_forget()
        detector_frame5.pack_forget()
    elif SELECTED_DETECTOR == Detector.SOBEL:
        detector_frame0.pack(fill=BOTH, expand=YES)
        detector_frame2.pack(fill=BOTH, expand=YES)
        detector_frame3.pack(fill=BOTH, expand=YES)
        detector_frame1.pack_forget()
        detector_frame4.pack_forget()
        detector_frame5.pack_forget()
    elif SELECTED_DETECTOR == Detector.PREWITT:
        detector_frame0.pack_forget()
        detector_frame1.pack_forget()
        detector_frame2.pack_forget()
        detector_frame3.pack_forget()
        detector_frame4.pack_forget()
        detector_frame5.pack_forget()


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
    try:
        img = Image.open(FILE_DIR)
        img = ImageTk.PhotoImage(image=img)
        video11.img = img
        video11.configure(image=img)
    except:
        print("[Warning]: file is not found")

def draw_histogram(img):
    fig.clear()
    fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0, 255]))
    hist_area.draw_idle()


# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)


def cam_thread():
    global SELECTED_BLUR, SELECTED_DETECTOR
    ret, color = cap.read()
    color = cv2.resize(color, dsize=(0, 0), fx=0.55, fy=0.55, interpolation=cv2.INTER_LINEAR)

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
w = window.winfo_screenwidth()  # width for the Tk root
h = 800  # height for the Tk root

ws = window.winfo_screenwidth()  # width of the screen
hs = window.winfo_screenheight()  # height of the screen
print(ws, hs)
x = (ws / 2) - (w / 2)
y = (hs / 2) - (h / 2)

window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.minsize(w, h)
window.configure(bg="#FFFFFF")
window.title("캡스톤디자인 NETFLEX팀 주제1")
window.bind('<Escape>', lambda e: window.quit())  # esc로 창 종료
window.resizable(True, True)
header_footerFont = Font(family='Tahoma', size=10)
scaleFont = Font(family='Tahoma', size=11)

# Canvas 3x2
canvas_frame = Frame(window)
canvas_frame.place(x=0, y=0, width=w, height=h-30)
canvas_frame.rowconfigure(0, weight=1)
canvas_frame.rowconfigure(1, weight=1)

canvas_frame_video = Frame(canvas_frame)
canvas_frame_video.place(x=0, y=0, width =w, height=640)

canvas_frame_bottom = Frame(canvas_frame)
canvas_frame_bottom.place(x=0, y=640, width= w, height=130)

# Footer
footer_label = Label(window, bg="#B7472A", font=header_footerFont, fg="white", text="Netflex.t of Sejong Univ.")
footer_label.place(x=0, y=h-30, width=w, height=30)

# Top layout
frame_tmp00 = Frame(canvas_frame_video, borderwidth=2, relief="ridge")
frame_tmp01 = Frame(canvas_frame_video, borderwidth=2, relief="ridge")
frame_tmp10 = Frame(canvas_frame_video, borderwidth=2, relief="ridge")
frame_tmp11 = Frame(canvas_frame_video, borderwidth=2, relief="ridge")

label00 = Label(master=frame_tmp00, width=int(w / 2), bg="#B7472A", fg="white", text="원본")
label01 = Label(master=frame_tmp01, width=int(w / 2), bg="#B7472A", fg="white", text="히스토그램")
label10 = Label(master=frame_tmp10, width=int(w / 2), bg="#B7472A", fg="white", text="에지")
label11 = Label(master=frame_tmp11, width=int(w / 2), bg="#B7472A", fg="white", text="캡쳐")

video00 = Label(master=frame_tmp00, width=int(w / 2))
video01 = Frame(master=frame_tmp01, width=int(w / 2))# toolbar frame
video10 = Label(master=frame_tmp10, width=int(w / 2))
video11 = Label(master=frame_tmp11, width=int(w / 2))

frame_tmp00.place(x=0, y=0, width= int(w/2), height=320)
frame_tmp01.place(x=int(w / 2), y=0, width= int(w/2), height=320)
frame_tmp10.place(x=0, y=320, width= int(w/2), height=320)
frame_tmp11.place(x=int(w / 2), y=320, width= int(w/2), height=320)

label00.pack(side="top")
label01.pack(side="top")
label10.pack(side="top")
label11.pack(side="top")

video00.pack(side="bottom", fill=BOTH, expand=YES)
video01.pack(side="bottom", pady="15")
video10.pack(side="bottom", fill=BOTH, expand=YES)
video11.pack(side="bottom", fill=BOTH, expand=YES)

fig = Figure(figsize=(5, 3), dpi=100)  # histogram
hist_area = FigureCanvasTkAgg(fig, master=video01)
hist_area.get_tk_widget().pack(fill="both")
toolbar = NavigationToolbar2Tk(hist_area, video01)

# Bottom layout (cell합치고 다시 parameter, capture영역으로 분할)
bottom_layout = canvas_frame_bottom
bottom_layout.columnconfigure(0, weight=4)
bottom_layout.columnconfigure(1, weight=1)
bottom_layout.rowconfigure(0, weight=1)

# Parameter layout 2x2
param_layout = Frame(bottom_layout)
param_layout.grid(row=0, column=0, sticky=NSEW)
param_layout.rowconfigure(0, weight=1)
param_layout.rowconfigure(1, weight=5)
param_layout.columnconfigure(0, weight=1)
param_layout.columnconfigure(1, weight=3)

# row=0
blur_frame = Frame(param_layout, bg="white", borderwidth=1, relief=SUNKEN)
blur_frame.grid(row=0, column=0, sticky=NSEW)
filter_frame = Frame(param_layout, bg="white", borderwidth=1, relief=SUNKEN)
filter_frame.grid(row=0, column=1, sticky=NSEW)

blur_label = Label(blur_frame, text="Blur Type", fg="black", bg="white", font=scaleFont)
blur_label.pack(side="left", padx=3)
blur_combo = ttk.Combobox(blur_frame, state="readonly", font=scaleFont, values=[e.name for e in Blur])
blur_combo.pack(side="left", padx=3)
blur_combo.current(0)
blur_combo.bind("<<ComboboxSelected>>", set_selected_blur)

detector_label = Label(filter_frame, text="Edge Detection Type", fg="black", bg="white", font=scaleFont)
detector_label.pack(side="left", padx=3)
detector_combo = ttk.Combobox(filter_frame, state="readonly", font=scaleFont, values=[e.name for e in Detector])
detector_combo.pack(side="left", padx=3)
detector_combo.current(0)
detector_combo.bind("<<ComboboxSelected>>", set_selected_detector)

# row=1
# -- blur --
blur_param_frame = Frame(param_layout, bg="white", borderwidth=1, relief=SUNKEN)
blur_param_frame.grid(row=1, column=0, sticky=NSEW)
detector_param_frame = Frame(param_layout, bg="white", borderwidth=1, relief=SUNKEN)
detector_param_frame.grid(row=1, column=1, sticky=NSEW)

blur_frame0 = Frame(blur_param_frame, bg="white")
blur_frame1 = Frame(blur_param_frame, bg="white")
blur_frame2 = Frame(blur_param_frame, bg="white")
blur_frame3 = Frame(blur_param_frame, bg="white")
blur_frame4 = Frame(blur_param_frame, bg="white")

ksize_label = Label(blur_frame0, text="ksize", font=scaleFont, bg="white")
ksize_label.pack(side="left", fill='x', expand=YES)
sigmaX_label = Label(blur_frame1, text="sigmaX", font=scaleFont, bg="white")
sigmaX_label.pack(side="left", fill='x', expand=YES)
d_label = Label(blur_frame2, text="diameter    ", font=scaleFont, bg="white")
d_label.pack(side="left", fill='x', expand=YES)
sigmaColor_label = Label(blur_frame3, text="sigmaColor", font=scaleFont, bg="white")
sigmaColor_label.pack(side="left", fill='x', expand=YES)
sigmaSpace_label = Label(blur_frame4, text="sigmaSpace", font=scaleFont, bg="white")
sigmaSpace_label.pack(side="left", fill='x', expand=YES)

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
ksize_spinbox = Spinbox(blur_frame0, from_=1, to=31, increment=2, state="readonly",
                        textvariable=default_value_ksize)
ksize_spinbox.pack(side="right", fill='x', expand=YES)
sigmaX_spinbox = Spinbox(blur_frame1, from_=0, to=10, increment=1, state="readonly")
sigmaX_spinbox.pack(side="right", fill='x', expand=YES)
d_spinbox = Spinbox(blur_frame2, from_=1, to=10, increment=1, state="readonly", textvariable=default_value_d)
d_spinbox.pack(side="right", fill='x', expand=YES)
sigmaColor_entry = Spinbox(blur_frame3, from_=0, to=75, increment=1, state="readonly",
                           textvariable=default_value_sigmaColor)
sigmaColor_entry.pack(side="right", fill='x', expand=YES)
sigmaSpace_entry = Spinbox(blur_frame4, from_=0, to=75, increment=1, state="readonly",
                           textvariable=default_value_sigmaSpace)
sigmaSpace_entry.pack(side="right", fill='x', expand=YES)

# -- detector --
dw = 40
detector_frame0 = Frame(detector_param_frame, bg="white")
detector_frame1 = Frame(detector_param_frame, bg="white")
detector_frame2 = Frame(detector_param_frame, bg="white")
detector_frame3 = Frame(detector_param_frame, bg="white")
detector_frame4 = Frame(detector_param_frame, bg="white")
detector_frame5 = Frame(detector_param_frame, bg="white")

ksize_d_label = Label(detector_frame0, width=dw, text="ksize", font=scaleFont, bg="white")
ksize_d_label.pack(side="left", fill='x', expand=YES)
norm_label = Label(detector_frame1, width=dw, text="norm", font=scaleFont, bg="white")
norm_label.pack(side="left", fill='x', expand=YES)
dx_label = Label(detector_frame2, width=dw, text="dx", font=scaleFont, bg="white")
dx_label.pack(side="left", fill='x', expand=YES)
dy_label = Label(detector_frame3, width=dw, text="dy", font=scaleFont, bg="white")
dy_label.pack(side="left", fill='x', expand=YES)
low_label = Label(detector_frame4, width=dw, text="Low Threshold", font=scaleFont, bg="white")
low_label.pack(side="left", fill='x', expand=YES)
high_label = Label(detector_frame5, width=dw, text="High Threshold", font=scaleFont, bg="white")
high_label.pack(side="left", fill='x', expand=YES)

ksize_d_spinbox = Spinbox(detector_frame0, from_=1, to=31, increment=2, state="readonly",
                          textvariable=default_value_ksize_d)
ksize_d_spinbox.pack(side="right", fill=BOTH, expand=YES)
norm_combobox = ttk.Combobox(detector_frame1, state="readonly", values=["L1", "L2"])
norm_combobox.current(1)
norm_combobox.pack(side="right", fill='x', expand=YES)
dx_spinbox = Spinbox(detector_frame2, from_=1, to=10, increment=1, state="readonly")
dx_spinbox.pack(side="right", fill='x', expand=YES)
dy_spinbox = Spinbox(detector_frame3, from_=1, to=10, increment=1, state="readonly")
dy_spinbox.pack(side="right", fill='x', expand=YES)
low_scale = Scale(detector_frame4, from_=0, to=255, bg="white", orient=HORIZONTAL)
low_scale.set(70)
low_scale.pack(side="right", fill='x', expand=YES)
high_scale = Scale(detector_frame5, from_=0, to=255, bg="white", orient=HORIZONTAL)
high_scale.set(120)
high_scale.pack(side="right", fill='x', expand=YES)


# Capture layout
capture_layout = Frame(bottom_layout, bg="white")
capture_layout.grid(row=0, column=1, sticky="NSEW")

capture_btn = Button(capture_layout,
                     text="Save Image",
                     font=scaleFont,
                     fg="white",
                     bg="#B7472A",
                     activeforeground="#B7472A",
                     borderwidth=3,
                     command=lambda: snapshot(),
                     relief="groove")
capture_btn.pack(side="top")

scrollbar = Scrollbar(capture_layout)
scrollbar.pack(side="right", fill="y")

capture_lb = Listbox(capture_layout, yscrollcommand=scrollbar.set, exportselection=False)
capture_lb['bg'] = "#E7E6E6"
capture_lb['fg'] = "grey"
capture_lb['font'] = scaleFont
capture_lb.pack(side="left", pady=3, fill="x", expand="yes")
capture_lb.bind("<<ListboxSelect>>", lambda event: popup_saved_image(capture_lb.get(capture_lb.curselection())))

for file in os.listdir(SAVED_IMAGES_PATH):
    capture_lb.insert(END, file)

scrollbar["command"] = capture_lb.yview
# -----------------------------------

if __name__ == "__main__":
    print("start")
    cam_thread()
    window.mainloop()
    print("end")
