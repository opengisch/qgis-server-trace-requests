# qgis-server-trace-requests

A QGIS server plugin to trace requests.

With this plugin installed, your QGIS server will be able to trace TCP/IP requests into trace files on a specified path.

## Quick start guide: existing qgis server infrastructure

1. Download https://github.com/opengisch/qgis-server-trace-requests/archive/master.zip
2. Unzip and copy the `qgis-server-trace-requests` folder to a local qgis server plugin path (check: metadata.txt must be in `[plugin_path]/qgis-server-trace-requests/metadata.txt`)
3. Configure the local plugin path by setting it in apache, nginx, (your favorite webserver) `QGIS_PLUGINPATH=[plugin_path]`
4. Optionally configure the trace files path, if not specified a temporary directory will be created. To configure it you have two possibilities:
   - Set the environment variable `QGIS_TRACEREQUESTS_FILESPATH=[trace_files_path]`.
   - Set it via network request (after server restart): `https://your-server.ch/?SERVICE=TRACE_REQUESTS&COMMAND=SET_FILES_PATH&PATH=[trace_files_path]`
5. Restart server

## Request

This plugin supports some special network requests, to display informations over itself, or to set some settings. All requests intended to be handled by this plugin must have the `SERVICE` parameter set to `TRACE_REQUESTS`. The `COMMAND` parameter specify what should be executed.

### About

`ABOUT` display informations about the plugin and provide a link to retrieve the current log content.

```
https://your-server.ch/?SERVICE=TRACE_REQUESTS&COMMAND=ABOUT
```

### Set files path

`SET_PATH` set the trace files path. If `PATH` is not set, the value from the environment variable is taken.

```
https://your-server.ch/?SERVICE=TRACE_REQUESTS&COMMAND=SET_PATH&PATH=[trace_files_path]
```

### Get traces

`GET_TRACES` return the content of the current trace file.

```
https://your-server.ch/?SERVICE=TRACE_REQUESTS&COMMAND=GET_TRACES
```
