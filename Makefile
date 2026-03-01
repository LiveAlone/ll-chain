.PHONY: install uninstall clean

install:
	uv tool install --editable .

uninstall:
	uv tool uninstall ll-chain

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

