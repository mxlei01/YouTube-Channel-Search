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
RUN pip install futures
#===========================Install Tornado/PyMongo/Motor======================

#===========================Installing MeteorJS================================
RUN curl https://install.meteor.com/ | sh
#===========================Installing MeteorJS================================

#===========================Installing MongoDB=================================
RUN curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-3.0.6.tgz
RUN mkdir MongoDB
RUN tar -C ./MongoDB -zxvf mongodb-linux-x86_64-3.0.6.tgz
#===========================Installing MongoDB=================================

#===========================Installing Supervisord=============================
RUN apt-get install -y supervisor
#===========================Installing Supervisord==============================

#===========================Run Supervisord=====================================
COPY Supervisord/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir /var/supervisord
CMD /usr/bin/supervisord
#===========================Run Supervisord=====================================
