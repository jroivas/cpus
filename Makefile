
all:
	@echo "Usage:"
	@echo "  make unittests  - Make unit tests"
	@echo "  make testapps    - Make test apps"
	@echo "  make runtests   - Make test apps and run them"

unittests:
	@bash ./tools/unittest.sh
	
testapps:
	@bash ./tools/assemble.sh

runtests: testapps
	@bash ./tools/batchrun.sh

nosetests:
	@nosetests --with-doctest --verbose
