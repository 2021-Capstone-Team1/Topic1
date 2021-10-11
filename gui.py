from enum import Enum
from pathlib import Path
from tkinter import *

import cv2
import imutils
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure


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
    res = cv2.Canny(img_blur, low, high)  # image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None
    return res


# 핵심: cv2.imshow 대신 tkinter에서 제공하는 label 위젯에 반복적으로 이미지를 교체해주는 것이다.
cap = cv2.VideoCapture(0)
def cam_thread():
    global VMODE
    ret, color = cap.read()
    color = imutils.resize(color, width=int(ws * 3 / 4), height=int(hs * 3 / 4))
    if VMODE == VidMode.ORIGINAL:
        image = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)

    elif VMODE == VidMode.EDGE:
        image = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)  # 그레이 스케일
        draw_histogram(image)
        image = canny_edge_detection(image, low_scale.get(), high_scale.get())  # 캐니에지검출
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

# 비디오 라벨 (경계)-------------------
video_label = Label(
    master=window,
    bg="#454545",
    width=int(ws * 3 / 4),  # w,
    height=int(hs * 3 / 4)  # h
)
video_label.pack(side="left", expand=True)

# frame-------------------
# wframe = Frame(window, bg="#342211")
# wframe.pack(side="bottom", expand=True)


# '사진업로드' 버튼----------
button_image_1 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_1 = Button(
    window,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.pack()
# button_1.place(
#     # x=120.0,
#     y=957.0,
#     width=159.0,
#     height=57.0,
#     relx=0.1
# )

# '경계검출' 버튼------------
button_image_2 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_2 = Button(
    window,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=switch_VMODE,
    relief="flat"
)
button_2.pack()
# threshold scale-------------------
low_label = Label(window, text="Low Threshold")
low_label.place(
    y=957.0,
    relx=0.3
)
low_scale = Scale(window, from_=0, to=255, orient=HORIZONTAL)
low_scale.set(100)
low_scale.place(
    y=957.0,
    relx=0.4
)

high_label = Label(window, text="High Threshold")
high_label.place(
    y=957.0,
    relx=0.5
)
high_scale = Scale(window, from_=0, to=255, orient=HORIZONTAL)
high_scale.set(150)
high_scale.place(
    y=957.0,
    relx=0.6
)

# 히스토그램-------------------
fig = Figure(figsize=(5, 1), dpi=100)
hist_area = FigureCanvasTkAgg(fig, master=window)
hist_area.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=1)
toolbar = NavigationToolbar2Tk(hist_area, window)

cam_thread()
window.mainloop()
