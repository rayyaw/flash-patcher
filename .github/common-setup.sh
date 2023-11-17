# Common setup for all GitHub workflows of Flash Patcher

echo "Installing Java..."
sudo apt install default-jdk

echo "Installing Mock JPEXS..."
sudo touch /usr/bin/ffdec

echo "Installing ANTLR..."
wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
echo 'export CLASSPATH=".:$GITHUB_WORKSPACE/antlr-4.13.1-complete.jar:$CLASSPATH"' >> $GITHUB_ENV

echo "Installing pip dependencies..."
python -m pip install --upgrade pip
pip install antlr4-python3-runtime pylint

echo "Building ANTLR files..."
cd build && make antlr-java
cd ..