FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget unzip

RUN wget --no-check-certificate https://download.manageengine.com/products/service-desk/91677414/ManageEngine_ServiceDesk_Plus.bin -O /opt/ManageEngine_ServiceDesk_Plus.bin

RUN chmod +x /opt/ManageEngine_ServiceDesk_Plus.bin

COPY installer.properties /opt/installer.properties

CMD [ "/opt/ManageEngine_ServiceDesk_Plus.bin" ]
# CMD [ "sleep infinity"]
