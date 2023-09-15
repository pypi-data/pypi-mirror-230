# peaq-py
Follow documentation for detailed overview of feature and functionalities of peaq SDK.


# How to publish
rm -rf build dist
python setup.py sdist bdist_wheel
twine upload dist/*
