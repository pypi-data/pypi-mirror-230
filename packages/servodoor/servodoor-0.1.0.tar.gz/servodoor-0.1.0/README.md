# Servodoor: a simple library for controlling RC servo based doors 

Servo door is a simple library for controlling (RC servo) doors  via via
Pimoroni's [Servo 2040](https://shop.pimoroni.com/products/servo-2040)
18-channel servo controller. Initially designed for use in T-maze type
experiments. The Serovo 2040 must be running the
[servodoor-firmware](https://github.com/willdickson/servodoor-firmware)

## Installing
Install using pip 

```bash
$ pip install servodoor 
```

## Installing from source

This package uses the [poetry](https://python-poetry.org/) dependency manager.
The installation instructions for poetry can be found
[here](https://python-poetry.org/docs/#installation)

Once poetry is installed the serovodoor package can be installed using

```bash
$ poetry install
```
Additional documentation on using poetry can be found
[here](https://python-poetry.org/docs/)


## Usage
```python
import time
from servodoor import ServoDoor

port = '/dev/ttyACM0'
ctrl = ServoDoor(port)

rsp = ctrl.get_config()
print(rsp['config'])

rsp = ctrl.get_positions()
print(rsp['positions'])

ctrl.set_doors({'front': 'open'})
time.sleep(5.0)

ctrl.set_doors({'front': 'close'})
time.sleep(5.0)
```

