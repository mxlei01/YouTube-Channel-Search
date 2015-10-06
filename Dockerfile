FROM buildpack-deps:wheezy

#Create a folder, and git pull the repo
RUN mkdir /application
RUN git clone git@github.com:mxlei01/YouTube-Channel-Search.git /application


