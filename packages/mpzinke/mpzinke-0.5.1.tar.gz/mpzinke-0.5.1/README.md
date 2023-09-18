# Python
Python libraries for MPZinke.
Includes

A Flask server class for simple routing by HTTP method.


## Build Commands
FROM: https://packaging.python.org/en/latest/tutorials/packaging-projects/

- `python3 -m pip install --upgrade build`
- `python3 -m pip install --upgrade twine`
- `python3 -m build`
- `python3 -m twine upload --repository testpypi dist/*`
	- username: `__token__`
	- password: `<API KEY>`

`python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps python_server_MPZinke`
