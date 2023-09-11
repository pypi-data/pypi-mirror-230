import datetime as dt
import math
import os
import struct
import time
import unittest
import comtrade
from comtrade import Comtrade


COMTRADE_SAMPLE_1_CFG = """STATION_NAME,EQUIPMENT,2001
2,1A,1D
1, IA              ,,,A,2.762,0,0, -32768,32767,1,1,S
1, Diff Trip A     ,,,0
60
0
0,2
01/01/2000, 10:30:00.228000
 01/01/2000,10:30:00.722000
ASCII
1
"""

COMTRADE_SAMPLE_1_CFG_LAZY = """,,1999
2,1A,1D
1,,,,A,2.762,0,0, -32768,32767,1,1,S
1,,,,

0
0,2
,

ASCII
1
"""


COMTRADE_SAMPLE_1_DAT = "1, 0, 0,0\n2,347,-1,1\n"


COMTRADE_SAMPLE_3_CFG = """STATION_NAME,EQUIPMENT,2013
2,1A,1D
1, Signal,,,A,1,0,0,-1,1,1,1,S
1, Status,,,0
60
0
0,{samples}
01/01/2019,00:00:00.000000000
01/01/2019,00:00:{seconds:012.9f}
{format}
1
"""

COMTRADE_SAMPLE_4_CFG_FILE = "tests/sample_files/sample_bin.cfg"
COMTRADE_SAMPLE_4_DAT_FILE = "tests/sample_files/sample_bin.dat"


class TestTimestamp(unittest.TestCase):
    """Test timestamp parsing."""

    def test_complete_date(self):
        complete_date = "01/01/2000"
        day, month, year = comtrade._get_date(complete_date)
        self.assertEqual(day, 1)
        self.assertEqual(month, 1)
        self.assertEqual(year, 2000)

    def test_complete_time(self):
        complete_time = "10:30:00.228000"
        hour, minute, second, microsecond, \
            in_nanoseconds = comtrade._get_time(complete_time)
        self.assertEqual(hour, 10)
        self.assertEqual(minute, 30)
        self.assertEqual(second, 0)
        self.assertEqual(microsecond, 228000)
        self.assertFalse(in_nanoseconds)

    def test_incomplete_fraction_time(self):
        incomplete_fraction_time = "00:00:00.23"
        hour, minute, second, microsecond, \
            in_nanoseconds = comtrade._get_time(incomplete_fraction_time)
        self.assertEqual(hour, 0)
        self.assertEqual(minute, 0)
        self.assertEqual(second, 0)
        self.assertEqual(microsecond, 230000)
        self.assertFalse(in_nanoseconds)

    def test_nanoseconds(self):
        nanoseconds = "00:00:00.123456789"
        ignore_warnings = True
        hour, minute, second, microsecond, \
            in_nanoseconds = comtrade._get_time(nanoseconds, ignore_warnings)
        self.assertEqual(hour, 0)
        self.assertEqual(minute, 0)
        self.assertEqual(second, 0)
        self.assertEqual(microsecond, 123456)  # s the decimal .789
        self.assertTrue(in_nanoseconds)

    def test_incomplete_seconds(self):
        incomplete_seconds = "01:02:3.012345"
        ignore_warnings = True
        hour, minute, second, microsecond, \
            in_nanoseconds = comtrade._get_time(incomplete_seconds, ignore_warnings)
        self.assertEqual(hour, 1)
        self.assertEqual(minute, 2)
        self.assertEqual(second, 3)
        self.assertEqual(microsecond, 12345)  # s the decimal .789
        self.assertFalse(in_nanoseconds)


class TestCfg1Reading(unittest.TestCase):
    """String CFG and DAT 1999 pair test case."""
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.read(COMTRADE_SAMPLE_1_CFG, COMTRADE_SAMPLE_1_DAT)

    def test_station(self):
        self.assertEqual(self.comtrade.station_name, "STATION_NAME")

    def test_rec_dev_id(self):
        self.assertEqual(self.comtrade.rec_dev_id, "EQUIPMENT")

    def test_rev_year(self):
        self.assertEqual(self.comtrade.rev_year, "2001")

    def test_1a(self):
        self.assertEqual(self.comtrade.analog_count, 1)

    def test_1d(self):
        self.assertEqual(self.comtrade.status_count, 1)

    def test_2c(self):
        self.assertEqual(self.comtrade.channels_count, 2)

    def test_frequency(self):
        self.assertEqual(float(self.comtrade.frequency), 60.0)

    def test_total_samples(self):
        self.assertEqual(self.comtrade.total_samples, 2)

    def test_timestamp(self):
        self.assertEqual(self.comtrade.start_timestamp, 
                         dt.datetime(2000, 1, 1, 10, 30, 0, 228000, None))

        self.assertEqual(self.comtrade.trigger_timestamp, 
                         dt.datetime(2000, 1, 1, 10, 30, 0, 722000, None))

    def test_time_base(self):
        self.assertEqual(self.comtrade.time_base,
                         self.comtrade.cfg.TIME_BASE_MICRO_SEC)

    def test_ft(self):
        self.assertEqual(self.comtrade.ft, "ASCII")


class TestCfg1LazyReading(unittest.TestCase):
    """String CFG and DAT 1999 pair test case, abusing missing values in CFG."""
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.read(COMTRADE_SAMPLE_1_CFG_LAZY, COMTRADE_SAMPLE_1_DAT)

    def test_station(self):
        self.assertEqual(self.comtrade.station_name, "")

    def test_rec_dev_id(self):
        self.assertEqual(self.comtrade.rec_dev_id, "")

    def test_rev_year(self):
        self.assertEqual(self.comtrade.rev_year, "1999")

    def test_1a(self):
        self.assertEqual(self.comtrade.analog_count, 1)

    def test_1d(self):
        self.assertEqual(self.comtrade.status_count, 1)

    def test_2c(self):
        self.assertEqual(self.comtrade.channels_count, 2)

    def test_frequency(self):
        self.assertEqual(float(self.comtrade.frequency), 0.0)

    def test_total_samples(self):
        self.assertEqual(self.comtrade.total_samples, 2)

    def test_timestamp(self):
        self.assertEqual(self.comtrade.start_timestamp,
                         dt.datetime(1, 1, 1, 0, 0, 0, 0, None))

        self.assertEqual(self.comtrade.trigger_timestamp,
                         dt.datetime(1, 1, 1, 0, 0, 0, 0, None))

    def test_time_base(self):
        self.assertEqual(self.comtrade.time_base,
                         self.comtrade.cfg.TIME_BASE_MICRO_SEC)

    def test_ft(self):
        self.assertEqual(self.comtrade.ft, "ASCII")


class TestCffReading(unittest.TestCase):
    """CFF 2013 file test case."""
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load("tests/sample_files/sample_ascii.cff")

    def test_station(self):
        self.assertEqual(self.comtrade.station_name, "SMARTSTATION")

    def test_rec_dev_id(self):
        self.assertEqual(self.comtrade.rec_dev_id, "IED123")

    def test_rev_year(self):
        self.assertEqual(self.comtrade.rev_year, "2013")

    def test_1a(self):
        self.assertEqual(self.comtrade.analog_count, 4)

    def test_1d(self):
        self.assertEqual(self.comtrade.status_count, 4)

    def test_2c(self):
        self.assertEqual(self.comtrade.channels_count, 8)

    def test_frequency(self):
        self.assertEqual(float(self.comtrade.frequency), 60.0)

    def test_total_samples(self):
        self.assertEqual(self.comtrade.total_samples, 40)

    def test_time_base(self):
        self.assertEqual(self.comtrade.time_base,
                         self.comtrade.cfg.TIME_BASE_MICRO_SEC)

    def test_ft(self):
        self.assertEqual(self.comtrade.ft, "ASCII")

    def test_hdr(self):
        self.assertEqual(self.comtrade.hdr, "")

    def test_inf(self):
        self.assertEqual(self.comtrade.inf, "")


class TestCfg2Reading(TestCffReading):
    """CFG and DAT 2013 file pair test case (same content as the CFF test).
    """
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load("tests/sample_files/sample_ascii.cfg")

    def test_hdr(self):
        self.assertIsNone(self.comtrade.hdr)

    def test_inf(self):
        self.assertIsNone(self.comtrade.inf)


class TestCfgWithSubCharsReading(TestCfg2Reading):
    """CFG and DAT 2013 file pair test case, but cfg has <sub> characters.
    """
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True).load("tests/sample_files/sample_sub_char.cfg",
                                                            "tests/sample_files/sample_ascii.dat")


class TestCffFloat32Reading(unittest.TestCase):
    """Sample CFF file with float32 .dat contents.
    """
    def setUp(self):
        self.comtrade = comtrade.load("tests/sample_files/sample_float32.cff",
                                      ignore_warnings=True)

    def test_hdr(self):
        self.assertEqual(len(self.comtrade.hdr.split("\n")), 4)

    def test_inf(self):
        self.assertEqual(len(self.comtrade.inf.split("\n")), 1)

    def test_cfg(self):
        self.assertEqual(self.comtrade.station_name, "EXAMPLE")
        self.assertEqual(self.comtrade.rec_dev_id, "example")
        self.assertEqual(self.comtrade.analog_count, 1)
        self.assertEqual(self.comtrade.status_count, 1)


class TestCfgAsciiEncodingReading(TestCffReading):
    """CFG and DAT 2013 file pair test case (same content as the CFF test), but
    this time with the file using ASCII text encoding.
    """
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load("tests/sample_files/sample_ascii_utf-8.cfg", "tests/sample_files/sample_ascii.dat")

    def test_hdr(self):
        self.assertIsNone(self.comtrade.hdr)

    def test_inf(self):
        self.assertIsNone(self.comtrade.inf)

    def test_station(self):
        self.assertEqual(self.comtrade.station_name, "SMARTSTATION testing text encoding: hgvcj터파크387")


class TestBinaryReading(unittest.TestCase):
    dat_format = comtrade._TYPE_BINARY
    filename = "temp_binary"

    def parseAnalog(self, analog_value):
        return int(analog_value)

    def getFormat(self):
        if struct.calcsize("L") == 4:
            return 'Lf h H'
        else:
            return 'If h H'

    def setUp(self):
        # Sample auto-generated Comtrade file.
        timebase = 1e+6 # seconds to microseconds
        timemult = 1
        max_time = 2
        self.samples = 10000
        sample_freq = max_time / self.samples
        # Create temporary cfg file.
        cfg_contents = COMTRADE_SAMPLE_3_CFG.format(samples=self.samples,
                                                    seconds=max_time,
                                                    format=self.dat_format)
        file_path = os.path.abspath("tests/{}.cfg".format(self.filename))
        with open(file_path, 'w') as file:
            file.write(cfg_contents)

        # Struct object to write data.
        datawriter = struct.Struct(self.getFormat())

        # Create temporary binary dat file, with one analog and one status
        # channel.
        max_time = 2.0

        def analog(t: float) -> float:
            return math.cos(2*math.pi*60*t)*100

        def status(t: float) -> bool:
            return t > max_time/2.0 and 1 or 0

        file_path = os.path.abspath("tests/{}.dat".format(self.filename))
        with open(file_path, 'wb') as file:
            for isample in range(0, self.samples):
                t = isample * sample_freq
                t_us = t * timebase * timemult
                y_analog = self.parseAnalog(analog(t))
                y_status = status(t)
                file.write(datawriter.pack(isample +1, t_us, y_analog, y_status))

        # Load file
        file_path = os.path.abspath("tests/{}".format(self.filename))
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load(file_path + ".cfg".format(self.filename))

    def tearDown(self):
        # Remove temporary files.
        os.remove("tests/{}.cfg".format(self.filename))
        os.remove("tests/{}.dat".format(self.filename))

    def test_total_samples(self):
        self.assertEqual(self.comtrade.total_samples,   self.samples)
        self.assertEqual(len(self.comtrade.analog[0]),  self.samples)
        self.assertEqual(len(self.comtrade.status[0]), self.samples)
        self.assertEqual(len(self.comtrade.time),       self.samples)

    def test_analog_channels(self):
        self.assertEqual(self.comtrade.analog_count, 1)
        self.assertEqual(len(self.comtrade.analog), 1)

    def test_status_channels(self):
        self.assertEqual(self.comtrade.status_count, 1)
        self.assertEqual(len(self.comtrade.status), 1)

    def test_max_analog_value(self):
        tolerance = 2
        self.assertLessEqual(100 - max(self.comtrade.analog[0]), 2)

    def test_last_status_value(self):
        self.assertEqual(self.comtrade.status[0][-1], 1)

    def test_timestamps(self):
        self.assertEqual(self.comtrade.start_timestamp, 
                         dt.datetime(2019, 1, 1, 0, 0, 0, 0, None))
        self.assertEqual(self.comtrade.trigger_timestamp, 
                         dt.datetime(2019, 1, 1, 0, 0, 2, 0, None))

    def test_time_base(self):
        self.assertEqual(self.comtrade.time_base,
                         self.comtrade.cfg.TIME_BASE_NANO_SEC)

    def test_ft(self):
        self.assertEqual(self.comtrade.ft, self.dat_format)


class TestBinary32Reading(TestBinaryReading):
    dat_format = comtrade._TYPE_BINARY32
    filename = "temp_binary32"

    def parseAnalog(self, analog_value):
        return int(analog_value)

    def getFormat(self):
        if struct.calcsize("L") == 4:
            return 'Lf l H'
        else:
            return 'If i H'


class TestFloat32Reading(TestBinaryReading):
    dat_format = comtrade._TYPE_FLOAT32
    filename = "temp_float32"

    def parseAnalog(self, analog_value):
        return int(analog_value)

    def getFormat(self):
        if struct.calcsize("L") == 4:
            return 'Lf f H'
        else:
            return 'If f H'


class TestRealBinaryReading(unittest.TestCase):
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load(COMTRADE_SAMPLE_4_CFG_FILE,
                           COMTRADE_SAMPLE_4_DAT_FILE)

    def test_value_conversion(self):
        va_4 = -23425 * 0.000361849
        self.assertAlmostEqual(va_4, self.comtrade.analog[0][3], places=6)

    def test_values(self):
        va = self.comtrade.analog[0][0]
        vb = self.comtrade.analog[1][0]
        vc = self.comtrade.analog[2][0]
        vn = self.comtrade.analog[3][0]
        # sum of phase-ground voltages is approximately 0
        self.assertAlmostEqual(0.0, va + vb + vc + vn, 1)

    def test_time(self):
        time_diff = self.comtrade.time[2] - self.comtrade.time[1]
        sample_rate = self.comtrade.cfg.sample_rates[0][0]
        self.assertAlmostEqual(1.0 / sample_rate, time_diff)


class TestEncodingHandling(unittest.TestCase):
    def test_loading_utf8(self):
        obj = comtrade.load(
            "tests/sample_files/sample_ascii_utf-8.cfg",
            "tests/sample_files/sample_ascii.dat",
            encoding="utf-8",
        )
        self.assertEqual(obj.cfg.station_name, "SMARTSTATION testing text encoding: hgvcj터파크387")
        self.assertEqual(obj.cfg.rec_dev_id, "IED123")

    def test_loading_iso8859_1(self):
        obj = comtrade.load("tests/sample_files/sample_iso8859-1.cfg", encoding="iso-8859-1")
        self.assertEqual(obj.cfg.station_name, "Estação de Medição")
        self.assertEqual(obj.cfg.rec_dev_id, "Oscilógrafo")
    
    def test_loading_iso8859_1_bin(self):
        obj = comtrade.load("tests/sample_files/sample_iso8859-1_bin.cfg", encoding="iso-8859-1")
        self.assertEqual(obj.cfg.station_name, "Estação de Medição")
        self.assertEqual(obj.cfg.rec_dev_id, "Oscilógrafo")
 

class TestExtensionCaseHandling(unittest.TestCase):
    def test_lower_case(self):
        self.assertEqual(comtrade._get_same_case(".cfg", ".dat"), ".dat")

    def test_upper_case(self):
        self.assertEqual(comtrade._get_same_case(".CFG", ".dat"), ".DAT")

    def test_capitalized(self):
        self.assertEqual(comtrade._get_same_case(".Cfg", ".dat"), ".Dat")


class TestCfgAsciiMissingDataReading(TestCfgAsciiEncodingReading):
    """CFG and DAT 2013 file pair test case (same content as the CFF test), but
    this time with the file using ASCII text encoding and empty strings (missing data) on dat file.
    """
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load("tests/sample_files/sample_ascii.cfg", "tests/sample_files/sample_ascii_missing.dat")

    def test_station(self):
        pass

    def test_known_missing_values(self):
        self.assertTrue(math.isnan(self.comtrade.analog[0][1]))
        self.assertTrue(math.isnan(self.comtrade.analog[1][2]))
        self.assertTrue(math.isnan(self.comtrade.analog[2][3]))
        self.assertTrue(math.isnan(self.comtrade.analog[3][4]))


class TestCfgBinaryMissingDataReading(unittest.TestCase):
    """Binary dat file with missing data (0xFFFF values)."""
    def setUp(self):
        self.comtrade = Comtrade(ignore_warnings=True)
        self.comtrade.load("tests/sample_files/sample_bin.cfg", "tests/sample_files/sample_bin_missing.dat")

    def test_known_missing_values(self):
        self.assertTrue(math.isnan(self.comtrade.analog[0][0]))
        self.assertTrue(math.isnan(self.comtrade.analog[1][1]))
        self.assertTrue(math.isnan(self.comtrade.analog[2][2]))
        self.assertTrue(math.isnan(self.comtrade.analog[3][3]))


class TestDoublePrecisionHandling(unittest.TestCase):
    def test_should_use_single_by_default(self):
        comtrade = Comtrade(ignore_warnings=True)
        comtrade.load(
            "tests/sample_files/sample_ascii.cfg",
            "tests/sample_files/sample_ascii.dat",
        )

        self.assertEqual(comtrade._use_double_precision, False)
        self.assertEqual(comtrade._get_dat_reader()._use_double_precision, False)

        self.assertEqual(comtrade.time.typecode, "f")
        for chan in comtrade.analog:
            self.assertEqual(chan.typecode, "f")

    def test_should_use_single_when_specified(self):
        comtrade = Comtrade(ignore_warnings=True, use_double_precision=False)
        comtrade.load(
            "tests/sample_files/sample_ascii.cfg",
            "tests/sample_files/sample_ascii.dat",
        )

        self.assertEqual(comtrade._use_double_precision, False)
        self.assertEqual(comtrade._get_dat_reader()._use_double_precision, False)

        self.assertEqual(comtrade.time.typecode, "f")
        for chan in comtrade.analog:
            self.assertEqual(chan.typecode, "f")

    def test_should_use_double_when_specified(self):
        comtrade = Comtrade(ignore_warnings=True, use_double_precision=True)
        comtrade.load(
            "tests/sample_files/sample_ascii.cfg",
            "tests/sample_files/sample_ascii.dat",
        )

        self.assertEqual(comtrade._use_double_precision, True)
        self.assertEqual(comtrade._get_dat_reader()._use_double_precision, True)

        self.assertEqual(comtrade.time.typecode, "d")
        for chan in comtrade.analog:
            self.assertEqual(chan.typecode, "d")


if __name__ == "__main__":
    unittest.main()
