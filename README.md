# Comcurrent Make (build automation tool)

### What is this?
An automation tool, similar to GNU Make, implemented in Python.  
The tool uses as many computers for building as it can, which can increase the performance

### How it works?
There are 2 programs: 
- Server for receiving requests and building the targets
- Main program, that builds the whole project, communicating with servers for increasing the build speed

Each of it is written in Python (vereion 3.7 or higher needed)

The main program uses a file, very similar to the Makefile for GNU Make, but with less features (hope, it will support all the Makefile features in the future)

#### Steps of building the project:
- Parse the ```concurrent_makefile```
- Identify the targets that need re-build (relying on the date of files creation)
- Build a dependency tree and identify the order of targets building
- Build targets by sending requests to different servers simultaniously

### Installation
##### Note: You need Python version >= 3.7 to be installed
#### You also need to specify the hosts with running server for targets builds

```(bash)
$ git clone https://github.com/ddatsko/concurrent_make.git

# to run server
$ cd concurrent_make/server
$ EXPORT FLASK_APP=app.py # On Linux
$ flask run --port=<desired_port> <Some other options>

# to build something
$ cd <your_project_root_dir>
$ python3 <path_to_concurrent_make>/app/main.py
```
