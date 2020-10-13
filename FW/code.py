#https://learn.adafruit.com/circuitpython-essentials/circuitpython-cap-touch
#https://www.silabs.com/documents/public/application-notes/AN0040.pdf
#https://music.stackexchange.com/questions/7227/what-keys-are-associated-to-what-drums-when-connecting-keyboard-to-roland-electr

import board
import digitalio
import touchio
import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
import adafruit_dotstar

#Debug the touch pads
debugCode = False

#Default time to wait after a drum is hit
defaultSleepTime = 1

#DotStar define colors
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)

#DotStar Fill
def color_fill(color, wait):
    dot.fill(color)
    dot.show()
    #time.sleep(wait)

class createDrum():
    def __init__(self, touchPin, note, velocity, waitTime, midi, led):

        #Need to add states - padTouched, sendingNote, setRunTime, disabled
        #pad is sending note while finger is still present

        self.touch = touchio.TouchIn(touchPin)
        self.note = note
        self.velocity = velocity
        self.waitTime = waitTime
        self.midi = midi
        self.led = led
        self.noteTimeoutValue = None
        self.running = False #Waits for timer to expire
        self.enabled = True #Enables pad completely.

    def sendNote(self):
        self.midi.send(NoteOn(self.note, self.velocity))

    def stopNote(self):
        self.midi.send(NoteOff(self.note, self.velocity))

    def ledEnable(self):
        self.led.value = True

    def ledDisable(self):
        self.led.value = False

    def setTimeout(self, timeValue):
        self.noteTimeoutValue = timeValue + self.waitTime
        self.running = True

    def queryTimeout(self):
        return self.noteTimeoutValue


#Setup LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

#Setup DotStar
num_pixels = 7
dot = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, num_pixels, brightness=0.5)

#Setup Midi
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

#Setup drums - touchPin, note, velocity, waitTime, midi, led
snare = createDrum(board.A0,       38, 120, defaultSleepTime, midi, led) #38
tom0 = createDrum(board.A1,        48, 120, defaultSleepTime, midi, led) #48
tom1 = createDrum(board.A3,        47, 120, defaultSleepTime, midi, led) #47
bass = createDrum(board.A2,        36, 120, defaultSleepTime, midi, led) #36
floorTom = createDrum(board.A4,    41, 120, defaultSleepTime, midi, led) #41
crashCymbal = createDrum(board.A5, 57, 120, defaultSleepTime, midi, led)
highHat = createDrum(board.D9,     42, 120, defaultSleepTime, midi, led)

while True:

    if debugCode:
        print('Snare - {}'.format(snare.touch.raw_value))
        print('tom0 - {}'.format(tom0.touch.raw_value))
        print('tom1 - {}'.format(tom1.touch.raw_value))
        print('floorTom - {}'.format(floorTom.touch.raw_value))
        print('crashCymbal - {}'.format(crashCymbal.touch.raw_value))
        print('highHat - {}'.format(highHat.touch.raw_value))
        print('bass - {}'.format(bass.touch.raw_value))
        print('\n')

        time.sleep(0.1)


    #Get current time
    currentTime = time.monotonic()


    if snare.enabled and snare.touch.raw_value < 4060: #<4062
        snare.enabled = False
        print('Snare')
        snare.sendNote()
        snare.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(RED, 0.5)
        snare.enabled = True


    if tom0.enabled and tom0.touch.raw_value > 3800:
        tom0.enabled = False
        print('Tom 0')
        tom0.sendNote()
        tom0.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(YELLOW, 0.5)
        tom0.enabled = True

    if tom1.enabled and tom1.touch.raw_value < 3800:
        tom1.enabled = False
        print('Tom 1')
        tom1.sendNote()
        tom1.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(ORANGE, 0.5)
        tom1.enabled = True

    if floorTom.enabled and floorTom.touch.raw_value < 4000:
        floorTom.enabled = False
        print('Floor Tom')
        floorTom.sendNote()
        floorTom.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(PURPLE, 0.5)
        floorTom.enabled = True

    if crashCymbal.enabled and crashCymbal.touch.raw_value > 1800:
        crashCymbal.enabled = False
        print('Crash Cymbal')
        crashCymbal.sendNote()
        crashCymbal.setTimeout( time.monotonic() )
        color_fill(BLUE, 0.5)
        time.sleep(0.1)
        crashCymbal.enabled = True

    if highHat.enabled and highHat.touch.value:
        highHat.enabled = False
        print('High Hat')
        highHat.sendNote()
        highHat.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(GREEN, 0.5)
        highHat.enabled = True


    if bass.enabled and bass.touch.raw_value < 4000:
        bass.enabled = False
        print('Bass')
        bass.sendNote()
        bass.setTimeout( time.monotonic() )
        time.sleep(0.1)
        color_fill(TEAL, 0.5)
        bass.enabled = True


    #------------ Stop -------------#
    if snare.enabled and snare.running:
        #Time has expired
        if time.monotonic() > snare.queryTimeout():
            color_fill(WHITE, 0.5)
            snare.running = False
            snare.stopNote()

    if tom0.enabled and tom0.running:
        #Time has expired
        if time.monotonic() > tom0.queryTimeout():
            color_fill(WHITE, 0.5)
            tom0.running = False
            tom0.stopNote()

    if tom1.enabled and tom1.running:
        #Time has expired
        if time.monotonic() > tom1.queryTimeout():
            color_fill(WHITE, 0.5)
            tom1.running = False
            tom1.stopNote()

    if floorTom.enabled and floorTom.running:
        #Time has expired
        if time.monotonic() > floorTom.queryTimeout():
            color_fill(WHITE, 0.5)
            floorTom.running = False
            floorTom.stopNote()

    if crashCymbal.enabled and crashCymbal.running:
        #Time has expired
        if time.monotonic() > crashCymbal.queryTimeout():
            color_fill(WHITE, 0.5)
            crashCymbal.running = False
            crashCymbal.stopNote()

    if highHat.enabled and highHat.running:
        #Time has expired
        if time.monotonic() > highHat.queryTimeout():
            color_fill(WHITE, 0.5)
            highHat.running = False
            highHat.stopNote()

    if bass.enabled and bass.running:
        #Time has expired
        if time.monotonic() > bass.queryTimeout():
            color_fill(TEAL, 0.5)
            bass.running = False
            bass.stopNote()

