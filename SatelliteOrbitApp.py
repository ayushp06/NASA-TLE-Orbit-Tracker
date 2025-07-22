import sys
import numpy as np
from skyfield.api import load
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SatWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Satellite Orbit")
        
        self.sat_layout = QVBoxLayout()
        self.sat_comboBox =  QComboBox()
        self.sat_button1 = QPushButton("Generate Orbit")
        self.sat_button2 = QPushButton("Remove Orbit")
        self.sat_widget = QWidget()
        self.sat_widget.setLayout(self.sat_layout)
        self.setCentralWidget(self.sat_widget)
        self.sat_layout.addWidget(self.sat_comboBox)
        self.sat_layout.addWidget(self.sat_button1)
        self.sat_layout.addWidget(self.sat_button2)
        
        self.plot_canvases = []
        
        self.sat_widget.setStyleSheet("font-size: 16px; padding: 5px 5px;")
        self.sat_comboBox.setStyleSheet("font-size: 16px; padding: 5px 5px;")
        
        url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'

        satellites = load.tle_file(url)

        self.sat_lib = {}
        for sat in satellites:
            self.sat_lib[sat.name] = sat
            
        self.sat_button1.clicked.connect(self.generateOrbit)
        self.sat_button2.clicked.connect(self.clearPlot)
        self.sat_comboBox.addItems(list(self.sat_lib.keys())[:50])
            
    def generateOrbit(self):
        sat_name = self.sat_comboBox.currentText()
        sat = self.sat_lib[sat_name]
        
        time_scale = load.timescale()
        time_0 = time_scale.now()
        array_time = np.arange(0, 90, 1)
        array_time = array_time * (1/1440)
        time = time_0 + array_time

        geocentric = sat.at(time)
        pos = geocentric.position.km
        
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.figure_canvas = FigureCanvas(self.figure)
        self.sat_layout.addWidget(self.figure_canvas)
        
        self.plot_canvases.append(self.figure_canvas)

        x_pos = pos[0]
        y_pos = pos[1]
        z_pos = pos[2]

        radius = 6371
            
        u, v = np.mgrid[0:2*np.pi:100j, 0:np.pi:100j]
        x = radius * np.cos(u) * np.sin(v)
        y = radius * np.sin(u) * np.sin(v)
        z = radius * np.cos(v)

        self.ax.plot_surface(x, y, z, color='b', alpha=0.4, linewidth=0)
        self.ax.plot3D(x_pos, y_pos, z_pos, 'r')
        self.ax.scatter(x_pos[0], y_pos[0], z_pos[0], color='red', s=50, label='Current Position')
        self.ax.set_title(sat_name)
        self.ax.legend()
        
        self.figure_canvas.draw()
        
        self.orbit_plot, = self.ax.plot3D(x_pos, y_pos, z_pos, 'r')
        self.sat_dot = self.ax.scatter(x_pos[0], y_pos[0], z_pos[0], color='red', s=50, label='Current Position')
        
    def clearPlot(self):
        if self.plot_canvases:
            recent_canvas = self.plot_canvases.pop()
            self.sat_layout.removeWidget(recent_canvas)
            recent_canvas.setParent(None)

if __name__ == "__main__":
    SatApp = QApplication(sys.argv)
    sat_window = SatWindow()
    sat_window.show()
    sys.exit(SatApp.exec_())