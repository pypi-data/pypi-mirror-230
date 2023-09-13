# Jupyter rquirements extractor

A simple library with a command to extract the requirements from a Jupyter or Colab notebook and extract their versions from your local environment. This can also be used in Google Colab's notebooks in orther to extract that information from their environment.

# Installation

```
pip install jureqex
```

# Usage

```
jureqex --path /path/to/notebook_folder --name notebook_name.ipynb --save /path/to/requirements.txt
```

# Install from GitHub and use it in Colab

First you need to download the Coalb notebook and update it in Colab's workspace.

```
!git clone https://github.com/IvanHCenalmor/JupyterReqExtractor.git
!python -m pip install -e ./JupyterReqExtractor
!jureqex --path /content --name XXX.ipynb --save /content/requirements.txt
```
