<!--
SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# FDBuild

Configurable and extensible CLI tool
to fulfill tasks sequentially on a list of projects or vast project hierarchies.
Most commonly used for compiling many projects at once.

<div align="center">
<a href="https://asciinema.org/a/08bG95UXStklafyMU0Ij6sfZl?autoplay=1&loop=1" target="_blank" title="FDBuild example usage">
<img src="https://asciinema.org/a/08bG95UXStklafyMU0Ij6sfZl.svg" width="500" alt="FDBuild processing Wayland template"/></a>
</div>

## Features

### Define Projects
* Define projects in a hierarchy of directories. Settings are inherited.
* Pick plugins to work on these projects.
* Simple YAML syntax allows to easily define projects and share settings.
  For example a toplevel settings file
  ```yaml
  projects:
    - drm
    - kwinft
  source:
    plugin: git
  build:
    plugin: ninja
    threads: max
  ```
  with the specific project settings file *drm/fdbuild.yaml*:
  ```yaml
  source:
    branch: main
    origin: https://gitlab.freedesktop.org/mesa/drm.git
  configure:
    plugin: meson
  install:
    path: /opt/drm
    sudo: false
  ```
* Customize settings in an *fdbuild.yaml* file next to each project and subtree.

### Convenience
* Work all projects with a single command: `fdbuild`
* Depending on your working directory work a subtree with the very same command.
* Bootstrap a single project or whole hierarchies of projects via templates:
  `fdbuild --init-with-template drm`

### Extensibility
* Several templates of popular open source projects are included.
* Work plugins for building most C and C++ software are included.
* Additional templates and work plugins can be installed as Python packages
  that are automatically discovered.

## Getting Started
* Get the latest release via: `pip install fdbuild`.
* Create a project from a template: `fdbuild --init-with-template linux-desktop-meta`.
* Change into the new directory and run `fdbuild`.

## Advanced Usage
### Step Selection
You may skip steps in projects by the *--no* flag or do subset of steps with the *--only* flag.

#### Example
With the steps *source, configure, build, install* the following two commands are equivalent:
* `fdbuild --no source,build`
* `fdbuild --only configure,install`

### Settings Override
Up to four key-value pairs may be overridden on invokation.
This overrides the value for any project independent of its position in the projects hierarchy.

#### Example
In the [above example](#define-projects) we may override the install path and sudo usage
as well as set the clear flag to do a clean build with:
```
fdbuild --set install:path:/usr/local --set1 install:sudo:true --set2 build:clear:true
```

### Settings Hierarchies
Without settings override through command line
a subproject always adheres to the nearest available settings value
in an *fdbuild.yaml* file of its hierarchy.

#### Example
Take the following project tree:
```
PRJ_A
│   fdbuild.yaml
│
└───PRJ_B
|   │   fdbuild.yaml
|   └───PRJ_C
|   │       fdbuild.yaml
|   └───PRJ_D
|           fdbuild.yaml
│
└───PRJ_E
        fdbuild.yaml
```
To query a specific settings value for project *PRJ_C*
FDBuild will first look in *PRJ_A/PRJ_B/PRJ_C/fdbuild.yaml*.
If this settings file defines the value FDBuild will use it on project *PRJ_C*.

Otherwise FDBuild will look into *PRJ_A/PRJ_B/fdbuild.yaml*.
And if this settings file also does not provide the value
FDBuild will look into *PRJ_A/fdbuild.yaml*.

Likewise, for a settings value of project *PRJ_D*, FDBuild will first check its settings file
*PRJ_A/PRJ_B/PRJ_D/fdbuild.yaml*,
next the settings file *PRJ_A/PRJ_B/fdbuild.yaml* and last *PRJ_A/fdbuild.yaml*.

For project *PRJ_E* FDBuild will first look into *PRJ_A/PRJ_E/fdbuild.yaml*,
and if the value is not found there look into *PRJ_A/fdbuild.yaml*.

If FDBuild is run in some directory the hierarchy unfolds recursively
according to the `projects` lists in the working directory and all adjacent directories.
For example assume that in the above tree FDBuild is run from directory *PRJ_B*,
then the settings file of *PRJ_A* will be considered
if and only if *PRJ_B* is listed in the `projects` entry of settings file *PRJ_A/fdbuild.yaml*.

Assume further that the parent directory of *PRJ_A*
does not feature a FDBuild settings file listing *PRJ_A* as one of its projects.
Then the lookup will stop here
and *PRJ_A* becomes the toplevel directory of this project hierarchy
defined through the settings files.

### Settings References
Besides common YAML syntax
you can use the following syntax for referencing other entries
in the same settings file or in another settings file within the project hierarchy:
`@{path_to_other_entry}`.
If you need to use the sequence `@{` without declaring a reference you have to write `@@{`.

The path to the other reference follows a certain syntax as well:
a section or entry in a settings file is denoted by one leading `$`,
project hierarchies are divided by `/`.

#### Example
* `$section$entry` - take value from same settings file at labels `section: entry`.
* `prjA/prjB$entry` - take value from label `entry` in settings file of project *prjA/prjB*
  relative to the settings file of the reference.
* `/prjC/prjD$entry` - take value from label `entry` in the settings file of project *prjC/prjD*,
  whereas *prjC* is a subproject at the toplevel of the project hierarchy.

### Work Dependencies
Usually projects are being worked on in the order defined by the projects hierarchy
and their position in the `projects` key.

This can be bypassed by setting dependencies between projects via the `depends` key
in the *fdbuild.yaml* file of the project that should only be worked on after another one.

#### Example:
In the [above example](#define-projects) writing additionally
```yaml
depends:
  - kwinft
```
to the *drm/fdbuild.yaml* file ensures
that the "kwinft" project is processed before the "drm" project.

## Extensions
With templates, stages, steps, and structurizers,
FDBuild can adapt to any work flow.
For users this means just installing another Python package.

For developers this means hooking into FDBuild's defined entry points
and making their set of templates or plugin a Python package.

### Templates
FDBuild can be made aware of additional templates by defining a `paths()` function for the
entry point group `fdbuild.templates`.

The `paths()` function should then return a list of paths,
where the template files of the package are stored.

#### Example
The official template collection of FDBuild provides:
* [an entry point](fdbuild/setup.cfg#51-52) hooking up
* [a paths() function](fdbuild/setup.cfg#51-52) returning a list with the path to
* [a directory containing the templates](fdbuild/templates)

### Plugins
Stage, step and structurizer plugins allow to extend FDBuild
in order to organize work for any project imaginable.

#### Stages
A stage provides an abstract view on a task.

Defining a custom stage means finding a unique name describing its purpose
and then creating for it an entry hook in the *fdbuild.stages* group.

The entry point must be a class inheriting *fdbuild.core.stage.Stage*.
Its constructor should take an object of type *fdbuild.core.step.Step* as argument
and forward it to the super constructor.
The abstract functionality of the stage can then be declared at will
as member functions of the class.

#### Steps
A step implements a stage.
They may access the abstract functionality of a certain stage
to conduct specific operations to fulfil the task at hand.

Defining a custom step means finding a unique name
and then creating for it an entry hook in the *fdbuild.steps* group.

The entry point must be a class
with its constructor taking an object of type *fdbuild.core.step.Step* as argument.
The class must provide a `work()` member function
that is then called by FDBuild to work on the stage.

#### Structurizers
A structurizer allows creating and updating complex project structures
before the actual work starts on them.

Defining a custom structurizer means finding a unique name
and then creating for it an entry hook in the *fdbuild.structurizers* group.

The entry point must be a class
with its constructor taking an object of type
*fdbuild.core.structurizer.Structurizer* as argument.
The class must provide a `structure(..)` member function
that takes an object of type *fdbuild.core.log.StructureLog* as argument
and returns a map that describes all settings files of projects being structurized.

## Status
This software has been used actively in production already for several years but without a proper release.
Now we first release an unstable version to gather feedback and in particular stabilize the extensions API.
Long-term the goal is a 1.0 release with stable settings syntax and extension API. But until then both may still change in backwards incompatible ways. Such changes will be listed in the changelog though.

## Development
There are a number of open [feature tickets](https://gitlab.com/kwinft/fdbuild/-/issues).
If you are interested in working on one, comment in the ticket or contact us in our [Gitter](https://gitter.im/kwinft/community)/[Matrix](https://matrix.to/#/#kwinft:matrix.org) room.
