import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl


class Visualizer:
    def __init__(self, title, pos=(100, 100), winSize=(500, 400)):
        top, left = pos
        width, height = winSize
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        self.window.setGeometry(top, left, width, height)

        self.layout = QVBoxLayout()
        self.centralWidget = QWidget(self.window)
        self.centralWidget.setLayout(self.layout)
        self.window.setCentralWidget(self.centralWidget)


class LidarPCDVisualizer(Visualizer):
    def __init__(self, plotCfg):   
        super().__init__(plotCfg['title'], plotCfg['pos'], plotCfg['winSize'])

        self.viewWidget = gl.GLViewWidget()
        self.viewWidget.opts['viewRect'] = (plotCfg['xRange'][0], plotCfg['yRange'][0], plotCfg['xRange'][1], plotCfg['yRange'][1])
        self.layout.addWidget(self.viewWidget)

        self.scatter = gl.GLScatterPlotItem(size=plotCfg['dotSize'])
        self.viewWidget.addItem(self.scatter)
        self.viewWidget.addItem(gl.GLGridItem())

    def plot_point_cloud(self, points):
        self.scatter.setData(pos=points)
        self.window.show()


class RadarPlotVisualizer(Visualizer):
    def __init__(self, plotCfg):
        super().__init__(plotCfg['title'], plotCfg['pos'], plotCfg['winSize'])

        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.view = pg.PlotItem()
        self.view.setLabel('left', plotCfg['xLabel'], units=plotCfg['xUnit'])
        self.view.setLabel('bottom', plotCfg['yLabel'], units=plotCfg['yUnit'])
        self.plotWidget.addItem(self.view)

        self.img = pg.ImageView(parent=self.centralWidget, view=self.view)
        # self.img.show()
        self.img.ui.roiBtn.hide()
        self.img.ui.menuBtn.hide()
        #img.ui.histogram.hide()
        self.img.getHistogramWidget().gradient.loadPreset('flame')
        self.img.setGeometry(0, 0, plotCfg['winSize'][0], plotCfg['winSize'][1])

    def plot_depth_fig(self, data, pos, scale):
        self.img.setImage(data.T, pos=pos, scale=scale)
        self.view.setAspectLocked(False)
        self.view.invertY(False)
        pg.QtGui.QGuiApplication.processEvents()
        self.window.show()


class CameraImgVisualizer(Visualizer):
    def __init__(self, plotCfg):
        super().__init__(plotCfg['title'], plotCfg['pos'], plotCfg['winSize'])

        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.view = pg.PlotItem()
        self.plotWidget.addItem(self.view)

        self.img = pg.ImageView(parent=self.centralWidget, view=self.view)
        # self.img.show()
        self.img.ui.roiBtn.hide()
        self.img.ui.menuBtn.hide()
        self.img.ui.histogram.hide()
        # self.img.getHistogramWidget().gradient.loadPreset('flame')
        self.img.setGeometry(0, 0, plotCfg['winSize'][0], plotCfg['winSize'][1])

    def show_img(self, img):
        self.img.setImage(img.T)
        self.view.setAspectLocked(True)
        pg.QtGui.QGuiApplication.processEvents()
        self.window.show()


class ScatterPointsVisualizer(Visualizer):
    def __init__(self, plotCfg):
        super().__init__(plotCfg['title'], plotCfg['pos'], plotCfg['winSize'])

        self.xlim = plotCfg['xlim']
        self.ylim = plotCfg['ylim']
        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(color=plotCfg['penColor'], width=plotCfg['penWidth']), symbol=plotCfg['symbol'], size=plotCfg['dotSize'])
        self.plotWidget.addItem(self.scatter)

    def plot_scatter(self, x, y):
        self.scatter.setData(x, y)
        self.plotWidget.setXRange(self.xlim[0], self.xlim[1])
        self.plotWidget.setYRange(self.ylim[0], self.ylim[1])
        self.window.show()

