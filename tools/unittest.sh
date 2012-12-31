#!/bin/bash
find -name "*.py" | while read p
do
	python -mdoctest "$p" || echo "Unit tests failed: $p"
done
