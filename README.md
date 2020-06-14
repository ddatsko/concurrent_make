# Concurrent Make (build automation tool)

### Table of Contents  
- [How it works](#how)  
- [Installation](#installation)  
- [Usage](#usage)  

### What is this?
An automation tool, similar to GNU Make, implemented in Python.  
The tool uses as many computers for building as it can, which can increase the performance

<a name="how"></a>
### How it works?
There are 2 programs: 
- Server for receiving requests and building the targets
- Main program, that builds the whole project, communicating with servers for increasing the build speed

Each of it is written in Python (**Version 3.8 or higher needed**)

The main program uses a file, very similar to the Makefile for GNU Make, but with less features (hope, it will support all the Makefile features in the future)

#### Steps of building the project:
- Parse the ```concurrent_makefile```
- Identify the targets that need re-build (relying on the date of files creation)
- Build a dependency tree and identify the order of targets building
- Build targets by sending requests to different servers simultaniously

<a name="installation"></a>
## Installation
##### You also need to specify the hosts with running server for targets builds and passwords fo them

### Installation of server using ```docker```
##### Prerequisites: ```docker``` installed
```(bash)
$ docker pull ddatsko/concurrent_make:latest
$ docker run -p <port_of_localhost>:3000  ddatsko/concurrent_make:latest
```
NOTE: You can specify any tag, you wish. Just check out available on [Dockerhub](https://hub.docker.com/repository/docker/ddatsko/concurrent_make)

### Installation of server using ```python```
##### Prerequisites: ```python >= 3.8``` and ```git``` installed

```(bash)
$ git clone https://github.com/ddatsko/concurrent_make.git

# to run server
$ cd concurrent_make/server  # Run server only from this directory
$ python3.8 app.py           # You can change some options like port and host in the app.py file 
 
# to build something
$ cd <your_project_root_dir>
# To check the description of arguments below run $ ypthon3 main.py --help
$ python3 <path_to_concurrent_make>/app/main.py [--file FILE] [--hosts HOSTS] [--max-timeout TIMEOUT]
```
<a name="usage"></a>
## Usage
To build something, you need to create a ```concurrent_makefile``` first (name of file can differ, but then you need to specify it in --file argument)

### concurent_makefile
Format of this file is similar to the Makefile (actually, ```concurrent_makefile``` can be used for GNU ```make```).
But, unfortunately, it has pretty less functionality, than Makefile.
#### in ```concurrent_makefile``` you MAY:
- use variables (assigned in different ways (=, :=, += etc.))
- specify targets, dependencies and commands
- use automatic variables, but only:
  - ```$@```
  - ```$*```
  - ```$<```
  - ```$^``` 
  - ```$+``` 
  - ```$(@D)```
  - ```$(@F)```
  
#### in ```concurrent_makefile``` you MUST:
- specify all the files, the target depends on (even if they are not used in commands runned)
- use Makefile syntax
- use a space sign before absolute path (```g++ ... -L/lib/...``` is **WRONG!**)

#### in ```concurrent_makefile``` you MUST NOT!!:
- use filenames of commands with any special characters or **SPACES**. In general, any characters, that is written with backslach in terminal (```\ , \\, \" ...```) are prohibited in filenames. Even if paths consists of a directory with space sign in name - it is **WRONG**

### ```hosts``` file
Path to file with hosts is relative to the program directory and is specified in ```config.py```, unless it is specified in ```--hosts HOSTS``` command lin argumet. Then the path is relative current location
File should contain many lines, containing information about the url for server and the password to it separated with single space. Comments are lines, starting with '#' sign.
E.g.
```
https://0.0.0.0:3000 strongest_password_ever THIS_WILL BE IGNORED
# This is a comment
https://0.0.0.0:2000 my_p@s$w0rd # THIS WILL BE IGNORED TOO
```


For building do the following:
```
$ cd <your_project_root_dir>
# To check the description of arguments below run $ ypthon3 main.py --help
$ python3 <path_to_concurrent_make>/app/main.py [--file FILE] [--hosts HOSTS] [--max-timeout TIMEOUT]
```




