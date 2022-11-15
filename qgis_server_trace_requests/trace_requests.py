# -*- coding: utf-8 -*-

"""
***************************************************************************
    trace_requests.py
    ---------------------
    Date                 : November 2022
    Copyright            : (C) 2022 by OPENGIS.ch
    Email                : info@opengis.ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = "Damiano Lombardi"
__date__ = "November 2022"
__copyright__ = "(C) 2022, Damiano Lombardi - OPENGIS.ch"

import os

from qgis.core import QgsMessageLog
from qgis.server import QgsServerFilter


class ParameterError(Exception):
    """A parameter exception that is raised will be forwarded to the client."""


class TraceRequestsFilter(QgsServerFilter):
    def __init__(self, serverIface=None):
        if serverIface:
            super().__init__(serverIface)

        self.prefix_path = os.environ.get("QGIS_RENDERGEOJSON_PREFIX")

    def onRequestReady(self):
        request = self.serverInterface().requestHandler()
        request.parameterMap()

        QgsMessageLog.logMessage(
            "######################################## onRequestReady"
        )

        return True

    def onResponseComplete(self):
        QgsMessageLog.logMessage(
            "######################################## onResponseComplete"
        )

        return True

    def onSendResponse(self):
        QgsMessageLog.logMessage(
            "######################################## onSendResponse"
        )

        return True


class TraceRequests:
    """Trace requests"""

    def __init__(self, serverIface):
        self.serverIface = serverIface
        serverIface.registerFilter(TraceRequestsFilter(serverIface), 1)
