#!/bin/sh
rejson_tag="$1"
rejson_target="$2"

mkdir -p "${rejson_target}"
git clone https://github.com/RedisLabsModules/rejson.git -b "${rejson_tag}" \
    --depth 1 \
    "${rejson_target}"
make -C "${rejson_target}"
