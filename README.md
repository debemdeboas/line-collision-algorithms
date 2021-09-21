# Collision Detection Algorithms

[This repository](https://github.com/debemdeboas/line-collision-algorithms) contains the implementation of three (four-ish) line collision algorithms: 
brute force, axis aligned bounding boxes (AABB) and regular spatial subdivision.

## Environment

**Python 3.9 or higher is required.**

Before running, please install all of the required packages using `pip`:

```
pip install -r requirements.txt
```

It is also recommended that you run this code from a virtual environment:

```
python -m venv venv
```

## Running

The script requires the user to pass the desired collision algorithm via the CLI, as follows:

```
python InterseccaoEntreTodasAsLinhas.py <algorithm>
```

If no arguments are provided, the script exits with an error message that lists the supported
algorithms.

- Original and original (improved):
  
```
python InterseccaoEntreTodasAsLinhas.py original
python InterseccaoEntreTodasAsLinhas.py original2
```

- Axis aligned bounding boxes:

```
python InterseccaoEntreTodasAsLinhas.py aabb
```

- Spatial subdivision:
  
```
python InterseccaoEntreTodasAsLinhas.py ss
```

The spatial subdivision algorithm also supports parameterized X and Y division sizes.
That is, the amount of cells per axis.
To provide the size, type:

```
python InterseccaoEntreTodasAsLinhas.py ss <sizeX,sizeY>
python InterseccaoEntreTodasAsLinhas.py ss 10,15
```


