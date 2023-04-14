# System code

This directory contains what we call the system code. The system class will be the base class for every other experiment
and can be found in [system.py](system.py). The system itself consists of modules and services. Custom modules and
services for this example system can be found in the [modules](modules) and [services](services)
directories.

Modules are organized in a tree structure with the system itself as the root. Normally, modules control subsets of
devices that realize joint behavior for an independent subsystem. Services, which are organized in a directed acyclic
graph structure, are able to control multiple modules to realize system-wide behavior. Services are also able to control
other services allowing complex system behavior and control abstractions.

System code is organized as a Python package to make the modules easily importable from the repository with experiments.

This is inherited from the dax_example though it will likely be altered and expanded
