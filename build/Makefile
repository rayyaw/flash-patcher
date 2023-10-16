# How to package and run multiple Python files:
# https://stackoverflow.com/questions/9002275/how-to-build-a-single-python-file-from-multiple-scripts

bundle:
	cp -r ../src/__main__.py ../src/patcher.py ../src/compile/ .
	zip -r -D ../flash-patcher.zip .
	echo "#!/usr/bin/python3" | /usr/bin/cat - ../flash-patcher.zip > ../flash-patcher
	chmod +x ../flash-patcher

install-lite: bundle
	sudo cp ../flash-patcher /usr/local/bin

install: bundle
	sudo cp ../flash-patcher /usr/local/bin
	sudo cp ../flash-patcher.json /var/gh-update/flash-patcher.json