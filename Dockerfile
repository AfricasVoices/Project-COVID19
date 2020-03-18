FROM python:3.6-slim

# Install Python tools (git + pipenv)
RUN apt-get update && apt-get install -y git
RUN pip install pipenv

# Install Chrome (for generating PNGs of graphs)
ARG CHROME_VERSION="google-chrome-stable"
RUN apt-get update && apt-get install -y wget gnupg \
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Install Chrome web driver (for connecting to Chrome from Python)
ARG CHROME_DRIVER_VERSION
RUN if [ -z "$CHROME_DRIVER_VERSION" ]; \
  then CHROME_MAJOR_VERSION=$(google-chrome --version | sed -E "s/.* ([0-9]+)(\.[0-9]+){3}.*/\1/") \
    && CHROME_DRIVER_VERSION=$(wget --no-verbose -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}"); \
  fi \
  && apt-get update && apt-get install unzip \
  && echo "Using chromedriver version: "$CHROME_DRIVER_VERSION \
  && wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
  && rm -rf /opt/selenium/chromedriver \
  && unzip /tmp/chromedriver_linux64.zip -d /opt/selenium \
  && rm /tmp/chromedriver_linux64.zip \
  && mv /opt/selenium/chromedriver /opt/selenium/chromedriver-$CHROME_DRIVER_VERSION \
  && chmod 755 /opt/selenium/chromedriver-$CHROME_DRIVER_VERSION \
  && ln -fs /opt/selenium/chromedriver-$CHROME_DRIVER_VERSION /usr/bin/chromedriver

# Install memory_profiler if this script is run with PROFILE_MEMORY flag
ARG INSTALL_MEMORY_PROFILER="false"
RUN if [ "$INSTALL_MEMORY_PROFILER" = "true" ]; then \
        apt-get update && apt-get install -y gcc && \
        pip install memory_profiler; \
    fi

#WORKDIR /tmp
#RUN wget --no-verbose -O orca.AppImage https://github.com/plotly/orca/releases/download/v1.3.0/orca-1.3.0.AppImage
#RUN chmod +x orca.AppImage
#RUN ./orca.AppImage --appimage-extract
#RUN printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /tmp/squashfs-root/app/orca "$@"' > /usr/bin/orca
#RUN chmod -R 777 squashfs-root/
##RUN chmod +x /usr/bin/orca
#RUN orca --help
#RUN chmod +x /tmp/orca.AppImage && ln -s /tmp/orca.AppImage /usr/local/bin/orca

# Plotly depedencies
ARG ORCA_VERSION="1.2.1"
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        xvfb \
        xauth \
        libgtk2.0-0 \
        libxtst6 \
        libxss1 \
        libgconf-2-4 \
        libnss3 \
        libasound2 && \
    mkdir -p /opt/orca && \
    cd /opt/orca && \
    wget --no-verbose -O /opt/orca/orca-${ORCA_VERSION}.AppImage https://github.com/plotly/orca/releases/download/v${ORCA_VERSION}/orca-${ORCA_VERSION}-x86_64.AppImage && \
    chmod +x orca-${ORCA_VERSION}.AppImage && \
    ./orca-${ORCA_VERSION}.AppImage --appimage-extract && \
    rm orca-${ORCA_VERSION}.AppImage && \
    printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /opt/orca/squashfs-root/app/orca "$@"' > /usr/bin/orca && \
    chmod +x /usr/bin/orca

# Make a directory for private credentials files
RUN mkdir /credentials

# Make a directory for intermediate data
RUN mkdir /data

# Set working directory
WORKDIR /app

RUN apt-get install -y gcc

# Install project dependencies.
ADD Pipfile /app
ADD Pipfile.lock /app
RUN pipenv sync

# Copy the rest of the project
ADD code_schemes/*.json /app/code_schemes/
ADD configuration/*.py /app/configuration/
ADD src /app/src
ADD fetch_raw_data.py /app
ADD generate_outputs.py /app
ADD upload_files.py /app
ADD generate_analysis_graphs.py /app
