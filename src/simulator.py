import functools
import math
import signal
import sys
import time
from typing import Optional, Tuple

from PyQt5 import Qt

from leo_channel import leo_channel

QTIMER_TIMEOUT = 1  # ms
SPEED_OF_LIGHT_IN_KM_S = 299_792_458 / 1_000  # km/s
EARTH_RADIUS_IN_KM = 6_371  # km
G = 6.67430e-11  # N m^2/kg^2
EARTH_MASS = 5.972e24  # kg


class LEOSatellite(object):
    altitude_in_km: float
    initial_position: float
    ue_position: float

    downlink_frequency: float
    uplink_frequency: float

    orbital_speed: float  # in km/s
    orbital_angular_speed: float  # in rad/s
    initial_epoch: Optional[float] = None
    initial_position: float
    current_position: float

    def _get_true_radius(self) -> float:
        return EARTH_RADIUS_IN_KM + self.altitude_in_km

    def _calculate_orbital_speed(self):
        G_ME = G * EARTH_MASS
        radius = self._get_true_radius()
        speed_in_m_s = math.sqrt(G_ME / (radius * 1000))
        self.orbital_speed = speed_in_m_s / 1000  # in km/s
        self.orbital_angular_speed = self.orbital_speed / radius

    def __init__(self,
                 altitude_in_km: float,
                 downlink_frequency: float,
                 uplink_frequency: float,
                 initial_position: float = 0,
                 ue_position: float = math.pi / 2):
        self.altitude_in_km = altitude_in_km
        self.current_position = self.initial_position = initial_position  # in radians
        self._calculate_orbital_speed()
        self.downlink_frequency = downlink_frequency
        self.uplink_frequency = uplink_frequency
        self.ue_position = ue_position

    def reset(self):
        self.current_position = 0.0
        self.initial_epoch = None

    def step(self):
        if self.initial_epoch is None:
            self.initial_epoch = time.time_ns()
        now = time.time_ns()
        elapsed_time = (now - self.initial_epoch) * 1e-9
        self.current_position = self.initial_position + self.orbital_angular_speed * elapsed_time
        self.current_position %= 2 * math.pi

    def get_orbital_speed(self) -> Tuple[float, float]:
        return self.orbital_speed, self.orbital_angular_speed

    def get_current_position(self) -> float:
        return self.current_position

    def _get_relative_angle(self) -> float:
        return self.ue_position - self.current_position

    def get_distance_to_ue(self) -> float:
        r = self._get_true_radius()
        theta = self._get_relative_angle()
        return math.sqrt(r ** 2 + EARTH_RADIUS_IN_KM ** 2 - 2 * r * EARTH_RADIUS_IN_KM * math.cos(theta))

    def get_relative_speed_to_ue(self) -> float:
        return self.orbital_speed * math.sin(self._get_relative_angle())

    def get_elevation_angle(self) -> float:
        theta = self._get_relative_angle()
        r = self._get_true_radius()
        return math.atan2(r * math.cos(theta) - EARTH_RADIUS_IN_KM, r * math.sin(theta))

    def _get_doppler_shift(self, frequency: float) -> float:
        return frequency * self.get_relative_speed_to_ue() / SPEED_OF_LIGHT_IN_KM_S

    def get_uplink_doppler_shift(self) -> float:
        return self._get_doppler_shift(self.uplink_frequency)

    def get_downlink_doppler_shift(self) -> float:
        return self._get_doppler_shift(self.downlink_frequency)

    def get_propagation_delay(self) -> float:
        return self.get_distance_to_ue() / SPEED_OF_LIGHT_IN_KM_S


def init_satellite(tb: leo_channel) -> LEOSatellite:
    return LEOSatellite(altitude_in_km=tb.get_sat_altitude(),
                        downlink_frequency=tb.get_dl_band_fc(),
                        uplink_frequency=tb.get_ul_band_fc(),
                        initial_position=0)


def qt_callback(tb: leo_channel, satellite: LEOSatellite):
    satellite.step()
    tb.set_prop_delay(satellite.get_propagation_delay())
    tb.set_doppler_freq(satellite.get_uplink_doppler_shift())  # TODO
    tb.set_doppler_freq(satellite.get_downlink_doppler_shift())


def main():
    qt_app = Qt.QApplication(sys.argv)

    tb = leo_channel()
    satellite = init_satellite(tb)
    satellite.reset()
    speed, angular_speed = satellite.get_orbital_speed()
    print(f"Orbital speed: {speed} km/s, {angular_speed} rad/s")

    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    callback = functools.partial(qt_callback, tb=tb, satellite=satellite)

    timer = Qt.QTimer()
    timer.setTimerType(Qt.Qt.PreciseTimer)
    timer.timeout.connect(callback)
    timer.start(QTIMER_TIMEOUT)

    qt_app.exec_()


if __name__ == '__main__':
    main()