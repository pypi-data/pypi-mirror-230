# Jikoku  
  
Flexible and extendable Python utility for generating working timetables from general schedule data.  
  
## Basic Usage Example

```python
from jikoku.models import Stop, Service
from jikoku.scheduler import schedule
from datetime import time, timedelta

# Define a simple service and return service
starts = time(hour=8)
ends = time(hour=9, minute=30)

first = Service("a_service", starts, ends, [Stop("Teufort", starts), Stop("Badlands",ends)])
first_return = Service( "a_return_service",starts , ends, [Stop("Badlands", starts), Stop("Teufort", ends)])

# Copy those services throughout the day
all_services = [first + timedelta(hours=i) for i in range(4)] + ([first_return + timedelta(hours=i) for i in range(4)])

# Schedule the services
generated_schedule = schedule(all_services)
print(generated_schedule)
"""prints the following:

train-ZT4bwn
        09:00:00 - 10:30:00: Teufort => Badlands
        11:00:00 - 12:30:00: Badlands => Teufort
train-eP9nMb
        08:00:00 - 09:30:00: Badlands => Teufort
        10:00:00 - 11:30:00: Teufort => Badlands
train-hVGMEI
        08:00:00 - 09:30:00: Teufort => Badlands
        10:00:00 - 11:30:00: Badlands => Teufort
train-jzVbxj
        09:00:00 - 10:30:00: Badlands => Teufort
        11:00:00 - 12:30:00: Teufort => Badlands
"""
```

Have a look at [the documentation](/docs) for more examples, including real word schedules from JR & SNCF! 
  
## Installation  
  
Jikoku is available on PyPI. Install via using (preferably in a virtual environment) via:
```bash
pip install jikoku
```

## Contributing

Pull requests, feature requests or other ideas always welcome.
To get a local development environment setup, you will need [Poetry](https://github.com/python-poetry/poetry) installed. Then:
```bash
git clone https://github.com/TakeoIschiFan/Jikoku
cd Jikoku
poetry install
```
> Note: use `poetry install --with docs if you want to compile the documentation website

To get logging working, add a `.env` file in the root directory which contains the following variables
```txt
PYTHONPATH="jikoku:tests"
DEBUG="true"
```

