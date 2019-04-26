#!/usr/bin/env python

from __future__ import print_function  # use python 3 syntax but make it compatible with python 2
from __future__ import division  # ''

import statistics
import time  # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers

BP = brickpi3.BrickPi3()  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

obstacle = [False, False, False, False, False, False, False]
position = [-75, -50, -25, 0, 25, 50, 75]
threshold = [50, 50, 50, 50, 50, 50, 50]
center = 3
currIdx = center

abort = False

def sensorVal():
    list = []
    for iter in range(9):
        try:
            time.sleep(0.02)
            val = BP.get_sensor(BP.PORT_1)
            list.append(val)
        except brickpi3.SensorError as error:
            print(error)

    print("Sensor vals: ", list)

    if (len(list) == 0):
        return 0
    return statistics.median(list)


def headAlignTask(idx):
    BP.set_motor_position(BP.PORT_B, position[idx])


def move(speed):
    BP.set_motor_dps(BP.PORT_A, speed)
    BP.set_motor_dps(BP.PORT_D, speed)


def moveLeftWheel(speed):
    BP.set_motor_dps(BP.PORT_A, speed)


def moveRightWheel(speed):
    BP.set_motor_dps(BP.PORT_D, speed)


def lookoutTask(idx):
    val = sensorVal()
    obstacle[idx] = val < threshold[idx]


def moveTask():
    move(900)
    time.sleep(1.5)


def stopMovingTask():
    move(0)
    time.sleep(1)


def safeToCross():
    for i in obstacle:
        if i:
            return False
    return True


def lookoutAtPosTask(idx):
    headAlignTask(idx)
    lookoutTask(idx)


def monitorTask():
    n = len(position)
    for i in range(center, -1, -1):
        lookoutAtPosTask(i)
    for i in range(1, n):
        lookoutAtPosTask(i)
    for i in range(n - 2, center - 1, -1):
        lookoutAtPosTask(i)
    if (safeToCross()):
        print("safe to cross!")
    else:
        print("not safe to cross!")


# Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
def reset():
    BP.reset_all()


def configure():
    try:
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))  # reset encoder A
        BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D))  # reset encoder D
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))  # reset encoder B
        BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_ULTRASONIC)         # Configure for an NXT ultrasonic sensor

        BP.set_motor_limits(BP.PORT_B, 30) # head movement speed limit
    except IOError as error:
        print(error)


def crossTask():
    while (True):
        monitorTask()

        print(obstacle)

        if (safeToCross()):
            moveTask()
            stopMovingTask()
            break;


def start():
    configure()
    try:
        while (True):
            cmd = input("Enter c for crossing: ")
            if (cmd == "c"):
                crossTask()
            else:
                print("No such command")
    except KeyboardInterrupt:
        print("\nbye bye\n")
    reset()


# start();

configure()





moveLeftWheel(-200)
moveRightWheel(400)

moveRightWheel(-200)
moveLeftWheel(400)

time.sleep(2)





reset()



