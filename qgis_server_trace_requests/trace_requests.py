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

import json
import os

from qgis.core import QgsMessageLog
from qgis.server import QgsServerFilter

from .logger import Logger


class ParameterError(Exception):
    """A parameter exception that is raised will be forwarded to the client."""


class TraceRequestsFilter(QgsServerFilter):
    def __init__(self, serverIface=None):
        if serverIface:
            super().__init__(serverIface)

        self.trace_files_path = self.__get_path_from_env()

        self.logger = Logger()
        self.logger.set_filename("RequestsLog")
        self.logger.set_folder_path(self.trace_files_path)

    def onRequestReady(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        QgsMessageLog.logMessage(f"onRequestReady {request} {params}")

        self.logger.write_incoming(str(params))

        return True

    def onResponseComplete(self):
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()

        QgsMessageLog.logMessage(f"params: {params}")

        # SERVICE=TRACEREQUESTPLUGIN -- we are taking over
        if params.get("SERVICE", "").upper() == "TRACE_REQUESTS":

            request.clear()

            command = params.get("COMMAND", "ABOUT").upper()

            if command == "ABOUT":
                QgsMessageLog.logMessage("About trace request plugin request")
                about = {
                    "name": "Trace Requests",
                    "qgisMinimumVersion": "3.16",
                    "description": "A QGIS server plugin to trace requests.",
                    "version": "0.0.1",
                    "traceFilesPath": self.trace_files_path,
                }

                request.setResponseHeader("Content-type", "text/json")
                request.appendBody(json.dumps(about, indent=1).encode("utf-8"))

            elif command == "SET_PATH":
                path = params.get("PATH", "")

                self.trace_files_path = path
                if not self.trace_files_path:
                    self.trace_files_path = self.__get_path_from_env()

                self.logger.set_folder_path(self.trace_files_path)

                response = f"Trace files path set to {self.trace_files_path}"
                QgsMessageLog.logMessage(response)

                request.setResponseHeader("Content-type", "text/plain")
                request.appendBody(response.encode("utf-8"))

            elif command == "GET_TRACES":
                current_trace_filename = self.logger.current_filename()

                with open(current_trace_filename, "rb") as trace_file:
                    content = trace_file.read()

                    request.setResponseHeader("Content-type", "text/plain")
                    request.appendBody(content)

        self.logger.write_outgoing(str(request.body()))
        return True

    def __get_path_from_env(self):
        return os.environ.get("QGIS_TRACEREQUESTS_FILESPATH")


class TraceRequests:
    """Trace requests"""

    def __init__(self, serverIface):
        self.serverIface = serverIface
        serverIface.registerFilter(TraceRequestsFilter(serverIface), 1)
