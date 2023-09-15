import pandas as pd
import os
import argparse
import cv2
from tkinter import Tk, Label, Text, Button, CENTER
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


def main(fraud, fraud_type, text, image):
    def press(x):
        global result
        global comments
        result = x
        comments = commentBox.get('1.0', 'end')
        gui.destroy()

    def reasonPress(x):
        global reason
        reason = x

    def pressQuit():
        global quitApp
        quitApp = True
        gui.destroy()

    gui = Tk()

    # set the background color of GUI window
    gui.configure(background="light grey")

    # set the title of GUI window
    gui.title("False Positive Identifier")

    # set the configuration of GUI window
    width = gui.winfo_screenwidth()
    height = gui.winfo_screenheight()
    gui.geometry("%dx%d" % (width, height))
    fig = Figure(figsize=(5, 5),
                 dpi=100)
    plot1 = fig.add_subplot(111)

    # plotting the graph
    plot1.imshow(image)
    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=gui)
    NavigationToolbar2Tk(canvas, gui)
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.25, rely=0.5, anchor=CENTER)

    metrics = Label(gui, text=text)
    metrics.place(relx=0.5, rely=0.5, anchor=CENTER)

    commentBox = Text(gui, width=40, height=10)
    commentBox.place(relx=.75, rely=.5, anchor=CENTER)
    commentBoxLabel = Label(gui, text='Comments')
    commentBoxLabel.place(relx=0.75, rely=0.35, anchor=CENTER)

    reasonLabel = Label(gui, text='Reason')
    reasonLabel.place(relx=0.75, rely=0.7, anchor=CENTER)

    ocrButton = Button(gui, text=' OCR Failure ', fg='black', bg='light blue',
                       command=lambda: reasonPress('ocr'), height=1, width=10)

    ocrButton.place(relx=0.70, rely=0.75, anchor=CENTER)

    yoloButton = Button(gui, text=' YOLO Failure ', fg='black', bg='light blue',
                        command=lambda: reasonPress('yolo'), height=1, width=10)

    yoloButton.place(relx=0.80, rely=0.75, anchor=CENTER)

    if fraud:
        fraud_label = Label(gui, text="FRAUD")
        fraud_label.config(font=("Courier", 60), bg='#FF0000')
        fraud_label.place(relx=0.5, rely=0.25, anchor=CENTER)
        button1 = Button(gui, text='False Positive ', fg='black', bg='#ff6961',
                         command=lambda: press('fp'), height=1, width=10)

        button2 = Button(gui, text=' True Positive ', fg='black', bg='light green',
                         command=lambda: press('tp'), height=1, width=10)

    else:
        fraud_label = Label(gui, text="NOT FRAUD")
        fraud_label.config(font=("Courier", 60), bg='green')
        fraud_label.place(relx=0.5, rely=0.25, anchor=CENTER)
        button1 = Button(gui, text='False Negative ', fg='black', bg='#ff6961',
                         command=lambda: press('fn'), height=1, width=10)

        button2 = Button(gui, text=' True Negative ', fg='black', bg='light green',
                         command=lambda: press('tn'), height=1, width=10)

    button1.place(relx=0.45, rely=0.65, anchor=CENTER)
    button2.place(relx=0.55, rely=0.65, anchor=CENTER)

    button3 = Button(gui, text=' Wrong Side ', fg='black', bg='light yellow',
                     command=lambda: press('ws'), height=1, width=10)

    button3.place(relx=0.45, rely=0.75, anchor=CENTER)

    button4 = Button(gui, text=' Inconclusive ', fg='black', bg='light yellow',
                     command=lambda: press('inconclusive'), height=1, width=10)

    button4.place(relx=0.55, rely=0.75, anchor=CENTER)

    quitButton = Button(gui, text=' Quit ', fg='black', bg='light yellow',
                        command=lambda: pressQuit(), height=1, width=10)

    quitButton.place(relx=0.75, rely=0.25, anchor=CENTER)

    gui.mainloop()
    return result, reason, comments, quitApp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", help="Input path to metrics csv file")
    parser.add_argument("-m", "--metrics", help="metrics to display for analysis")
    parser.add_argument("-o", "--output", help="output for csv including false positives")
    parser.add_argument("-a", "--analysisType", nargs='?', help="analysis type, false pos or false neg")
    parser.add_argument("-s", "--start", nargs='?', const=1, help="start  rows to analyze")
    parser.add_argument("-e", "--end", nargs='?', help=" stop rows to analyze")
    parser.add_argument("-i", "--include_all", nargs='?', help="include all images")
    args = parser.parse_args()
    metrics = args.metrics.split(',')
    data = pd.read_csv(args.filepath)
    if args.end is None:
        stop = len(data)
        print(f"Stop: {stop}")
    else:
        stop = args.end
    data = data.loc[int(args.start):int(stop)]
    fp = False
    fn = False
    ia = False
    if args.analysisType == "falsepositive":
        fp = True
    elif args.analysisType == "falsenegative":
        fn = True
    if args.include_all == "True":
        ia = True

    data['result_classification'] = [None for i in range(0, len(data['filepath']))]
    data['reason'] = ['' for i in range(0, len(data['filepath']))]
    data['comments'] = ['' for i in range(0, len(data['filepath']))]

    fraud_c = 0
    for i, row in data.iterrows():
        result = None
        reason = None
        comments = ''
        quitApp = False
        if not os.path.exists(row['filepath']):
            print(f"The path to the image does not exist: {row['filepath']}")
            continue
        if fp and not row['is_fraud']:
            continue
        if fn and row['is_fraud']:
            continue
        if not ia and not row['fraud_logic_executed']:
            continue
        fraud_c += 1
        fraud = row['is_fraud']

        text = ""
        for m in metrics:
            text += f"\n{m}: {row[m]}\n"

        img_to_view = cv2.imread(row['filepath'])
        result, reason, comments, quitApp = main(fraud, None, text, img_to_view)

        if quitApp:
            print(f"Exiting application: left off on row {i}")
            break
        data.loc[i, 'result_classification'] = result
        data.loc[i, 'reason'] = reason
        if comments != '\n':
            data.loc[i, 'comments'] = comments[:-1]
        if not os.path.exists(args.output) or os.stat(args.output).st_size == 0:
            data.loc[[i]].to_csv(args.output, index=False, mode='a')
        else:
            data.loc[[i]].to_csv(args.output, index=False, header=False, mode='a')
