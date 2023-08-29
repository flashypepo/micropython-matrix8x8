"""
2023-0828 PP modified lib/matrix8x8.py according to commit - see matrix8x8.py
             test the modifications -> matrix werkt
Enkele testen zorgen ervoor dat de matrix niet meer oplicht:
  * set_blinking()
  * set_brightness(),
  * on() en/of off()
==============================================================
"""
import time
import tinypico as board
from machine import SoftI2C, Pin

# Import the HT16K33 LED matrix module.
from matrix8x8 import Matrix8x8

# Create the I2C interface.
sda_pin = Pin(board.I2C_SDA)  
scl_pin = Pin(board.I2C_SCL)
i2c = SoftI2C(scl=scl_pin, sda=sda_pin)
print(f"i2c devices: {[hex(device) for device in i2c.scan()]}")

# create the display
display = Matrix8x8(i2c=i2c, brightness=15)

#while True:
# test - from matrix8x8.py
def test1(dt=500):
    print("test1: github matrix8x8 example ...")
    display.set(b'\xFF' * 8)    # turn on all LEDs
    time.sleep_ms(dt)
    display.clear()             # turn off all LEDs
    time.sleep_ms(dt)
    display.set_row(2, 0xFF)    # turn on all LEDs in row 2
    time.sleep_ms(dt)
    display.set_column(3, 0xFF) # turn on all LEDs in column 3
    time.sleep_ms(dt)
    display.set_pixel(7, 6)     # turn on LED at row 7, column 6
    time.sleep_ms(dt)


def test2(dt=500):
    print("test2: set() and clear()...")
    display.set(b'\xFF' * 8)
    time.sleep_ms(dt)
    display.clear()
    time.sleep_ms(dt)
    display.set(b'\x55\xAA' * 4)
    time.sleep_ms(dt)
    display.set(b'\xAA\x55' * 4)
    time.sleep_ms(dt)


def test3(dt=100):
    print("test3: set_row(), clear_row() ...")
    for i in range(8):
        display.set_row(i, 0xFF)
        time.sleep_ms(dt)
    for i in range(8):
        display.clear_row(i)
        time.sleep_ms(dt)


def test4(dt=100):
    print("test4: set_column(), clear_column()...")
    for i in range(8):
        display.set_column(i, 0xFF)
        time.sleep_ms(dt)
    for i in range(8):
        display.clear_column(i)
        time.sleep_ms(dt)


def test5(dt=40):
    print("test5: set_pixel(), clear_pixel()...")
    for row in range(8):
        for column in range(8):
            display.set_pixel(row, column)
            time.sleep_ms(dt)
    for row in range(8):
        for column in range(8):
            display.clear_pixel(row, column)
            time.sleep_ms(dt)


def test6(dt=100):
    print("test6: set_brightness()", end="... ")
    display.set(b'\xFF' * 8)
    for i in range(16):
        print(f"{i}", end=" ")
        display.set_brightness(i)
        time.sleep_ms(dt)
    print(" | ", end=" ")
    for i in range(16):
        print(f"{15-i}", end=" ")
        display.set_brightness(15-i)
        time.sleep_ms(dt)
    print()


def test7(dt=1000):
    print("test7: on(), off()...")
    display.set_brightness(15)
    display.set(b'\xAA' * 8)
    time.sleep_ms(dt)
    display.off()
    time.sleep_ms(dt)
    display.on()
    time.sleep_ms(dt)


def test8(dt=5000):
    print("test8: set_blinking()", end="... ")
    display.set(b'\xAA' * 8)
    print("3", end=" ")
    display.set_brightness(5)
    display.set_blinking(3)
    time.sleep_ms(dt)
    print("2", end=" ")
    display.set_brightness(10)
    display.set_blinking(2)
    time.sleep_ms(dt)
    print("1", end=" ")
    display.set_brightness(15)
    display.set_blinking(1)
    time.sleep_ms(dt)
    print("0")
    display.set_brightness(5)
    display.set_blinking(0)
    time.sleep_ms(dt)


def test9(dt=2000):
    print("test9: changes when display is in off state", end="... ")
    display.set_brightness(15)
    print("off", end=' ')
    display.off()
    time.sleep_ms(500)
    display.set(b'\x33' * 8)
    display.set_blinking(1)
    print("on")
    display.on()
    time.sleep_ms(dt)
    display.set_blinking(0)
    time.sleep_ms(dt)


def test99():
    print('Tests done!')


def clear_matrix(dt=2):
    display.clear()
    time.sleep(dt)


# main
if __name__ == "__main__":
    print("test features of 8x8 LED matrix...")
    
    # define testcases
    #    modify list of testcases to execute tests you want,
    #    in whatever order...
    # Note: test99: end-of-testcases
    
    # all tests
    case_set = [test1, test2, test3, test4, test5,
             test6, test7, test8, test9, test99]
    # example selected tests:
    case_set2 = [test4, test1, test9, test7, test99]
    
    # set the test_set:
    test_set = case_set2
    # execute tests in test_set:
    for test in test_set:  
        test()
        clear_matrix()
