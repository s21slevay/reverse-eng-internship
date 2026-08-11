FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    build-essential \
    binutils \
    file \
    gdb \
    xxd \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["bash"]