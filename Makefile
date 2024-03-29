.PHONY: whitespace-format-check whitespace-format black-check black-format pydocstyle pylint flake8 isort-check isort-format mypy test coverage clean install-python create-environment delete-environment install-dependencies build-package publish-to-pypi publish-to-test-pypi

PYTHON_ENVIRONMENT = "init_file_checker"
PYTHON_VERSION = "3.8.5"
SOURCE_FILES = *.py

whitespace-format-check:
	# Check whitespace formatting.
	whitespace-format --check-only --color --new-line-marker linux --verbose \
			--add-new-line-marker-at-end-of-file \
			--remove-trailing-whitespace \
			--remove-trailing-empty-lines \
			--normalize-non-standard-whitespace replace \
			--normalize-whitespace-only-files empty \
			--exclude ".pyc$$|venv/|^.git/|^.idea|^.coverage$$|^.pytest_cache/|^.mypy_cache/|^pytest_results/|^.ruff_cache/"  .

whitespace-format:
	# Reformat code.
	whitespace-format --color --new-line-marker linux --verbose \
			--add-new-line-marker-at-end-of-file \
			--remove-trailing-whitespace \
			--remove-trailing-empty-lines \
			--normalize-non-standard-whitespace replace \
			--normalize-whitespace-only-files empty \
			--exclude ".pyc$$|venv/|^.git/|^.idea|^.coverage$$|^.pytest_cache/|^.mypy_cache/|^pytest_results/|^.ruff_cache/"  .

black-check:
	# Check code formatting.
	black --diff --check --color --exclude "_pb2.py|_rpc.py|_twirp.py" $(SOURCE_FILES)

black-format:
	# Reformat code.
	black --exclude "_pb2.py|_rpc.py|_twirp.py" $(SOURCE_FILES)

pydocstyle:
	# Check docstrings
	python -m pydocstyle --verbose --explain --source --count $(SOURCE_FILES)

pylint:
	# Static code analysis.
	pylint --output-format=colorized --ignore-patterns="_pb2.py,_rpc.py,_twirp.py" --rcfile=pylintrc $(SOURCE_FILES)

ruff:
	# Static code analysis using ruff.
	ruff check $(SOURCE_FILES)

flake8:
	# Check PEP8 code style.
	flake8 --color=always --exclude="*_pb2.py,*_rpc.py,*_twirp.py" $(SOURCE_FILES)

isort-check:
	# Check imports.
	isort --check-only --diff --color --skip-glob="*_pb2.py" --skip-glob="*_rpc.py" --skip-glob="*_twirp.py" $(SOURCE_FILES)

isort-format:
	# Format imports.
	isort --color --skip-glob="*_pb2.py" --skip-glob="*_rpc.py" --skip-glob="*_twirp.py" $(SOURCE_FILES)

mypy:
	# Check type hints.
	mypy --config-file "mypy.ini" --exclude ".*_pb2.py$$|.*_rpc.py$$|.*_twirp.py$$" $(SOURCE_FILES)

# Run all code formatting checks.
lint: whitespace-format-check black-check pydocstyle pylint ruff flake8 isort-check mypy poetry-check

# Run all code reformatting.
lint-format: whitespace-format black-format isort-format

test:
	# Run unit tests.
	pytest --verbose ./

coverage:
	# Compute unit test code coverage.
	coverage run -m pytest --verbose --junit-xml=pytest_results/pytest.xml  ./
	coverage report --show-missing
	coverage xml

clean:
	# Remove temporary files.
	rm -rf logs/*.log  pytest_results/  .ruff_cache/ .coverage *.egg-info/  dist/
	find . -name "__pycache__" -prune -exec rm -rf {} \;
	find . -name ".pytest_cache" -prune -exec rm -rf {} \;
	find . -name ".mypy_cache" -prune -exec rm -rf {} \;

install-python:
	# Install the correct version of python.
	pyenv install $(PYTHON_VERSION)

create-environment:
	# Create virtual environment.
	pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_ENVIRONMENT)
	pyenv local $(PYTHON_ENVIRONMENT)
	pip install --upgrade pip

delete-environment:
	# Delete virtual environment.
	pyenv virtualenv-delete $(PYTHON_ENVIRONMENT)

install-dependencies:
	# Install all dependencies.
	poetry install --verbose

	# Force pyenv to re-index the commands available in the virtual environment.
	pyenv rehash

build-package:
	# Build a wheel package.
	poetry build

publish-to-pypi:
	# Publish package to PyPI.
	poetry publish

publish-to-test-pypi:
	# Publish package to Test-PyPI.
	poetry publish -r test-pypi

poetry-check:
	# Check if poetry.lock is consistent with pyproject.toml file.
	poetry check --lock
