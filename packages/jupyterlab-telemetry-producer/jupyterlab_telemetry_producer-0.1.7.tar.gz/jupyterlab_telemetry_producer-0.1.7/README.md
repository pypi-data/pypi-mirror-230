# JupyterLab Telemetry Producer

[![PyPI](https://img.shields.io/pypi/v/jupyterlab-telemetry-producer.svg)](https://pypi.org/project/jupyterlab-telemetry-producer)
[![npm](https://img.shields.io/npm/v/jupyterlab-telemetry-producer.svg)](https://www.npmjs.com/package/jupyterlab-telemetry-producer)

A JupyterLab extension for generating telemetry data with a basic JupyterLab event library.

This extension relies on the [jupyterlab-telemetry-router](https://github.com/educational-technology-collective/jupyterlab-telemetry-router) extension.

## Get started

### Run the telemetry system with docker compose
```bash
# enter the configuration_example directory and run
docker compose -p jupyterlab-telemetry up --build
```
 A JupyterLab application with the telemetry system installed and configured will run on localhost:8888.
 
### Or install the extension and configure it manually

To install the extension, execute:

```bash
pip install jupyterlab-telemetry-producer
```

The `jupyterlab-telemetry-router` extension is automatically installed when `jupyterlab-telemetry-producer` is installed.

Before starting Jupyter Lab with the telemetry system, users need to write their own producer/router configuration files (or use provided configuration examples) and **place them in the correct directory**.

Examples of producer configurations are [here](#configurations).

Examples of router configurations are [here](https://github.com/educational-technology-collective/jupyterlab-telemetry-router#configurations).

## Basic JupyterLab Event Library

### Overview

| Event Producer ID     | Event Triggered When                 | Event Data Structure                                                                               |
| --------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| NotebookOpenEvent     | a notebook is opened                 | eventName, eventTime, environ: current environment data                                            |
| NotebookScrollEvent   | user scrolls on the notebook         | eventName, eventTime, cells: visible cells after scrolling                                         |
| NotebookVisibleEvent  | user navigates back to Jupyter Lab   | eventName, eventTime, cells: visible cells when user navigates back                                |
| NotebookHiddenEvent   | user leaves the Jupyter Lab tab      | eventName, eventTime                                                                               |
| ClipboardCopyEvent    | user copies from a notebook cell     | eventName, eventTime, cells: cell copied from, selection: copied text                              |
| ClipboardCutEvent     | user cuts from a notebook cell       | eventName, eventTime, cells: cell cut from, selection: cut text                                    |
| ClipboardPasteEvent   | user pastes to a notebook cell       | eventName, eventTime, cells: cell pasted to, selection: pasted text                                |
| ActiveCellChangeEvent | user moves focus to a different cell | eventName, eventTime, cells: activated cell                                                        |
| NotebookSaveEvent     | a notebook is saved                  | eventName, eventTime                                                                               |
| CellExecuteEvent      | a cell is executed                   | eventName, eventTime, cells: executed cell, success, kernelError: error detail if execution failed |
| CellAddEvent          | a new cell is added                  | eventName, eventTime, cells: added cell                                                            |
| CellRemoveEvent       | a cell is removed                    | eventName, eventTime, cells: removed cell                                                          |

## Configurations

### Syntax

`activateEvents`: required. An array of the ids of the events. Only valid event producers (1. has an id associated with the event producer class, and 2. the event id is included in `activatedEvents`) will be activated.

`logNotebookContentEvents`: required. An array of the ids of the events. Only valid event producers (1. has an id associated with the event producer class, and 2. the event id is included in `logNotebookContentEvents`) will have the router export the entire notebook content along with the event data.

**The configuration file should be saved into one of the config directories provided by `jupyter --path`.**

### Example

```python
c.JupyterLabTelemetryProducerApp.activeEvents = [
    'NotebookOpenEvent',
    'NotebookScrollEvent',
    # 'NotebookVisibleEvent',
    # 'NotebookHiddenEvent',
    'ClipboardCopyEvent',
    'ClipboardCutEvent',
    'ClipboardPasteEvent',
    'ActiveCellChangeEvent',
    'NotebookSaveEvent',
    'CellExecuteEvent',
    'CellAddEvent',
    'CellRemoveEvent',
]

c.JupyterLabTelemetryProducerApp.logNotebookContentEvents = [
    'NotebookOpenEvent',
    # 'NotebookScrollEvent',
    # 'NotebookVisibleEvent',
    # 'NotebookHiddenEvent',
    # 'ClipboardCopyEvent',
    # 'ClipboardCutEvent',
    # 'ClipboardPasteEvent',
    # 'ActiveCellChangeEvent',
    'NotebookSaveEvent',
    # 'CellExecuteEvent',
    # 'CellAddEvent',
    # 'CellRemoveEvent',
]
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyterlab-telemetry-producer
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

**To write your own telemetry producer extensions, a tutorial with a simple demo could be find [here](https://github.com/educational-technology-collective/jupyterlab_telemetry_producer_demo).**

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupyterlab-telemetry-producer directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable jupyterlab-telemetry-producer
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable jupyterlab-telemetry-producer
pip uninstall jupyterlab-telemetry-producer
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jupyterlab-telemetry-producer` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
