import os

from PySide2.QtCore import QDateTime, QDir, QObject, qDebug


class Logger(QObject):
    MAX_LOG_FILE_LENGTH = 20000
    MAX_LOG_FOLDER_LENGTH = 20

    LOG_EXTENSION_FILE = ".log"

    DIRECTION_INCOMING = "<-"
    DIRECTION_OUTGOING = "->"
    DIRECTION_NEUTRAL = "--"

    def __init__(self):

        self._logFile = None
        self._logLines = 0
        self._logFolderPath = None
        self._logFileName = None

    def set_folder_path(self, path):
        self._logFolderPath = path

        if not self._logFolderPath:
            return

        qDir = QDir()
        if qDir.exists(self._logFolderPath) is False:
            if qDir.mkpath(self._logFolderPath) is False:
                print("Could not create directory '{0}'".format(self._logFolderPath))

        self._create_new_file()

    def set_filename(self, filename):
        self._logFileName = filename

    def current_filename(self) -> str:
        if not self._logFile:
            return None

        return self._logFile.name

    def write_incoming(self, text):
        self.write(text, Logger.DIRECTION_INCOMING)

    def write_outgoing(self, text):
        self.write(text, Logger.DIRECTION_OUTGOING)

    def write(self, text, direction=None):

        if not direction:
            direction = Logger.DIRECTION_NEUTRAL

        prefix = "{0} {1} ".format(
            QDateTime.currentDateTime().toString("yyyy.MM.dd hh:mm:ss.zzz"), direction
        )

        self._write_text(text=text, prefix=prefix)

    def _write_text(self, text, prefix):
        text_list = text.split("\n")

        for txt in text_list:
            logText = prefix + txt
            self._write_to_file(logText)

            qDebug(logText)

    def _write_to_file(self, log):

        qDebug(f"_write_to_file before {self._logFileName} : {self._logFolderPath}")

        if not self._logFileName or not self._logFolderPath:
            return

        qDebug("_write_to_file after")

        self._logLines += 1
        self._logFile.write(log + "\n")
        self._logFile.flush()

        if self._logLines >= Logger.MAX_LOG_FILE_LENGTH:
            self._create_new_file()

    def _create_new_file(self):
        if not self._logFileName or not self._logFolderPath:
            return

        if self._logFile is None:
            if os.path.exists(
                self._logFolderPath
                + "/"
                + self._logFileName
                + Logger.LOG_EXTENSION_FILE
            ):
                self._logFile = open(
                    self._logFolderPath
                    + "/"
                    + self._logFileName
                    + Logger.LOG_EXTENSION_FILE,
                    "r+",
                )
            else:
                self._logFile = open(
                    self._logFolderPath
                    + "/"
                    + self._logFileName
                    + Logger.LOG_EXTENSION_FILE,
                    "w+",
                )

            self._logLines = self._logFile.read().count("\n")

        if self._logLines + 1 > Logger.MAX_LOG_FILE_LENGTH:
            renamePath = (
                self._logFolderPath
                + "/"
                + self._logFileName
                + "_"
                + QDateTime.currentDateTime().toString("yyyy-MM-dd_hh-mm-ss")
                + Logger.LOG_EXTENSION_FILE
            )
            self._logFile.close()
            os.rename(self._logFile.name, renamePath)
            self._logLines = 0
            self._logFile = open(
                self._logFolderPath
                + "/"
                + self._logFileName
                + Logger.LOG_EXTENSION_FILE,
                "w+",
            )
            while len(os.listdir(self._logFolderPath)) > Logger.MAX_LOG_FOLDER_LENGTH:
                oldestFile = min(
                    os.listdir(self._logFolderPath),
                    key=lambda f: os.path.getctime(self._logFolderPath + "/" + f),
                )
                os.remove(self._logFolderPath + "/" + oldestFile)
