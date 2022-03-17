from microbit import *
import math

display.off()  # Turns off microbit LED display - required for using digital I/O pins

# -------------------------------------------------
# FUNCTIONS

# Sends a MIDI Note On message to the MaxForLive device
def midiNoteOn(chan, n, vel):
    MIDI_NOTE_ON = 0x90

    # Check that function arguments are in the correct range for MIDI
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return

    # Generate MIDI message
    msg = bytes([MIDI_NOTE_ON | chan, n, vel])
    uart.write(msg)

# Sends a MIDI Note Off message to the MaxForLive device
def midiNoteOff(chan, n, vel):
    MIDI_NOTE_OFF = 0x80

    # Check that function arguments are in the correct range for MIDI
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return

    # Generate MIDI message
    msg = bytes([MIDI_NOTE_OFF | chan, n, vel])
    uart.write(msg)

# Sends MIDI CC data to the MaxForLive device
def midiControlChange(chan, n, value):
    MIDI_CC = 0xB0

    # Check that function arguments are in the correct range for MIDI
    if chan > 15:
        return
    if n > 127:
        return
    if value > 127:
        return

    # Generate MIDI message
    msg = bytes([MIDI_CC | chan, n, value])
    uart.write(msg)

# Interrupts the main loops until both right hand buttons have been released
# This is used to prevent unintended user input
def preventInstantExit():
    while True:
        buttonA = button_a.is_pressed()
        buttonB = button_b.is_pressed()

        if (not buttonA) and (not buttonB):
            return
        sleep(100)

# When buttons A & B are pressed, this function runs a new loop (for preset mode)
def presetMode():
    midiNoteOn(0, 9, 127)  # Generate 'Enter' earcon
    preventInstantExit()

    # Initialise variables
    lastIF = False
    lastMF = False
    lastRF = False
    lastPF = False

    # Preset Mode loop
    while True:
        buttonA = button_a.is_pressed()  # Right hand middle finger
        buttonB = button_b.is_pressed()  # Right hand ring finger

        # Get left hand button values
        indexF = pin3.read_digital()
        middleF = pin4.read_digital()
        ringF = pin6.read_digital()
        pinkyF = pin7.read_digital()

        # Check for exiting Preset Mode first
        if buttonA and buttonB:
            midiNoteOff(0, 9, 127)  # Earcon: exit
            return

        elif buttonA:  # Chords 1-4
            if indexF and not lastIF:
                midiNoteOn(0, 10, 1)
                preventInstantExit()
                midiNoteOff(0, 10, 1)
            elif middleF and not lastMF:
                midiNoteOn(0, 10, 2)
                preventInstantExit()
                midiNoteOff(0, 10, 2)
            elif ringF and not lastRF:
                midiNoteOn(0, 10, 3)
                preventInstantExit()
                midiNoteOff(0, 10, 3)
            elif pinkyF and not lastPF:
                midiNoteOn(0, 10, 4)
                preventInstantExit()
                midiNoteOff(0, 10, 4)

        elif buttonB:  # Chords 5-8
            if indexF and not lastIF:
                midiNoteOn(0, 10, 5)
                midiNoteOff(0, 10, 5)
            elif middleF and not lastMF:
                midiNoteOn(0, 10, 6)
                midiNoteOff(0, 10, 6)
            elif ringF and not lastRF:
                midiNoteOn(0, 10, 7)
                midiNoteOff(0, 10, 7)
            elif pinkyF and not lastPF:
                midiNoteOn(0, 10, 8)
                midiNoteOff(0, 10, 8)

        # Re-initialise variables
        lastIF = False
        lastMF = False
        lastRF = False
        lastPF = False

        sleep(100)

# Checks which buttons are pressed and sends relevant MIDI messages to MaxForLive device
def makeStrum(buttonA, buttonB):

    # Get left hand button values
    indexF = pin3.read_digital()
    middleF = pin4.read_digital()
    ringF = pin6.read_digital()
    pinkyF = pin7.read_digital()

    # Choose which chord to tell the MaxForLive device to generate
    if buttonA:  # Chords 1-4
        if indexF:
            midiNoteOn(0, 1, 127)
            midiNoteOff(0, 1, 127)
        elif middleF:
            midiNoteOn(0, 2, 127)
            midiNoteOff(0, 2, 127)
        elif ringF:
            midiNoteOn(0, 3, 127)
            midiNoteOff(0, 3, 127)
        elif pinkyF:
            midiNoteOn(0, 4, 127)
            midiNoteOff(0, 4, 127)

    elif buttonB:  # Chords 5-8
        if indexF:
            midiNoteOn(0, 5, 127)
            midiNoteOff(0, 5, 127)
        elif middleF:
            midiNoteOn(0, 6, 127)
            midiNoteOff(0, 6, 127)
        elif ringF:
            midiNoteOn(0, 7, 127)
            midiNoteOff(0, 7, 127)
        elif pinkyF:
            midiNoteOn(0, 8, 127)
            midiNoteOff(0, 8, 127)

# -------------------------------------------------
# MAIN CODE

# Initialise MIDI communication
uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)

# Initialise variables
lastA = False
lastB = False
lastHandSpeed = 0
lastfingerFlex = 0

# Set how fast the microbit needs to move to trigger a strum
strumThreshold = 10  # Range = 1-1024 (lower = more sensitive to strums)

# Main code loop
while True:

    # Get right hand button values
    buttonA = button_a.is_pressed()
    buttonB = button_b.is_pressed()

    # Check for Preset Mode first
    if buttonA and buttonB:
        presetMode()  # New loop runs in this function until Preset Mode is exited
        preventInstantExit()

    # Check for new flex sensor CC data
    fingerFlex = (pin2.read_analog()-510)*10+200  # Value put into useful range
    if fingerFlex != lastfingerFlex:  # Only send value if it has changed
        valueFlex = math.floor(math.fabs(((fingerFlex + 1024) / 2048 * 127)))
        midiControlChange(0, 23, valueFlex)

    # Check for new strum
    currentHandSpeed = accelerometer.get_z()
    if currentHandSpeed >= strumThreshold and lastHandSpeed < currentHandSpeed:
        makeStrum(buttonA, buttonB)

    # Update values for next loop cycle
    lastA = buttonA
    lastB = buttonB
    lastHandSpeed = currentHandSpeed
    lastfingerFlex = fingerFlex

    sleep(50)  # Time between each loop cycle
