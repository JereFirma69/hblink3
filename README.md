# Project Status

### ⚠️ **Important:** The original repository has been **archived by its maintainers**, and no further development is expected there.

This fork continues the development of the project and is now **actively maintained**. The goal of this repository is to preserve the functionality of the original project while introducing new features, improvements, and bug fixes.

### What this means

* Development continues in this repository
* Issues and pull requests are welcome
* New features and improvements are planned

If you were previously using the archived repository, consider switching to this fork to receive updates and future enhancements.

---
# Support, Discussion, and Getting Involved

If you need support, want to discuss the project, or are interested in contributing to development, please contact:

* **Developer & maintaner:** Dorian (JereFirma69)
* **Callsign:** 9A3COX
* **Email:** [dorian.jercic@gmail.com](mailto:dorian.jercic@gmail.com)
* **GitHub:** https://github.com/JereFirma69

Contributions, bug reports, and feature suggestions are welcome via GitHub Issues or Pull Requests.

### Public HBlink Systems Registry

A voluntary registry for HBlink systems with public access exists at:

http://hblink-register.com.es

If you operate an open-access HBlink system, consider listing it there so other users can discover and connect to your network.

---

# PROJECT: Open Source HomeBrew Repeater Protocol Client/Master. ##

**UPDATES:**

**PURPOSE:** Thanks to the work of Jonathan Naylor, G4KLX; Hans Barthen, DL5DI; Torsten Shultze, DG1HT we have an open protocol for internetworking DMR repeaters. Unfortunately, there's no generic client and/or master stacks. This project is to build an open-source, python-based implementation. You are free to use this software however you want, however we ask that you provide attribution in some public venue (such as project, club, organization web site). This helps us see where the software is in use and track how it is used.

For those who will ask: This is a piece of software that implements an open-source, amateur radio networking protocol. It is not a network. It is not intended to be a network. It is not intended to replace or circumvent a network. People do those things, code doesn't.
  
**PROPERTY:**  
This work represents the author's interpretation of the HomeBrew Repeater Protocol, based on the 2015-07-26 documents from DMRplus, "IPSC Protocol Specs for homebrew DMR repeater" as written by Dorian Jercic, 9A3COX, Jonathan Naylor, G4KLX; Hans Barthen, DL5DI; Torsten Shultze, DG1HT, also licenced under Creative Commons BY-NC-SA license.

**WARRANTY**
None. The owners of this work make absolutely no warranty, express or implied. Use this software at your own risk.

**PRE-REQUISITE KNOWLEDGE:**  
This document assumes the reader is familiar with Linux/UNIX, the Python programming language and DMR.  

**Using docker version**

Docker file included for own image build
To work with provided docker setup you will need:
* A private repository with your configuration files (all .cfg files in repo will be copyed to the application root directory on start up)
* A service user able to read your private repository (or be brave and publish your configuration, or be really brave and give your username and password to the docker)
* A server with docker installed
* Follow this simple steps:

Build your own image from source

```bash

docker build . -t hblink3/hblink3:latest

```

Or user a prebuilt one in docker hub: shaymez/hblink3:latest
This image is multi-arch

Wake up your container

```bash
touch /var/log/hblink.log
chown 54000 -R /var/log/hblink.log
 run -v /var/log/hblink/hblink.log:/var/log/hblink/hblink.log -e GIT_USER=$USER -e GIT_PASSWORD=$PASSWORD -e GIT_REPO=$URL_TO_REPO_WITHOUT_HTTPS://  -p 54000:54000  shaymez/hblink3:latest
 ```

---

# Documentation

Additional documentation for this fork will be added as development progresses. Planned documentation includes:

* Installation and setup guides
* Configuration examples
* Network topology examples
* Feature documentation for new additions
* Development and contribution guidelines

Users and contributors are encouraged to open GitHub Issues for questions, bug reports, or documentation requests.

---

## ***0x49 DE 9A3COX***

Copyright (C) 2016-2020 Cortney T. Buffington, N0MJS n0mjs@me.com

Copyright (C) 2026–present Dorian Jerčić, 9A3COX [dorian.jercic@gmail.com](mailto:dorian.jercic@gmail.com)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
