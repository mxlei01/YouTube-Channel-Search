FROM buildpack-deps:wheezy

#=====Create a folder, and copy our application into the application folder====
RUN mkdir /application
COPY Tornado-Application /application/Tornado-Application
COPY MongoDB-Settings /application/MongoDB-Settings
COPY MeteorJS-Application  /application/MeteorJS-Application
#=====Create a folder, and copy our application into the application folder====

#===========================Start Update Debian================================
RUN apt-get -y update > /dev/null 2>&1
RUN apt-get -y upgrade > /dev/null 2>&1
RUN apt-get -y install apt-utils > /dev/null 2>&1
RUN apt-get -y update > /dev/null 2>&1 
RUN apt-get -y upgrade > /dev/null 2>&1 
RUN apt-get -y install build-essential > /dev/null 2>&1
#===========================End Update Debian==================================

#===========================Install Tornado/PyMongo/Motor======================
RUN sudo apt-get install python-pip
RUN pip install tornado
RUN pip install pymongo==2.8
RUN pip install motor
#===========================Install Tornado/PyMongo/Motor======================


