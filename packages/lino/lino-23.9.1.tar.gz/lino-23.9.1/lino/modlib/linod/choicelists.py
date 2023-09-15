# -*- coding: UTF-8 -*-
# Copyright 2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# See https://dev.lino-framework.org/plugins/linod.html

from django.conf import settings

from typing import Callable
from django.utils.timezone import now
from lino.api import dd, _

class Procedure(dd.Choice):
    func: Callable
    every_unit: str
    every_value: int
    start_datetime = now()

    def run(self, ar):
        self.func(ar)

    def __repr__(self):
        return f"Procedures.{self.value} every {self.every_value} {self.every_unit}"


class Procedures(dd.ChoiceList):
    max_length = 100
    item_class = Procedure


class LogLevels(dd.ChoiceList):
    pass

add = LogLevels.add_item
add('DEBUG', "DEBUG", 'debug')
add('INFO', "INFO", 'info')
add('WARNING', "WARNING", 'warning')
add('ERROR', "ERROR", 'error')
add('CRITICAL', "CRITICAL", 'critical')
