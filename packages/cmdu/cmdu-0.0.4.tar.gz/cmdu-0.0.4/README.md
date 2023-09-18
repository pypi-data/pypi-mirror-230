# build
```shell
pip install -r requirements.txt
rm -rf dist
python -m build
python -m twine upload dist/* -u __token__ -p {token}
```
# pypi-AgEIcHlwaS5vcmcCJDkwYTBjZTY5LWU5NGQtNDNhYS05ZWIxLTBiZjdjMzJlMmUyZQACDFsxLFsiY21kdSJdXQACLFsyLFsiNmQ2NWI5ZmQtZDAzYS00YzE4LTgwNjYtOTdlZTBkY2UwMGZiIl1dAAAGIJKby55lo8IXSuyaedbHLVaGOx6K1Wp_SdWeBXwcF3O9

# Commands
```
|-- cmdu
|   |-- json2json
|   |-- json2yaml
|   |-- yaml2json
```
# json2yaml
convert a json input (from stdin) as json output (to stdout)
1. with raw json `python -m cmdu json2json`
2. with pretty format `python -m cmdu json2json --pretty`
2. with pretty format and indentation as 2 `python -m cmdu json2json --pretty --indent 2`

# json2yaml
convert a json input (from stdin) as yaml output (to stdout)
1. `python -m cmdu json2yaml`

# yaml2json
convert a yaml input (from stdin) as json output (to stdout)
1. with raw json `python -m cmdu yaml2json`
2. with pretty format `python -m cmdu yaml2json --pretty`
2. with pretty format and indentation as 2 `python -m cmdu yaml2json --pretty --indent 2`
