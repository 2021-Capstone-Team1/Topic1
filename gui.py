from enum import Enum
from pathlib import Path
from tkinter import *
from tkinter.font import Font

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
    fig.add_subplot(111).plot(cv2.calcHist([img], [0], None, [256], [0, 255]))
    hist_area.draw_idle()


def canny_edge_detection(img_gray, low, high):
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    # cv2.Canny: image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None
    res = cv2.Canny(img_blur, low, high)
    return res


# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)


def cam_thread():
    global VMODE
    ret, color = cap.read()
    v_color = cv2.resize(color, dsize=(0, 0), fx=1.5, fy=1.5)
    g_color = cv2.resize(color, dsize=(0, 0), fx=0.5, fy=0.5)

    if VMODE == VidMode.ORIGINAL:
        image = cv2.cvtColor(v_color, cv2.COLOR_BGR2RGB)
    elif VMODE == VidMode.EDGE:
        image = cv2.cvtColor(v_color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일
        g_image = cv2.cvtColor(g_color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일

        draw_histogram(image)
        image = canny_edge_detection(image, low_scale.get(), high_scale.get())  # 캐니에지검출

        # 오른쪽 그레이스케일 이미지용
        g_image = Image.fromarray(g_image)
        g_image = ImageTk.PhotoImage(g_image)
        greyscale_label.gimg = g_image
        greyscale_label.configure(image=g_image)

    image = Image.fromarray(image)  # ndarray -> tkinter용 이미지로 변환
    imgtk = ImageTk.PhotoImage(image)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, cam_thread)


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
window.title("캡스톤디자인1팀 경계검출")
window.bind('<Escape>', lambda e: window.quit())  # esc로 창 종료
window.resizable(True, True)

canvas_frame = Frame(window, width=w, height=h)
canvas_frame.pack(fill=BOTH, expand=YES)
canvas_frame.columnconfigure(0, weight=3)
canvas_frame.columnconfigure(1, weight=2)
canvas_frame.rowconfigure(0, weight=1)

# Create Main Frames
left_frame = Frame(canvas_frame, width=730, bg="white")
right_frame = Frame(canvas_frame, width=w - 730, bg="white")

# Design Main Frames
left_frame.grid(column=0, row=0, sticky=NSEW)
right_frame.grid(column=1, row=0, sticky=NSEW)

# -- left layout
left_frame.columnconfigure(index=0, weight=1)
left_frame.columnconfigure(index=1, weight=1)
left_frame.columnconfigure(index=2, weight=1)
left_frame.rowconfigure(index=0, weight=5)
left_frame.rowconfigure(index=1, weight=1)

# -- right layout
right_frame.rowconfigure(index=0, weight=2)
right_frame.rowconfigure(index=1, weight=3)
right_frame.columnconfigure(index=0, weight=1)

# Left Layout Widgets: Labels, Buttons, Scale
video_label = Label(left_frame, bg="#1c3257", text="video")
video_label.grid(row=0, columnspan=4, sticky=NSEW)

buttonFont = Font(family='Tahoma', size=16, weight='bold', underline=1)
scaleFont = Font(family='Tahoma', size=16, weight='bold')
edge_button = Button(
    left_frame,
    text="Edge Detection",
    font=buttonFont,
    fg="white",
    bg="#4535AA",
    activeforeground="#009888",
    borderwidth=3,
    command=switch_VMODE,
    relief="groove"
)
edge_button.grid(column=2, row=1, padx=3)

# threshold scale
scale_frame1 = Frame(left_frame, bg="white")
scale_frame2 = Frame(left_frame, bg="white")
scale_frame1.grid(column=0, row=1, padx=3)
scale_frame2.grid(column=1, row=1, padx=3)

low_label = Label(scale_frame1, text="Low Threshold", fg="#4535AA", font=scaleFont, bg="white")
low_label.pack(side="left", padx=3)

low_scale = Scale(scale_frame1, length="200", from_=0, to=255, bg="white", orient=HORIZONTAL)
low_scale.set(100)
low_scale.pack(side="right", padx=3)

high_label = Label(scale_frame2, text="High Threshold", fg="#4535AA", font=scaleFont, bg="white")
high_label.pack(side="left", padx=3)

high_scale = Scale(scale_frame2, length="200", from_=0, to=255, bg="white", orient=HORIZONTAL)
high_scale.set(150)
high_scale.pack(side="right", padx=3)

# Right Layout Widgets: Labels
greyscale_label = Label(right_frame,bg="white")
greyscale_label.grid(column=0, row=0)

toolbar_frame = Frame(right_frame, bg="white")
toolbar_frame.grid(column=0, row=1, sticky=NSEW)

fig =Figure(figsize=(4,5), dpi=100)
hist_area = FigureCanvasTkAgg(fig, master=toolbar_frame)
hist_area.get_tk_widget().pack(side="top", fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(hist_area, toolbar_frame)

cam_thread()
window.mainloop()
