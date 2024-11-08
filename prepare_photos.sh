#!/bin/bash

mkdir -p photos/large/
mkdir -p photos/small/

for x in photos/input/*; do
    echo "handle $x.."
    bn="$(basename $x)"
    convert "$x" -resize 2160 -quality 70 "photos/large/$bn"
    convert "$x" -resize "200x200^" -gravity center -crop 200x200+0+0 +repage -quality 70 "photos/small/$bn"
done