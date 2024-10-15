import math

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from satellites import EARTH_RADIUS_IN_KM, LEOSatellite


class OrbitingWidget(QWidget):
    satellite: LEOSatellite
    ax: plt.Axes
    canvas: FigureCanvas
    earth: plt.Circle
    satellite_orbit: plt.Circle
    ue_dot: None

    def __init__(self, satellite: LEOSatellite, parent=None):
        super().__init__(parent)
        self.satellite = satellite
        self._initialize_ui()

    def _get_orbit_radius(self) -> float:
        return EARTH_RADIUS_IN_KM + self.satellite.get_altitude()

    def _initialize_canvas(self) -> None:
        limit = EARTH_RADIUS_IN_KM + self.satellite.get_altitude()
        limit *= 1.2
        self.canvas = FigureCanvas(Figure(figsize=(10, 10)))
        self.ax = self.canvas.figure.subplots()
        self.ax.grid(True)
        # self.ax.set_xlim(-2000, 2000)
        self.ax.set_xlim(-limit, limit)
        # self.ax.set_ylim(4000, 8000)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_aspect('equal', 'box')

    def _initialize_components(self) -> None:
        center = (0, 0)
        self.earth = plt.Circle(center, EARTH_RADIUS_IN_KM, color='blue', fill=False, linestyle='dashed')
        self.earth.set_label('Earth')
        self.satellite_orbit = plt.Circle(center, self._get_orbit_radius(), color='red', fill=False)
        self.satellite_orbit.set_label('Satellite Orbit')
        self.ax.add_artist(self.earth)
        self.ax.add_artist(self.satellite_orbit)

        ue_location = self.satellite.get_ue_location()
        self.ue_dot, = self.ax.plot(EARTH_RADIUS_IN_KM * math.cos(ue_location),
                                    EARTH_RADIUS_IN_KM * math.sin(ue_location),
                                    'bo')
        self.ue_dot.set_label('UE')

        self.satellite_dot, = self.ax.plot([], [], 'ro')
        self.satellite_dot.set_label('Satellite')

        self.ax.legend()

    def _initialize_ui(self) -> None:
        self.setWindowTitle('LEO Satellite Emulator')
        layout = QVBoxLayout(self)
        self._initialize_canvas()
        layout.addWidget(self.canvas)
        self._initialize_components()

    def update(self) -> None:
        pos = self.satellite.get_current_position()
        radius = self._get_orbit_radius()
        self.satellite_dot.set_data([radius * math.cos(pos)], [radius * math.sin(pos)])
        self.canvas.draw_idle()
