all:

.PHONY: requirements
requirements:
	@command -v pipreqs &> /dev/null || { echo "pipreqs not found, installing pipreqs..."; pip install pipreqs; }
	@pipreqs . --encoding=utf8 --force

.PHONY: run
run:
	@python main.py

.PHONY: install
install:
	@pip install -r requirements.txt