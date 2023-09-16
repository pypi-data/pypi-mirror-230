# peaq-py
Follow documentation for detailed overview of feature and functionalities of peaq SDK.

# test
In this version, there are several test cases in the peaq-bc-test. In the future, we have to move it back


# How to publish
rm -rf build dist
python setup.py sdist bdist_wheel
twine upload dist/*
