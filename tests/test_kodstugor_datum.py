#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arrow
from managedata import datum


def test_add_send_delete_email(as_admin, as_volontär):
    # TODO: ADD reminder to kodstuga
    # TODO: ADD datum for sending
    arrow.utcnow().format("YYYY-MM-DD")
    datum.send_email_reminders_once()
    # TODO: Check send result
    # TODO: Remove
    assert True


def test_add_send_delete_sms(as_admin, as_volontär):
    # TODO: ADD reminder to kodstuga
    # TODO: ADD datum for sending
    arrow.utcnow().format("YYYY-MM-DD")
    datum.send_sms_reminders_once()
    # TODO: Check send result
    # TODO: Remove
    assert True
