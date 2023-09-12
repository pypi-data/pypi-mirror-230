# tests.test_alarms.py

from datetime import datetime

import pytest

from pyonms import PyONMS
from pyonms.models.alarm import Alarm
from pyonms.models.event import Event, Severity


@pytest.mark.vcr()
def test_alarm_one(test_instance: PyONMS):
    test_alarm = test_instance.alarms.get_alarm(904)
    assert isinstance(test_alarm, Alarm)
    assert test_alarm.id == 904
    assert test_alarm.lastEvent.id == 17164
    assert test_alarm.serviceType.id == 4
    assert test_alarm.count == 6
    assert test_alarm.severity == Severity.MINOR
    assert isinstance(test_alarm.lastEventTime, datetime)
    assert isinstance(test_alarm.lastEvent, Event)


@pytest.mark.vcr()
def test_alarm_all(test_instance: PyONMS):
    alarms = test_instance.alarms.get_alarms(limit=1000)
    assert len(alarms) == 8
    assert alarms[0].id == 971
    assert alarms[0].lastEvent.id == 17236
    assert alarms[0].parameters[0].name == "importResource"


@pytest.mark.vcr()
def test_alarm_batch(test_instance: PyONMS):
    alarms = test_instance.alarms.get_alarms(limit=40, batch_size=5)
    assert len(alarms) == 8
    assert alarms[0].id == 971
    assert alarms[0].lastEvent.id == 17236
    assert alarms[0].parameters[0].name == "importResource"
