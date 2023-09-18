FROM docker.io/archlinux
ENV PIP_BREAK_SYSTEM_PACKAGES 1

MAINTAINER Portmod

USER root
# mesa fontconfig and libxkbcommon are undocumented library dependencies of PySide6
RUN pacman -Sy rust bubblewrap python python-pip git gcc make patch python-virtualenv unzip pandoc pkgconf icu which wget cargo-audit mesa fontconfig libxkbcommon --noconfirm
