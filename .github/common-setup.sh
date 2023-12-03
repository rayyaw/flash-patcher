# Common setup for all GitHub workflows of Flash Patcher
echo -e "\nInstalling FFDec..."
wget https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version20.0.0/ffdec_20.0.0.deb
sudo apt install ./ffdec_20.0.0.deb

echo -e "\nInstalling ANTLR..."
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
echo 'export CLASSPATH=".:$GITHUB_WORKSPACE/antlr-4.13.1-complete.jar:$CLASSPATH"' >> $GITHUB_ENV

echo -e "\nInstalling pip dependencies..."
python3 -m pip install -U pytest
python3 -m pip install antlr4-python3-runtime pylint coverage hatch twine

echo -e "\nBuilding ANTLR files..."
cd build && make antlr-java
cd ..