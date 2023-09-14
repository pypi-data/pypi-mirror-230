rm dist/* -fr
pip install twine
python setup.py check
python setup.py sdist bdist_wheel
python -m twine upload dist/*