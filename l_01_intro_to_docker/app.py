#! /bin/env python3

from datetime import datetime
from os import environ
from time import tzset

environ['TZ'] = 'Europe/Kiev'
tzset()

time_ = datetime.now()\
        .strftime("%H:%M %d.%m.%y")
name_ = "Maksym Bilyk"

print( "\n\t - ".join(["Lab_01: ", time_, name_]) )