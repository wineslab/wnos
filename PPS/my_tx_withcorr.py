# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Test Corr And Sync Tx
# Generated: Fri Mar 10 18:45:31 2017
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import numpy
import sip
import sys
import time

# my own correlation module
import mycorr

# configuration file
import csi


class test_corr_and_sync_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Test Corr And Sync Tx")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Test Corr And Sync Tx")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "test_corr_and_sync_tx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = csi.sps
        self.nfilts = nfilts = 32
        self.eb = eb = 0.35
        self.samp_rate = samp_rate = csi.samp_rate
        
        self.preamble = preamble = csi.pn_used
        
        self.payload_size = payload_size = 992
        self.matched_filter = matched_filter = firdes.root_raised_cosine(nfilts, nfilts, 1, eb, int(11*sps*nfilts))
        self.gap = gap = 0
        self.gain = gain = csi.tx_gain
        self.freq = freq = csi.freq
        self.fine_freq = fine_freq = 0
        self.digital_gain = digital_gain = csi.digi_gain_tx
        self.constel = constel = digital.constellation_calcdist(([1,- 1]), ([0,1]), 2, 1).base()
        self.addr = addr = csi.tx_usrp_ip

        ##################################################
        # Blocks
        ##################################################
        self._gain_range = Range(0, 31.5, 0.5, 12.5, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "Tx Gain", "counter_slider", float)
        self.top_grid_layout.addWidget(self._gain_win, 2,0,1,1)
        self._freq_range = Range(1e9, 5e9, 100e3, 2.45e9, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "Tx Frequency", "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_win, 3,0,1,1)
        self._fine_freq_range = Range(-10e3, 10e3, 10, 0, 200)
        self._fine_freq_win = RangeWidget(self._fine_freq_range, self.set_fine_freq, "Fine Frequency", "counter_slider", float)
        self.top_grid_layout.addWidget(self._fine_freq_win, 3,1,1,1)
        self._digital_gain_range = Range(0, 200, 1, 45, 200)
        self._digital_gain_win = RangeWidget(self._digital_gain_range, self.set_digital_gain, "Digital Gain", "counter_slider", float)
        self.top_grid_layout.addWidget(self._digital_gain_win, 2,1,1,1)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join((addr, "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(freq+fine_freq, 0)
        self.uhd_usrp_sink_0.set_gain(gain, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	samp_rate, #bw
        	"QT GUI Plot", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-120, 20)
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_freq_sink_x_0.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 0,0,1,2)
        self.digital_psk_mod_0 = digital.psk.psk_mod(
          constellation_points=2,
          mod_code="none",
          differential=False,
          samples_per_symbol=sps,
          excess_bw=0.35,
          verbose=False,
          log=False,
          )
        #self.digital_correlate_and_sync_cc_0 = digital.correlate_and_sync_cc((preamble), (matched_filter), sps)
        self.digital_correlate_and_sync_cc_0 = mycorr.corrsync_cc((preamble), (matched_filter), sps, 250000)
        
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b(map(lambda x: (-x+1)/2, preamble), True, 1, [])
        self.blocks_stream_mux_0_0_0 = blocks.stream_mux(gr.sizeof_char*1, (len(preamble)/8,payload_size))
        self.blocks_stream_mux_0_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, ((len(preamble)+8*payload_size)*sps, gap))
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_null_source_0_0 = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((digital_gain, ))
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, 256, 100000)), True)
        
        #self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*1, "/home/wines-wnos/Dropbox/TBWNOS/gnucorrsync/data2.dat", False)
        #self.blocks_file_sink_1.set_unbuffered(False)	        

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_stream_mux_0_0_0, 1))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_freq_sink_x_0, 0))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.blocks_null_source_0_0, 0), (self.blocks_stream_mux_0_0, 1))    
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_stream_mux_0_0_0, 0))    
        self.connect((self.blocks_stream_mux_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))    
        self.connect((self.blocks_stream_mux_0_0_0, 0), (self.digital_psk_mod_0, 0))    
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_pack_k_bits_bb_0, 0))    
        self.connect((self.digital_correlate_and_sync_cc_0, 0), (self.blocks_null_sink_0, 0))    
        self.connect((self.digital_correlate_and_sync_cc_0, 1), (self.blocks_null_sink_0_0, 0))    
        self.connect((self.digital_psk_mod_0, 0), (self.blocks_stream_mux_0_0, 0))    
        #self.connect((self.digital_psk_mod_0, 0), (self.digital_correlate_and_sync_cc_0, 0))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.digital_correlate_and_sync_cc_0, 0)) 
        
        #self.connect((self.digital_correlate_and_sync_cc_0, 1), (self.blocks_file_sink_1, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "test_corr_and_sync_tx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_matched_filter(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1, self.eb, int(11*self.sps*self.nfilts)))

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_matched_filter(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1, self.eb, int(11*self.sps*self.nfilts)))

    def get_eb(self):
        return self.eb

    def set_eb(self, eb):
        self.eb = eb
        self.set_matched_filter(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1, self.eb, int(11*self.sps*self.nfilts)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

    def get_preamble(self):
        return self.preamble

    def set_preamble(self, preamble):
        self.preamble = preamble
        self.blocks_vector_source_x_0_0.set_data(map(lambda x: (-x+1)/2, self.preamble), [])

    def get_payload_size(self):
        return self.payload_size

    def set_payload_size(self, payload_size):
        self.payload_size = payload_size

    def get_matched_filter(self):
        return self.matched_filter

    def set_matched_filter(self, matched_filter):
        self.matched_filter = matched_filter

    def get_gap(self):
        return self.gap

    def set_gap(self, gap):
        self.gap = gap

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)
        	

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_sink_0.set_center_freq(self.freq+self.fine_freq, 0)

    def get_fine_freq(self):
        return self.fine_freq

    def set_fine_freq(self, fine_freq):
        self.fine_freq = fine_freq
        self.uhd_usrp_sink_0.set_center_freq(self.freq+self.fine_freq, 0)

    def get_digital_gain(self):
        return self.digital_gain

    def set_digital_gain(self, digital_gain):
        self.digital_gain = digital_gain
        self.blocks_multiply_const_vxx_0.set_k((self.digital_gain, ))

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel

    def get_addr(self):
        return self.addr

    def set_addr(self, addr):
        self.addr = addr


def main(top_block_cls=test_corr_and_sync_tx, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    #qapp.exec_()
    
    n = 1
    rslt = 0	
    while n < 100:
        tmp_rslt = tb.digital_correlate_and_sync_cc_0.get_corr_rslt()
		
        if n < 10:
            n += 1
        else:			
            rslt += tmp_rslt.real		
            print rslt/(n-9), '    ', tmp_rslt, '     ', tmp_rslt.real	
            n += 1
        time.sleep(0.5)


if __name__ == '__main__':
	
    #print gr.version()
    #exit(0)	
	
    main()
