# Trail

Trail brings more transparency to your ML experiments.
Start by using MLflow to track experiments and follow the steps below.

# Installation

Install Trail from PyPI via ```pip install trailml```

# Get started

```python
import mlflow
from trail import Trail

with mlflow.start_run() as run:
    with Trail():
      ...your training code...
```

# User configuration

Primary path: ```trailconfig.yml```  
Secondary path: ```~/.config/trail.yml```

```yaml
username: <YOUR_USERNAME>
password: <YOUR_PASSWORD>
projects:
    id: 1234ABC
    parentExperimentId: ABCD123
```


## Required options:
- username
- password

Project-specific options are required if not overwritten at runtime.

If the project is started with missing configuration file, you will be guided through configuration file creation process. If you want to change your configuration file after initial creation, ```scripts/create_config``` can be run to edit the configuration file via command line.
