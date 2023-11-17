# Common setup for all GitHub workflows of Flash Patcher

echo -e "\nInstalling Java..."
sudo apt install default-jdk

echo -e "\nInstalling Mock JPEXS..."
sudo touch /usr/bin/ffdec

echo -e "\nInstalling ANTLR..."
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
echo 'export CLASSPATH=".:$GITHUB_WORKSPACE/antlr-4.13.1-complete.jar:$CLASSPATH"' >> $GITHUB_ENV

echo -e "\nInstalling pip dependencies..."
python -m pip install --upgrade pip
pip install antlr4-python3-runtime pylint

echo -e "\nBuilding ANTLR files..."
cd build && make antlr-java
cd ..