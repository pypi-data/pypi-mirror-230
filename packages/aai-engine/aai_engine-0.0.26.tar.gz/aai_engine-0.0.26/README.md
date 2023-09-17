# AAI Engine

The AAI Engine is a computer vision based automation python library, enabling easy desktop automation with legacy applications, citrix environments, webapps and regualar desktop apps.

## Installation

`pip install aai-engine`

### Local

`python -m pip install -e c:\<>\<>\aai_engine`

or if that does not work (permission issue):

`python3 -m pip install --no-build-isolation -e /example/path/to/aai_engine`

If on macos with an m1, create a conda environment to be able to use opencv.

```
brew install miniforge
conda init zsh
conda create -n aai python=3.8.6
conda activate aai
conda install -c conda-forge opencv
```

## Documentation

[Here](https://aai-org.github.io/aai_engine_manager/) is the documentation for the AAI Engine.

## Build

`python -m build`

Should you want to add files not directly under src/aai_engine_package, add them in MANIFEST.in.

## Usage

The easiest way to capture and edit screenshots is to use the GUI.
One can launch the gui by executing `aai-engine-gui` in the terminal.

### Using the CLI to Take a screenshot

`aai-engine-capture '/path/to/where/you/want/to/save/the/screenshot'`
