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

from qgis.core import QgsMessageLog, QgsSettingsEntryString
from qgis.PyQt.QtCore import QTemporaryDir, QUrl
from qgis.server import QgsServerFilter

from .logger import Logger


class TraceRequestsFilter(QgsServerFilter):

    COMMAND_ABOUT = "ABOUT"
    COMMAND_SET_PATH = "SET_PATH"
    COMMAND_GET_TRACES = "GET_TRACES"

    def __init__(self, serverIface=None):
        if serverIface:
            super().__init__(serverIface)

        self.settings_entry_trace_files_path = QgsSettingsEntryString(
            "TraceFilesPath", "TraceRequests", "", "Trace files path"
        )

        self.trace_files_path = str()
        self.__update_trace_file_path()

        self.logger = Logger()
        self.logger.set_filename("RequestsLog")
        self.logger.set_folder_path(self.trace_files_path)

    def onRequestReady(self):
        request = self.serverInterface().requestHandler()

        self.logger.write_incoming(f"Url: {request.url()}")
        self.logger.write_incoming(f"Headers: {request.requestHeaders()}")
        self.logger.write_incoming(f"Paremeters: {request.parameterMap()}")

        return True

    def onResponseComplete(self):
        request = self.serverInterface().requestHandler()

        # SERVICE=TRACE_REQUESTS -- we are taking over
        skip_body_tracing = False
        if request.parameterMap().get("SERVICE", "").upper() == "TRACE_REQUESTS":
            command = request.parameterMap().get("COMMAND", self.COMMAND_ABOUT).upper()

            if command == self.COMMAND_ABOUT:
                self.__command_about(request)

            elif command == self.COMMAND_SET_PATH:
                self.__command_set_path(request)

            elif command == self.COMMAND_GET_TRACES:
                self.__command_get_traces(request)
                skip_body_tracing = True

        self.logger.write_outgoing(f"Headers: {request.responseHeaders()}")
        if not skip_body_tracing:
            self.logger.write_outgoing(f"Body: {request.body()}")

        return True

    def __update_trace_file_path(self):

        # First choice from settings
        if self.settings_entry_trace_files_path.value():
            self.trace_files_path = self.settings_entry_trace_files_path.value()

        # Second choice from env
        if not self.trace_files_path:
            self.trace_files_path = self.__get_path_from_env()

        # Third choice a tmp location
        if not self.trace_files_path:
            temporary_dir = QTemporaryDir()
            if temporary_dir.isValid():
                self.trace_files_path = temporary_dir.path()
            else:
                QgsMessageLog.logMessage("Could not create a temporary directory")
                self.trace_files_path = str()

    def __get_path_from_env(self):
        return os.environ.get("QGIS_TRACEREQUESTS_FILESPATH")

    def __command_about(self, request):

        url = QUrl(request.url()).toString(QUrl.RemoveQuery)

        about = f"""<!DOCTYPE html>
        <html>
        <head><title>Trace requests plugin</title></head>
        <body>
        <h1>Trace requests plugin</h1>
        <p>A QGIS server plugin to trace requests.</p>
        <p>Trace files path: {self.trace_files_path}.</p>
         <a href="{url}?SERVICE=TRACE_REQUESTS&COMMAND={self.COMMAND_GET_TRACES}">See current trace file</a>
        </body>
        </html>"""

        request.clear()
        request.setResponseHeader("Content-type", "text/html")
        request.appendBody(about.encode("utf-8"))

    def __command_set_path(self, request):
        path = request.parameterMap().get("PATH", "")

        self.settings_entry_trace_files_path.setValue(path)

        self.__update_trace_file_path()

        self.logger.set_folder_path(self.trace_files_path)

        request.clear()
        request.setResponseHeader("Content-type", "text/plain")
        request.appendBody(
            f"Trace files path set to {self.trace_files_path}".encode("utf-8")
        )

    def __command_get_traces(self, request):
        current_trace_filename = self.logger.current_filename()

        with open(current_trace_filename, "rb") as trace_file:
            content = trace_file.read()

            request.clear()
            request.setResponseHeader("Content-type", "text/plain")
            request.appendBody(content)


class TraceRequests:
    """Trace requests"""

    def __init__(self, serverIface):
        self.serverIface = serverIface
        serverIface.registerFilter(TraceRequestsFilter(serverIface), 1)
