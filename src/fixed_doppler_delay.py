import signal
import sys
from optparse import OptionParser

import utils
from PyQt5 import Qt

from leo_channel import leo_channel

DEFAULT_DOPPLER_FREQ = 0
DEFAULT_PROP_DELAY = 0
DEFAULT_DL_FREQ = 2.68 * 1e9  # Default downlink frequency, GHz
DEFAULT_UL_FREQ = 2.53 * 1e9  # Default uplink frequency, GHz
DEFAULT_NOISE_VOLTAGE = 0.0  # Default noise power in voltage


def main():
    qt_app = Qt.QApplication(sys.argv)

    parser = OptionParser()
    parser.add_option("--dl_freq", dest="dl_freq", type="float", default=DEFAULT_DL_FREQ,
                      help="Set the downlink frequency in Hz)")
    parser.add_option("--ul_freq", dest="ul_freq", type="float", default=DEFAULT_UL_FREQ,
                      help="Set the uplink frequency in Hz)")
    parser.add_option("-d", "--doppler_freq", dest="doppler_freq", type="float", default=DEFAULT_DOPPLER_FREQ,
                      help="Set the doppler frequency (in Hz)")
    parser.add_option("-p", "--prop_delay", dest="prop_delay", type="float", default=DEFAULT_PROP_DELAY,
                      help="Set the propagation delay (in μs)")
    parser.add_option("-n", "--noise_voltage", dest="noise_voltage", type="float", default=DEFAULT_NOISE_VOLTAGE,
                      help="Set the noise power in voltage")

    (options, args) = parser.parse_args()

    tb = leo_channel()
    tb.set_prop_delay(utils.get_delay_in_samples(options.prop_delay, tb.get_samp_rate()))
    tb.set_dl_band_fc(options.dl_freq)
    tb.set_ul_band_fc(options.ul_freq)
    tb.set_doppler_freq_dl(options.doppler_freq)
    tb.set_doppler_freq_ul(options.doppler_freq)
    tb.set_noise_voltage(options.noise_voltage)

    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qt_app.exec_()


if __name__ == '__main__':
    main()
