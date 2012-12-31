#!/bin/bash

if [ ! -d "tests/output" ] ; then
	echo "Binaries not assembled yet!"
	exit 1
fi

ls tests/output/*.bin | while read p
do
	echo "*** Running $p"
	python runner.py "$p"
done
