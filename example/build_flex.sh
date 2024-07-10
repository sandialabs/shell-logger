#!/usr/bin/env bash

# Clone the Flex repository.
git clone \
  --depth 1 \
  --branch flex-2.5.39 \
  https://github.com/westes/flex.git \
  flex-2.5.39

# Run `autogen`.
cd flex-2.5.39 || exit
./autogen.sh

# Configure flex.
./configure --prefix="$(dirname "$(pwd)")/flex"

# Build `libcompat.la`.
cd lib || exit
make libcompat.la

# Build & install flex.
cd ..
make install-exec
