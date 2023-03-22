from matplotlib.widgets import Button
import pysrt
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.widgets import Slider, Button
import  tkinter as tk
from tkinter import Label, ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import sys

root = tk.Tk()
root.title('Appilyzer')
root.resizable(False, False)
root.geometry('300x150')

def select_video_file():
    filetypes = (
        ('video files', '*.mp4'),
    )

    filename = fd.askopenfilename(
        title='Select Video File',
        initialdir='/',
        filetypes=filetypes)

    video_label.config(text=filename)

def select_srt_file():
    filetypes = (
        ('srt files', '*.srt'),
    )

    filename = fd.askopenfilename(
        title='Select Video File',
        initialdir='/',
        filetypes=filetypes)

    srt_label.config(text=filename)

# open button
open_video = ttk.Button(
    root,
    text='Select Video File',
    command=select_video_file
)

open_video.pack(expand=True)
video_label = Label(root, text="No File selected")
video_label.pack()

# open button
open_srt = ttk.Button(
    root,
    text='Select SRT File',
    command=select_srt_file
)

open_srt.pack(expand=True)
srt_label = Label(root, text="No File selected")
srt_label.pack()




def runProgram(videolabel, srtlabel):
    subs = pysrt.open(srtlabel)
    input_name=videolabel
    time = [0]
    height = []


    for sub in subs:
        he = sub.text.find('rel_alt')
        height.append(float(sub.text[he:].split(']')[0].split(" ")[1]))
        time.append(time[-1] + 0.042)

    fig = plt.figure(figsize=(8, 6))
    fig.subplots_adjust(bottom=0.25)
    ax = fig.add_subplot(111)
    ax.plot( time[1:], height)
    highLine = ax.axhline(max(height), ls="--", c="r")
    axfreq = fig.add_axes([0.25, 0.15, 0.65, 0.03])
    highSlider = Slider(
        ax=axfreq,
        label='High Threshold',
        valmin=-10,
        valmax=10,
        valinit=max(height),
    )
    def updateHigh(val):
        highLine.set_ydata(highSlider.val)

    highSlider.on_changed(updateHigh)

    lowLine = ax.axhline(min(height), ls="--", c="r")
    axfreq2 = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    lowSlider = Slider(
        ax=axfreq2,
        label='Lower Threshold',
        valmin=-10,
        valmax=10,
        valinit=min(height),
    )
    def update(val):
        lowLine.set_ydata(lowSlider.val)

    lowSlider.on_changed(update)

    resetax = fig.add_axes([0.25, 0.05, 0.65, 0.03])
    button = Button(resetax, 'Confirm', hovercolor='0.975')
    def reset(event):
        plt.close()
    button.on_clicked(reset)

    plt.show()

    high = highSlider.val
    low = lowSlider.val

    clips = []
    current = []
    allC = []
    start = 0
    for sub in subs:
        he = sub.text.find('rel_alt')
        h = float(sub.text[he:].split(']')[0].split(" ")[1])
        if h > low and h < high:
            if start == 0:
                start = sub.start
            current.append(h)
            allC.append(h)
        else:
            if len(current) > 0:
                clips.append([start,sub.end])
                start = 0
                current = []

    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(111)
    # ax.plot(allC)
    # plt.show()

    i = 0
    with open("videos.txt", "w") as file:
        for c in clips:
            start = c[0].to_time()
            end = c[1].to_time()
            os.system('ffmpeg -i {0} -vcodec copy -acodec copy -ss {1} -to {2} ./output/out{3}.mp4'.format(input_name,start,end,i))
            file.write("file './output/out{0}.mp4' \n".format(i))
            i += 1
    os.system('ffmpeg -f concat -safe 0 -i videos.txt -c copy ./output/{0}.mp4'.format(video_label['text'].split("/")[-1]+"cut"))
    os.remove("videos.txt")
    i = 0
    for c in clips:
        os.remove("./output/out{0}.mp4".format(i))
        i += 1


def run():
    runProgram(video_label['text'],srt_label['text'])

# open button
run_button = ttk.Button(
    root,
    text='Run',
    command=run
)

run_button.pack()
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        sys.exit("Error message")

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

