# How to package and run multiple Python files:
# https://stackoverflow.com/questions/9002275/how-to-build-a-single-python-file-from-multiple-scripts

# If you don't have antlr4 CLI, run export ANTLR_TARGET=antlr-java in your CLI
ANTLR_TARGET ?= antlr

# Package everything into an executable zip file
# The find rule creates an __init__.py in all subdirectories, including nested subdirectories
all: $(ANTLR_TARGET)
	cp -r ../src/* .
	find . -type d -exec touch {}/__init__.py \;
	zip -r -D ../flash-patcher.zip . > /dev/null
	echo "#!/usr/bin/python3" | /usr/bin/cat - ../flash-patcher.zip > ../flash-patcher
	chmod +x ../flash-patcher

# Move stuff to antlr-source in preparation for compilation
antlr-copy:
	cp ../src/antlr/*.g4 ../src/antlr_source

	cat ../src/antlr/AssetPack.g4 ../src/antlr/Common.g4 > ../src/antlr_source/AssetPack.g4
	cat ../src/antlr/Stagefile.g4 ../src/antlr/Common.g4 > ../src/antlr_source/Stagefile.g4

# Create ANTLR parsers from the CLI tool
antlr: antlr-copy
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileLexer.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileParser.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/AssetPack.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/Stagefile.g4

# Create ANTLR parsers from the jar file
# Required since github can't install ANTLR through apt
antlr-java: antlr-copy
	cp ../src/antlr/*.g4 ../src/antlr_source

	cat ../src/antlr/AssetPack.g4 ../src/antlr/Common.g4 > ../src/antlr_source/AssetPack.g4
	cat ../src/antlr/Stagefile.g4 ../src/antlr/Common.g4 > ../src/antlr_source/Stagefile.g4

	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileLexer.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileParser.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../src/antlr_source/AssetPack.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../src/antlr_source/Stagefile.g4

# Install the zip to /usr/local/bin
install-lite:
	sudo cp ../flash-patcher /usr/local/bin

# Install the zip to /usr/local/bin, and install the gh-update files
install:
	sudo cp ../flash-patcher /usr/local/bin
	sudo cp ../flash-patcher.json /var/gh-update/flash-patcher.json

# Run Pylint pull-request checks
pylint: $(ANTLR_TARGET)
	echo "Running pylint on source code..."
	pylint $(shell git ls-files '../src/*.py') \
	--disable=missing-module-docstring \
	--disable=too-few-public-methods \
	--disable=inconsistent-return-statements \
	--disable=too-many-arguments \
	--disable=unspecified-encoding

	echo "Running pylint on tests..."
	pylint $(shell git ls-files '../test/*.py') \
	--disable=missing-module-docstring \
	--disable=missing-function-docstring \
	--disable=missing-class-docstring \
	--disable=import-error \
	--disable=wrong-import-position \
	--disable=no-name-in-module

# Run unit tests
# The find rule creates an __init__.py in all subdirectories, including nested subdirectories
test: $(ANTLR_TARGET)
	find ../test -type d -exec touch {}/__init__.py \;

	echo "Running tests..."
	python -m coverage run -m pytest ..

# TODO: Add code coverage check
# Command: python -m coverage report -m $(shell git ls-files "../src/*.py") --omit "../src/__main__.py"

# Delete all temp files used for compilation.
# We use find to delete all __init__.py and __pycache__ files and folders
# We also use find to delete everything in those directories, except for specific items
clean:
	find ../test                           -name __init__.py -delete
	find .. -type d                        -name __pycache__ -exec rm -r {} +
	find .                   -mindepth 1 ! -name 'Makefile' -delete
	find ../src/antlr_source -mindepth 1 ! -name '.gitkeep' -delete
	rm ../flash-patcher ../flash-patcher.zip