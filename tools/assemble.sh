#!/bin/bash

if [ ! -e tests ] ; then
	echo "Tests folder not found!"
	exit 1
fi

mkdir -p tests/output
ls tests/*.asm | while read p
do
	name=$(basename "$p" .asm)
	python assembler.py "$p" "tests/output/$name.bin"
done
