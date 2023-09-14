
from datetime import datetime, timedelta
from pychrysalide.arch import vmpa
import string
import struct


def data_to_number(content, addr, order, fmt):
    """Convert to a number, if possible."""

    size =  struct.calcsize(order + fmt)

    data = content.read_raw(addr, size)

    value = struct.unpack(order + fmt, data)[0]

    return str(value)


def data_to_time(content, addr, order, fmt):
    """Convert to a number, if possible."""

    size =  struct.calcsize(order + fmt)

    data = content.read_raw(addr, size)

    value = struct.unpack(order + fmt, data)[0]

    return str(datetime(1970, 1, 1) + timedelta(seconds=value))


# Cf. FILETIME structure
# https://docs.microsoft.com/fr-fr/windows/win32/api/minwinbase/ns-minwinbase-filetime

def data_to_filetime(content, addr, order):
    """Convert to a Windows FILETIME, if possible."""

    data = content.read_raw(addr, 8)

    value = struct.unpack(order + 'Q', data)[0]

    us = value / 10.

    return str(datetime(1601, 1, 1) + timedelta(microseconds=us))


# Cf. DosDateTimeToFileTime()
# https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-dosdatetimetofiletime

def data_to_dos_time(content, addr, order):
    """Convert to a MS-DOS time, if possible."""

    data = content.read_raw(addr, 2)

    value = struct.unpack(order + 'H', data)[0]

    seconds = (value & 0x1f) * 2
    minutes = (value & 0x7e0) >> 5
    hours = (value & 0xf800) >> 11

    return '%02u:%02u:%02u' % (hours, minutes, seconds)

def data_to_dos_date(content, addr, order):
    """Convert to a MS-DOS date, if possible."""

    data = content.read_raw(addr, 2)

    value = struct.unpack(order + 'H', data)[0]

    day = (value & 0x1f)
    month = (value & 0x1e0) >> 5
    year = ((value & 0xfe00) >> 9) + 1980

    return '%u/%u/%u' % (month, day, year)


def data_to_char(content, addr, order):
    """Convert to a character, if possible."""

    data = content.read_raw(addr, 1)

    value = struct.unpack(order + 'c', data)[0]

    ch = chr(value[0])

    return ch if ch in string.printable else '-'


def data_to_ansi(content, addr, order):
    """Convert to an ANSI string, if possible."""

    result = None

    while True:

        try:

            data = content.read_raw(addr, 1)

            value = struct.unpack(order + 'c', data)[0]

            ch = chr(value[0])

            if not(ch in string.printable):
                break

            if result:
                result += ch
            else:
                result = ch

        except:
            pass

    return result if result else '-'


def _data_to_utf(content, addr, utf):
    """Convert to an UTF-X string, if possible."""

    result = None

    length = 0

    while True:

        try:

            start = vmpa(addr.phys, 0)
            data = content.read_raw(start, length + 1)

            result = data.decode(utf)

            length += 1

        except Exception as e:
            break

    if length > 0:

        data = content.read_raw(addr, length)

        result = data.decode('utf-8')

    else:
        result = '-'

    return result


def data_to_utf8(content, addr, order):
    """Convert to an UTF-8 string, if possible."""

    return _data_to_utf(content, addr, 'utf-8')


def data_to_utf16(content, addr, order):
    """Convert to an UTF-16 string, if possible."""

    return _data_to_utf(content, addr, 'utf-16')
