# How to package and run multiple Python files:
# https://stackoverflow.com/questions/9002275/how-to-build-a-single-python-file-from-multiple-scripts

# Package everything into an executable zip file
# The find rule creates an __init__.py in all subdirectories, including nested subdirectories
all: antlr
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

# Run unit tests
test:
	touch ../test/__init__.py
	touch ../test/compile/__init__.py

	pytest ..

# Delete all temp files used for compilation.
# We use find to delete everything in those directories, except for specific items
clean:
	rm ../flash-patcher ../flash-patcher.zip
	find .                   -mindepth 1 ! -name 'Makefile' -delete
	find ../src/antlr_source -mindepth 1 ! -name '.gitkeep' -delete