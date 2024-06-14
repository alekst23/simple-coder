setup:
	pip install setuptools
	pip install -r requirements.txt

install:
	pip install -e .

reinstall:
	pip uninstall simplecoder
	pip install -e .
	
all: setup install