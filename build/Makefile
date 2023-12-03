# If you don't have antlr4 CLI, run export ANTLR_TARGET=antlr-java in your CLI
ANTLR_TARGET ?= antlr

# Build the python project using hatch.
make: $(ANTLR_TARGET)
	rm -rf flash_patcher
	cp -r ../flash_patcher .
	find . -type d -exec touch {}/__init__.py \;
	hatch build
	cp -r dist ..
	rm -f ../dist/__init__.py

# Move stuff to antlr-source in preparation for compilation
antlr-copy:
	cp ../flash_patcher/antlr/*.g4 ../flash_patcher/antlr_source

	cat ../flash_patcher/antlr/AssetPack.g4 ../flash_patcher/antlr/Common.g4 > ../flash_patcher/antlr_source/AssetPack.g4
	cat ../flash_patcher/antlr/Stagefile.g4 ../flash_patcher/antlr/Common.g4 > ../flash_patcher/antlr_source/Stagefile.g4

# Create ANTLR parsers from the CLI tool
antlr: antlr-copy
	antlr4 -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileLexer.g4
	antlr4 -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileParser.g4
	antlr4 -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/AssetPack.g4
	antlr4 -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/Stagefile.g4

# Create ANTLR parsers from the jar file
# Required since github can't install ANTLR through apt
antlr-java: antlr-copy
	cp ../flash_patcher/antlr/*.g4 ../flash_patcher/antlr_source

	cat ../flash_patcher/antlr/AssetPack.g4 ../flash_patcher/antlr/Common.g4 > ../flash_patcher/antlr_source/AssetPack.g4
	cat ../flash_patcher/antlr/Stagefile.g4 ../flash_patcher/antlr/Common.g4 > ../flash_patcher/antlr_source/Stagefile.g4

	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileLexer.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileParser.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/AssetPack.g4
	java -jar ${GITHUB_WORKSPACE}/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/Stagefile.g4

# Run Pylint pull-request checks
pylint:
	echo "Running pylint on source code..."
	pylint $(shell git ls-files '../flash_patcher/*.py') \
	--disable=missing-module-docstring \
	--disable=too-few-public-methods \
	--disable=inconsistent-return-statements \
	--disable=too-many-arguments \
	--disable=unspecified-encoding \
	--disable=import-error \
	--disable=invalid-name

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
	python -m coverage report -m $(shell git ls-files "../flash_patcher/*.py")
	python -m coverage xml -o coverage.xml

# Delete all temp files used for compilation.
# We use find to delete all __init__.py and __pycache__ files and folders
# We also use find to delete everything in those directories, except for specific items
# We use rm -f to delete without erroring out if the file does not exist
clean:
	find ../test                                     -name __init__.py -delete
	find ../flash_patcher              -mindepth 2   -name __init__.py -delete
	find .. -type d                                  -name __pycache__ -exec rm -r {} +
	find ../build                      -mindepth 1 ! -name 'Makefile' ! -name 'pyproject.toml' -delete
	find ../flash_patcher/antlr_source -mindepth 1 ! -name '.gitkeep' -delete
	rm -rf ../dist