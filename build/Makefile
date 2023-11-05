# How to package and run multiple Python files:
# https://stackoverflow.com/questions/9002275/how-to-build-a-single-python-file-from-multiple-scripts

all: antlr
	cp -r ../src/__main__.py ../src/patcher.py ../src/compile/ ../src/inject/ ../src/util/ ../src/parse/ ../src/antlr_source/ .
	touch antlr_source/__init__.py compile/__init__.py inject/__init__.py parse/__init__.py parse/visitor/__init__.py util/__init__.py
	zip -r -D ../flash-patcher.zip . > /dev/null
	echo "#!/usr/bin/python3" | /usr/bin/cat - ../flash-patcher.zip > ../flash-patcher
	rm ../flash-patcher.zip
	chmod +x ../flash-patcher

antlr:
	cp ../src/antlr/*.g4 ../src/antlr_source

	cat ../src/antlr/AssetPack.g4 ../src/antlr/Common.g4 > ../src/antlr_source/AssetPack.g4
	cat ../src/antlr/Stagefile.g4 ../src/antlr/Common.g4 > ../src/antlr_source/Stagefile.g4

	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileLexer.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/PatchfileParser.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/AssetPack.g4
	antlr4 -Dlanguage=Python3 -visitor ../src/antlr_source/Stagefile.g4

install-lite:
	sudo cp ../flash-patcher /usr/local/bin

install:
	sudo cp ../flash-patcher /usr/local/bin
	sudo cp ../flash-patcher.json /var/gh-update/flash-patcher.json

clean:
	rm -rf antlr_source compile inject parse util __main__.py patcher.py ../flash-patcher
	rm ../src/antlr_source/*.g4 ../src/antlr_source/*.interp ../src/antlr_source/*.tokens ../src/antlr_source/*.py