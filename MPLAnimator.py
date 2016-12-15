import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5 import QtWidgets, QtGui
from PyQt5.Qt import Qt

import tempfile
import os

# imports currently only for type-hinting
import matplotlib.backend_bases




class Animator:

    def __init__(self, name = None, setup_handle = None):
        self.qApp = QtWidgets.QApplication([])

        self.w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.w.setLayout(layout)

        self.stack = QtWidgets.QStackedLayout()
        layout.addLayout(self.stack)

        self.label = QtWidgets.QLabel()
        self.stack.addWidget(self.label)
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.stack.addWidget(self.canvas)

        self.canvas.mpl_connect('button_press_event', self.mouseFun)

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.visualize)
        layout.addWidget(self.slider)

        self.prerender_checkbox = QtWidgets.QCheckBox("Prerendered")
        layout.addWidget(self.prerender_checkbox)

        self.prerendered = None

        self.name = name
        if name == None:
            self.tmpdir = tempfile.TemporaryDirectory()
            self.dir = self.tmpdir.name
            self.name = 'animator_'+self.dir
        else:
            self.dir = ".prerendered/" + name
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)

        if setup_handle != None:
            setup_handle()

    def setFrameCallback(self, frame_handle, max_frame):
        self.frame_handle = frame_handle
        self.max_frame = max_frame
        self.slider.setMaximum(max_frame - 1)

    def setClickCallback(self, click_cb):
        self.click_cb = click_cb

    def rerender(self):
        self.clear()
        self.prerender()

    def prerender(self):
        if len(os.listdir(self.dir)) == 0:
            print("prerendering images...")
            for i in range(self.max_frame):
                print("rendering frame {}/{}".format(i + 1, self.max_frame))
                self.frame_handle(i)
                plt.savefig("{}/{}.png".format(self.dir, i))

    def mouseFun(self, event: matplotlib.backend_bases.MouseEvent):
        self.click_cb(**(event.__dict__))
        self.visualize()


    def visualize(self, i = None):
        if i == None:
            i = self.slider.value()
        if self.prerender_checkbox.isChecked():
            if not self.prerendered:
                self.prerender()
            if self.stack.currentWidget() != self.label:
                self.stack.setCurrentWidget(self.label)
            pm = QtGui.QPixmap("{}/{}.png".format(self.dir, i))
            self.label.setPixmap(pm)
        else:
            if self.stack.currentWidget() != self.canvas:
                self.stack.setCurrentWidget(self.canvas)
            self.frame_handle(i)
            self.canvas.draw()

    def clear(self):
        for file in os.listdir(self.dir):
            os.remove(self.dir + "/" + file)

    def run(self, clear = False, prerendered = True, initialFrame = 0):
        if clear:
            self.clear()
        if prerendered:
            self.prerender()

        self.prerendered = prerendered
        self.prerender_checkbox.setChecked(prerendered)

        self.w.show()
        self.visualize(initialFrame)
        self.slider.setValue(initialFrame)
        self.qApp.exec()
