# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/08/23 6:18
# Project:      Zibanu - Django
# Module Name:  db_handler
# Description:
# ****************************************************************
from logging import StreamHandler
from logging import LogRecord

class DbHandler(StreamHandler):
    """
    Inherited class from StreamHandler to capture log record and save on Database.
    """
    def emit(self, record: LogRecord) -> None:
        """
        Emit override method to force save on database.

        Parameters
        ----------
        record : LogRecord send by logging system

        Returns
        -------
        None
        """
        try:
            from zibanu.django.logging.models import Log as Log
            log = Log()
            log.action = record.levelname
            log.sender = record.module + "/" + record.funcName
            log.detail = self.format(record)
            if record.args:
                log.user_id = record.args.get("user_id", None)
                log.ip_address = record.args.get("ip_address", None)
            log.save(force_insert=True)
        except Exception:
            pass
