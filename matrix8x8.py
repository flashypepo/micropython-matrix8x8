"""
matrix8x8: micropython driver for Adafruit 8x8 LED matrix

based upon MicroPython Matrix8x8 Driver made by Jan Bednařík
with commits from r1chardj0n3s (2016)

github repro: https://github.com/JanBednarik/micropython-matrix8x8

Configuration:
- Micropython: v1.20
- microcontroller: TinyPICO (UnexpectedMaker)
- LED matrix: Adafruit HT16K33 LED Backpack

History:
TODO: matrix does not show pixels after a cold reboot (power off -> power on).
2023-0828 PP: vond twee commits waarin onderstaande problemen zijn opgelost
      URL: https://github.com/JanBednarik/micropython-matrix8x8/pull/3/commits/ba1e99aa70eb1a0da52be9fe7377401262748866
      COMMIT: update for pyb -> machine migration
              er zijn twee commits. De 3de commit die rotate() verwijderd, werkt niet bij mij
2023-0827 PP: werkt niet -> i2c.send() bestaat niet voor SoftI2C
"""

#import pyb
from machine import SoftI2C, Pin
import tinypico as board

# PP added from ht16k33_matrix.py
#todo when running ht16k33_matrix_simpletest, even on cold boot -> pixels are visible.
_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = b'\0xE0' #const(0xE0)  PP modified
_HT16K33_OSCILATOR_ON = b'\0x21' #const(0x21)  PP modified

class Matrix8x8:
    """
    Driver for AdaFruit 8x8 LED Matrix display with HT16K33 backpack.
    Example of use:

    display = Matrix8x8()
    display.set(b'\xFF' * 8)    # turn on all LEDs
    display.clear()             # turn off all LEDs
    display.set_row(2, 0xFF)    # turn on all LEDs in row 2
    display.set_column(3, 0xFF) # turn on all LEDs in column 3
    display.set_pixel(7, 6)     # turn on LED at row 7, column 6
    """
    row_addr = (0x00, 0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0E)

    def __init__(self, i2c_bus=1, addr=0x70, brightness=15, i2c=None):
        """
        Params:
        * i2c_bus = I2C bus ID (1 or 2) or None (if param 'i2c' is provided)
        * addr = I2C address of connected display
        * brightness = display brightness (0 - 15)
        * i2c = initialised instance of pyb.I2C object
        """
        self._blinking = 0
        self._brightness = brightness  # PP added
        self.addr = addr
        self.buf = bytearray(8)

        # I2C init
        assert i2c is not None, "i2c must not be 'None'"
        if i2c:
            self.i2c = i2c
            #print("i2c is saved ...")
        else:
            # 2023-0828 PP: not tested yet
            #self.i2c = pyb.I2C(i2c_bus, pyb.I2C.MASTER, baudrate=400000)
            pass  # PP: should not happen - see assert
        
        # set HT16K33 oscillator on
        self._send(_HT16K33_OSCILATOR_ON)
        #self._send(b'\x21')  # 2023-0828 PP modified
        
        #self._brightness = brightness
        self.set_brightness(brightness)
        # DEBUG: print(f"brightness is set on {brightness} ...")
        self.clear()
        self.on()
        # DEBUG: print("matrix is powered on ...")

    def _send(self, data):
        """
        Send data over I2C.
        """
        #self.i2c.send(data, self.addr)
        #self.buf[0] = data   # PP added
        self.i2c.writeto(self.addr, data)  # 2023-0828 PP modified

    def _send_row(self, row):
        """
        Send single row over I2C.
        """
        #PP NOT modified: rotate is required for proper working
        data = bytes((self.row_addr[row], rotate_right(self.buf[row])))
        #data = bytes((self.row_addr[row], self.buf[row]))
        self._send(data)

    def _send_buf(self):
        """
        Send buffer over I2C.
        """
        #2023-0828 PP removed
        data = bytearray(16)
        i = 1
        for byte in self.buf:
            data[i] = rotate_right(byte)
            i += 2
        self._send(data)
        #self._send(self.buf)

    def _clear_column(self, column):
        """
        Clear column in buffer (set it to 0).
        """
        mask = 0x80 >> column
        for row in range(8):
            if self.buf[row] & mask:
                self.buf[row] ^= mask

    def _set_column(self, column, byte):
        """
        Set column in buffer by byte.
        """
        self._clear_column(column)
        if byte == 0:
            return
        mask = 0x80
        for row in range(8):
            shift = column - row
            if shift >= 0:
                self.buf[row] |= (byte & mask) >> shift
            else:
                self.buf[row] |= (byte & mask) << abs(shift)
            mask >>= 1

    def on(self):
        """
        Turn on display.
        """
        self.is_on = True
        # 2023-0828 PP modified: self._send(0x81 | self._blinking << 1)
        #PP modified: self._send(chr(0x81 | self._blinking << 1))
        self._send(bytes([0x81 | self._blinking << 1]))

    def off(self):
        """
        Turn off display. You can controll display when it's off (change image,
        brightness, blinking, ...).
        """
        self.is_on = False
        # PP modified: self._send(0x80)
        self._send(b'\x80')

    def set_brightness(self, value):
        """
        Set display brightness. Value from 0 (min) to 15 (max).
        """
        # PP modified: self._send(0xE0 | value)
        # 2023-0828 PP added assert
        assert value in range(16), f"Illegal value: '{value}'"
        self._send(bytes([0xE0 | value]))
        

    def set_blinking(self, mode):
        """
        Set blinking. Modes:
            0 - blinking off
            1 - blinking at 2Hz
            2 - blinking at 1Hz
            3 - blinking at 0.5Hz
        """
        # 2023-0828 PP added assert
        assert mode in range(4), f"Illegal value for mode: '{mode}'"
        self._blinking = mode
        if self.is_on:
            self.on()

    def set(self, bitmap):
        """
        Show bitmap on display. Bitmap should be 8 bytes/bytearray object or any
        iterable object containing 8 bytes (one byte per row).
        """
        self.buf = bytearray(bitmap)
        self._send_buf()

    def clear(self):
        """
        Clear display.
        """
        for i in range(8):
            self.buf[i] = 0
        self._send_buf()

    def set_row(self, row, byte):
        """
        Set row by byte.
        """
        self.buf[row] = byte
        self._send_row(row)

    def clear_row(self, row):
        """
        Clear row.
        """
        self.set_row(row, 0)

    def set_column(self, column, byte):
        """
        Set column by byte.
        """
        self._set_column(column, byte)
        self._send_buf()

    def clear_column(self, column):
        """
        Clear column.
        """
        self._clear_column(column)
        self._send_buf()

    def set_pixel(self, row, column):
        """
        Set (turn on) pixel.
        """
        self.buf[row] |= (0x80 >> column)
        self._send_row(row)

    def clear_pixel(self, row, column):
        """
        Clear pixel.
        """
        self.buf[row] &= ~(0x80 >> column)
        self._send_row(row)



def rotate_right(byte):
    """
    Rotate bits right.
    """
    byte &= 0xFF
    bit = byte & 0x01
    byte >>= 1
    if(bit):
        byte |= 0x80
    return byte
