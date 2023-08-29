"""
game of life on 8*8 LED matrix

2023-0828 PP from:
    https://github.com/JanBednarik/micropython-matrix8x8/blob/master/examples/game_of_life.py

2023-0828 PP modifications:
    * add i2c
    * replace pyb with time
    * pyb.delay with time.sleep_ms
    * pyb.rng with random
     
"""
#import pyb
import time
import urandom
import tinypico as board
from machine import SoftI2C, Pin
# Import the HT16K33 LED matrix module.
from matrix8x8 import Matrix8x8


def neighbors(cell):
    """
    Yields neighbours of cell.
    """
    x, y = cell
    yield x, y + 1
    yield x, y - 1
    yield x + 1, y
    yield x + 1, y + 1
    yield x + 1, y - 1
    yield x - 1, y
    yield x - 1, y + 1
    yield x - 1, y - 1


def advance(board):
    """
    Advance to next generation in Conway's Game of Life.
    """
    new_board = set()
    for cell in ((x, y) for x in range(8) for y in range(8)):
        count = sum((neigh in board) for neigh in neighbors(cell))
        if count == 3 or (count == 2 and cell in board):
            new_board.add(cell)
    return new_board, new_board == board


def generate_board():
    """
    Returns random board.
    """
    board = set()
    for x in range(8):
        for y in range(8):
            #if pyb.rng() % 2 == 0:
            if urandom.getrandbits(30) % 2 == 0:
                board.add((x, y))
    return board


def board_to_bitmap(board):
    """
    Returns board converted to bitmap.
    """
    bitmap = bytearray(8)
    for x, y in board:
        bitmap[x] |= 0x80 >> y
    return bitmap


def restart_animation(display):
    """
    Shows restart animation on display.
    """
    for row in range(8):
        display.set_row(row, 0xFF)
        time.sleep_ms(100)
    for row in range(8):
        display.clear_row(7-row)
        time.sleep_ms(100)


def gameOfLife(display):
    print("Game of Life...")
    display.set_brightness(3)
    board, still_life = None, False

    while True:
        # init or restart of the game
        if still_life or not board:
            board = generate_board()
            restart_animation(display)
            time.sleep_ms(500)
            display.set(board_to_bitmap(board))

        time.sleep_ms(500)
        # advance to next generation
        board, still_life = advance(board)
        display.set(board_to_bitmap(board))

        # finish dead
        if not board:
            time.sleep_ms(1500)

        # finish still
        if still_life:
            time.sleep_ms(3000)


# excute if main
if __name__ == "__main__":
    try:
        #print("Game of Life ...")
        # Create the I2C interface.
        sda_pin = Pin(board.I2C_SDA)  
        scl_pin = Pin(board.I2C_SCL)
        i2c = SoftI2C(scl=scl_pin, sda=sda_pin)
        print(f"i2c devices: {[hex(device) for device in i2c.scan()]}")
        # create the display
        #display = Matrix8x8(brightness=0)
        #todo: when cold start -> nothing is seen on display. brigthness??
        display = Matrix8x8(i2c=i2c, brightness=15)
        gameOfLife(display)
    
    except KeyboardInterrupt:
        print("user interrupt", end="...")
        display.clear()
        print("done!")
