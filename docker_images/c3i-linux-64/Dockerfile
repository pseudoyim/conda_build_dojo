# 4/15/2021: This Dockerfile was written for conda_build_dojo (adapted from the 
# original c3i-linux-64 Dockerfile that can be found here: 
# https://github.com/conda/conda-concourse-ci/blob/master/docker/c3i-linux-64/Dockerfile

FROM centos:7

MAINTAINER Paul Yim <pyim@anaconda.com>

# Set the locale
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

RUN yum install -y \
  gettext gettext.i686 \
  libX11 libX11.i686 \
  libXau libXau.i686 \
  libXcb libXcb.i686 \
  libXdmcp libXdcmp.i686 \
  libXext libXext.i686 \
  libXrender libXrender.i686 \
  libXt libXt.i686 \
  mesa-libGL mesa-libGL.i686 \
  mesa-libGLU mesa-libGLU.i686 \
  libXcomposite libXcomposite.i686 \
  libXcursor libXcursor.i686 \
  libXi libXi.i686 \
  libXtst libXtst.i686 \
  libXrandr libXrandr.i686 \
  libXScrnSaver libXScrnSaver.i686 \
  alsa-lib alsa-lib.i686 \
  mesa-libEGL mesa-libEGL.i686 \
  pam pam.i686 \
  openssh-clients \
  patch \
  rsync \
  util-linux \
  wget \
  xorg-x11-server-Xvfb \
  chrpath \
  vim \
  && yum clean all

WORKDIR /build_scripts
ENV CONDA_SHOW_CHANNEL_URLS 1
ENV CONDA_ADD_PIP_AS_PYTHON_DEPENDENCY 0
COPY install_miniconda.sh /build_scripts
RUN ./install_miniconda.sh
COPY install_dojo.sh /build_scripts
RUN chmod ugo+x /build_scripts/install_dojo.sh
RUN echo 'alias start="bash /build_scripts/install_dojo.sh"' >> ~/.bashrc

# Update conda and install git and conda-build.
RUN export PATH="/opt/conda/bin:${PATH}" && \
    conda update conda && \
    conda install --yes git conda-build && \
    conda clean -tipsy && \
    conda build purge-all

CMD [ "/bin/bash" ]