# ecghelper

A utility package for working with electrocardiograms, particularly 12-lead electrocardiograms.

## Quickstart

```sh
pip install ecghelper
```

### Development

Assuming `conda` or `mamba` are available in the shell, you can create a virtual environment for package development as follows.

```sh
conda create -y -n ecghelper "python>=3.9"
conda activate ecghelper
pip install ecghelper[dev]
```

If you are using `zsh`, you will need to escape the square brackets, i.e.:

```sh
pip install ecghelper\[dev\]
```

## Converting functions

Debug - directly call the entry point.

```
python -m pdb src/ecghelper/__main__.py convert -i 82000.xml -f xml -o 82000_wfdb -t wfdb
```
