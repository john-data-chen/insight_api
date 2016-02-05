# Install

### Python Package
   - System Package
	1. sudo apt-get install libncurses5-dev
	2. sudo apt-get install libxml2-dev libxslt1-dev
	3. sudo apt-get install python-dev libffi-dev libssl-dev
   - Python package
	1. virtualenv venv
	2. source venv/bin/activate
	3. pip install -r requirements.txt

# Configurate

### Configurate settings
   - cp instance/config.samply.py instance/config.py
   - modify instance/config.py according to your need 
     
# Execution

### Start flask application
  - python backend.py
