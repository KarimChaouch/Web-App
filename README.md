[[_TOC_]]

## Install

```
# clone the repo
git clone git@github.com:KarimChaouch/Web-App.git
cd Web-App

# Create a virtualenv or conda environment
conda create --name VMmanager python=3.8 -y
#or
virtualenv -p python3 VMmanager

# Activate the created environment
conda activate Web-App
#or
source VMmanager/bin/activate

# install dependencies
pip install -e .
```