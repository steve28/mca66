import mca66
import time

with mca66.MCA66('/dev/ttyUSB0') as audio:
    audio.queryZone(2)
