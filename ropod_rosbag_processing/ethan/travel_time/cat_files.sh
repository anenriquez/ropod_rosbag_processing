#!/bin/sh

# cat all .txt files together in each sub directory
#for d in [0-9][0-9][0-9]
for d in $(find . -maxdepth 1 -type d \( ! -name . \) -exec bash -c "cd '{}' && pwd" \;)
do
    ( cd "$d" && cat *.txt > all_runs.out )
done