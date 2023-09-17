# BL1ZC
BL1ZC lets you use config files, and install and load packages from a list.

How to use package feature:
### app.py
```python
    packages = ["colorify", "wget", "PIL"]

    import bl1zc
    bl1zc.packages.installfromlist(packages)
    bl1zc.packages.openfromlist(packages)

    # Rest of your code
```
How to use config feature (from [bl1c](https://bl1z33.github.io/bl1c)):
### app.bl1c
```
    text: Hello World!
```
### app.py
```python
    import bl1zc
    cfg = bl1zc.config.readFile("app.bl1c")
    print(cfg.getValue("text"))
```