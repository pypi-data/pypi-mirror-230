# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:36
# Project:      Zibanu Django Project
# Module Name:  signals
# Description:
# ****************************************************************
import inspect
from django import dispatch
from django.dispatch import receiver
from zibanu.django.logging.models import Log
from zibanu.django.logging.models import MailLog

send_mail = dispatch.Signal()

@receiver(send_mail)
def on_send_mail(sender, mail_from: str, mail_to: list, subject: str, smtp_error: str, smtp_code: int, **kwargs):
    """
    Event manager for send_mail signal

    Parameters
    ----------
    sender: Sender class of signal
    mail_from: Mail address from
    mail_to: Mail address list to
    subject: Subject of mail
    smtp_error: SMTP error string
    smtp_code: SMTP error code
    kwargs: Dictionary of parameters

    Returns
    -------
    None
    """
    class_name = sender.__name__
    log = Log(sender=class_name, action=inspect.currentframe().f_code.co_name)
    log.save()
    mail_log = MailLog(log=log, mail_from=mail_from, mail_to=";".join(mail_to), subject=subject, smtp_error=smtp_error,
                       smtp_code=smtp_code)
    mail_log.save()
