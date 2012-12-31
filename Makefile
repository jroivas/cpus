
all:
	echo "Usage:"
	echo "  make unittests  - Make unit tests"
	echo "  make test       - Make test apps"
	echo "  make runtests   - Make test apps and run them"

unittests:
	@bash ./tools/unittest.sh
	
test:
	@bash ./tools/assemble.sh

runtests: test
	@bash ./tools/batchrun.sh
