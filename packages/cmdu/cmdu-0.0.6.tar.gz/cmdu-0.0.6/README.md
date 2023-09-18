# build
```shell
pip install -r requirements.txt
rm -rf dist
python -m build
python -m twine upload dist/* -u __token__ -p {token}
```
# Commands
```
|-- cmdu
|   |-- lnes
|   |   |-- set-nu
|   |
|   |-- convert
|   |   |-- j2j
|   |   |-- j2y
|   |   |-- y2j
|   |
```
## lines set-nu
set line number to each line, pad `000000 |` to the left
1. `python -m cmdu lines set-nu`
    ```
    # input
    line 1
    line 2

    # output
    000001 |line 1
    000002 |line 2
    ```

## convert j2j
convert a json input (from stdin) as json output (to stdout)
1. with raw json(no indentation and new line) `python -m cmdu json2json`
2. with pretty format `python -m cmdu json2json --pretty`
3. with pretty format and indentation as 2 `python -m cmdu json2json --pretty --indent 2`

## convert j2y
convert a json input (from stdin) as yaml output (to stdout)
1. `python -m cmdu json2yaml`

## convert y2j
convert a yaml input (from stdin) as json output (to stdout)
1. with raw json `python -m cmdu yaml2json`
2. with pretty format `python -m cmdu yaml2json --pretty`
3. with pretty format and indentation as 2 `python -m cmdu yaml2json --pretty --indent 2`
