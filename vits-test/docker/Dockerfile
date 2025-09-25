ARG BASEIMAGE
FROM ${BASEIMAGE}

WORKDIR /workdir

RUN apt update && \
    apt upgrade -y && \
    echo "Asia/Tokyo" > /etc/timezone && \
    DEBIAN_FRONTEND=noninteractive apt install -y tzdata


RUN apt update && \
    apt install --no-install-recommends -y python3.10 python3.10-dev build-essential python3-pip espeak-ng && \
    apt clean

ARG DEVICE
ADD ./resources/${DEVICE}.requirements.txt /tmp
RUN pip3 install -r /tmp/${DEVICE}.requirements.txt

# RUN apt update && \
#     apt install --no-install-recommends -y \
#     # for soundfile
#     libsndfile1 espeak

ADD ./resources/requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
