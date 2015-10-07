FROM buildpack-deps:wheezy

#=====Create a folder, and copy our application into the application folder====
RUN mkdir /application
COPY Tornado-Application /application/Tornado-Application
COPY MongoDB-Settings /application/MongoDB-Settings
COPY MeteorJS-Application  /application/MeteorJS-Application
#=====Create a folder, and copy our application into the application folder====

#===========================Start Update Debian================================
RUN apt-get -y update 
RUN apt-get -y upgrade
RUN apt-get -y install apt-utils 
RUN apt-get -y update 
RUN apt-get -y upgrade
RUN apt-get -y install build-essential python-dev
#===========================End Update Debian==================================

#===========================Install Tornado/PyMongo/Motor======================
RUN apt-get -y install python-pip
RUN pip install tornado
RUN pip install pymongo==2.8
RUN pip install motor
#===========================Install Tornado/PyMongo/Motor======================

#===========================Installing MeteorJS================================
RUN curl https://install.meteor.com/ | sh
#==============================================================================

