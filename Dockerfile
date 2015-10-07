FROM buildpack-deps:wheezy

#Create a folder, and git pull the repo
RUN mkdir /application
COPY Tornado-Application /application/Tornado-Application
