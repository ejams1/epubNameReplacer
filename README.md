# epubNameReplacer
Small program to replace names in an .epub file.

# Install

1. Clone repo
1. Run `pip install -r requirements.txt`

# Usage

```python
python3 main.py <path/to/epub> <find> <replace> [--out=path/to/output/epub]
```

# Examples

## One-to-One

```python
python3 main.py ./my.epub Matt Tim
```
will output to the default output of `out.my.epub`, or

```python
python3 main.py ./my.epub Matt Tim --out=new.epub
```
will replace all occurrences of `Matt` with `Tim` and output to `new.epub`.

## Many-to-One

```python
python3 main.py ./my.epub Matt,Brad,Craig Tim
```
will replace all occurrences of `Matt`, `Brad`, and `Craig` with `Tim` and output to `new.epub`.

## Many-to-Many

```python
python3 main.py ./my.epub Matt,Brad,Craig Tim,James,Earl
```
will replace all occurrences of `Matt`, `Brad`, and `Craig` with `Tim`, `James`, and `Earl` respectively, and output to `new.epub`.
