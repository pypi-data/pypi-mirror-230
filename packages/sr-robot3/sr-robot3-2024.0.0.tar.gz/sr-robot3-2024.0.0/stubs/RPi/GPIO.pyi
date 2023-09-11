from __future__ import annotations
from typing import Iterable, Optional, Union

BCM: int = 11
BOARD: int = 10
BOTH: int = 33
FALLING: int = 32
HARD_PWM: int = 43
HIGH: int = 1
I2C: int = 42
IN: int = 1
LOW: int = 0
OUT: int = 0
PUD_DOWN: int = 21
PUD_OFF: int = 20
PUD_UP: int = 22
RPI_REVISION: int
SERIAL: int = 40
SPI: int = 41
UNKNOWN: int = -1
VERSION: str

def cleanup() -> None: ...
def setmode(mode: int) -> None: ...
def getmode() -> Optional[int]: ...
def gpio_function() -> None: ...
def input(pin: int) -> bool: ...
def output(pin: Union[int, Iterable[int]], state: Union[int, Iterable[int]]) -> None: ...
def setup(
    pin: Union[int, list[int]],
    direction: int,
    *,
    initial: Optional[int] = None,
    pull_up_down: Optional[int] = None,
) -> None: ...
def setwarnings(warnings: bool) -> None: ...

class PWM:
    def __init__(self, channel: int, frequency: int) -> None: ...
    def start(self, duty_cycle: int) -> None: ...
    def ChangeFrequency(self, frequency: int) -> None: ...
    def ChangeDutyCycle(self, duty_cycle: int) -> None: ...
    def stop(self) -> None: ...
