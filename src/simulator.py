import functools
import signal
import sys
from optparse import OptionParser

from PyQt5 import Qt

import utils
from leo_channel import leo_channel
from satellites import LEOSatellite
from ui import OrbitingWidget

QTIMER_TIMEOUT = 1  # ms

DEFAULT_DL_FREQ = 2.68 * 1e9  # Default downlink frequency, GHz
DEFAULT_UL_FREQ = 2.53 * 1e9  # Default uplink frequency, GHz
DEFAULT_SATELLITE_ALTITUDE = 600  # Default satellite altitude in km
DEFAULT_SATELLITE_LOCATION = 0  # Default satellite location, in degrees

timer = 0


def init_satellite(tb: leo_channel,
                   dl_freq: int, ul_freq: int,
                   sat_altitude: int, sat_init_pos: int) -> LEOSatellite:
    initial_position = utils.degrees_to_radians(sat_init_pos)
    tb.set_sat_altitude(sat_altitude)
    tb.set_dl_band_fc(dl_freq)
    tb.set_ul_band_fc(ul_freq)
    return LEOSatellite(altitude_in_km=sat_altitude,
                        downlink_frequency=dl_freq,
                        uplink_frequency=ul_freq,
                        initial_position=initial_position)


def qt_callback(tb: leo_channel, orbit_view: OrbitingWidget, satellite: LEOSatellite):
    global timer
    satellite.step()
    delay = satellite.get_propagation_delay()
    tb.set_prop_delay_us(delay * 1e6)  # to microseconds
    # tb.set_prop_delay(0)
    tb.set_prop_delay(utils.get_delay_in_samples(delay, tb.get_samp_rate()))
    tb.set_doppler_freq_ul(satellite.get_uplink_doppler_shift())
    tb.set_doppler_freq_dl(satellite.get_downlink_doppler_shift())
    tb.set_relative_speed_label(satellite.get_relative_speed_to_ue())

    # Display satellite and UE information
    tb.set_satellite_location(utils.radians_to_degrees(satellite.get_current_position()))
    speed, angular_speed = satellite.get_orbital_speed()
    tb.set_orbiting_speed(speed)
    tb.set_ue_location(utils.radians_to_degrees(satellite.get_ue_location()))
    tb.set_elevation_angle(utils.radians_to_degrees(satellite.get_elevation_angle()))
    tb.set_distance_to_ue(satellite.get_distance_to_ue())

    if (timer % 1000) == 0:
        orbit_view.update()

    timer += 1


def main():
    parser = OptionParser()
    parser.add_option("--dl_freq", dest="dl_freq", type="float", default=DEFAULT_DL_FREQ,
                      help="Set the downlink frequency in Hz)")
    parser.add_option("--ul_freq", dest="ul_freq", type="float", default=DEFAULT_UL_FREQ,
                      help="Set the uplink frequency in Hz)")
    parser.add_option("--sat_altitude", dest="sat_altitude", type="float", default=DEFAULT_SATELLITE_ALTITUDE,
                      help="Set the satellite altitude in KM")
    parser.add_option("--sat_init_pos", dest="sat_init_pos", type="float", default=DEFAULT_SATELLITE_LOCATION,
                      help="Set the initial position of the satellite in degrees")
    (opts, args) = parser.parse_args()
    qt_app = Qt.QApplication(sys.argv)

    tb = leo_channel()
    satellite = init_satellite(tb,
                               opts.dl_freq, opts.ul_freq,
                               opts.sat_altitude, opts.sat_init_pos)
    satellite.reset()

    plot_window = OrbitingWidget(satellite)
    plot_window.show()

    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    callback = functools.partial(qt_callback,
                                 tb=tb,
                                 orbit_view=plot_window,
                                 satellite=satellite)

    timer = Qt.QTimer()
    timer.setTimerType(Qt.Qt.PreciseTimer)
    timer.timeout.connect(callback)
    timer.start(QTIMER_TIMEOUT)

    qt_app.exec_()


if __name__ == '__main__':
    main()
