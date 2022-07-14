FROM centos:7

RUN yum install -y pinentry rpm-sign rpm-build

COPY build_rpm.sh /usr/sbin/
