# Simple Logger
this is a simple logger for python
to simplify the logging process this module will create a logger object with a file handler and a stream handler and auto format the log message. 
All the logs will be saved in the log file and also printed to the console. 
the log file will be saved in the Logs folder in the root directory of the project.

## Usage
here is an example of how to use this module

```python
import simple-log-helper as log_helper
logger = log_helper.CustomLogger(model_name=__name__,log_filename='./Logs/logs.log').logger
logger.setLevel(log_helper.CustomLogger.INFO)
```

this will create a logger object with the name of the current module and save the logs.log file in the Logs folder in the root directory of the project.