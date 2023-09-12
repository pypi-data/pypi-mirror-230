# Log Module

## Requirements

### Libraries
- pyyaml

### Log Configurations

The log module requires a .yaml file with configurations.

This file is set by default to be read from the environment variable 'LOG_CONFIGURATIONS' but it a file path can also be passed as an argument to the function configure_logging.

The default log configurations are set in the CONFIGURATIONS repositories.

```yaml

logging:

  #formatters determine how are the log messages
  formatters:
    simpleFormatter:
      format: "%(asctime)s - %(levelname)s %(name)s: %(message)s"
      datefmt: "%d/%m/%Y %H:%M:%S"
    detailFormatter:
      format: "%(asctime)s - %(levelname)s %(name)s - File: %(filename)s - %(funcName)s() - Line: %(lineno)d - %(message)s"
      datefmt: "%d/%m/%Y %H:%M:%S"

  disable_existing_loggers: true

  # the loggers listed here can be called by other programs and will behave according to their configurations.
  root:
    level: NOTSET
    handlers: [console]

  loggers:
    my_script:
      level: NOTSET
      handlers: [console, logfile_my_script]
      qualname: my_script
      propagate: false

  # the handlers manage which information goes where. The level section determines which handler processes which log level.
  handlers:
    console:
      class: logging.StreamHandler
      stream: ext://sys.stdout
      formatter: simpleFormatter
      level: INFO
    logfile_my_script:
      class: log.log_module.DynamicRotatingFilenameHandler
      filename: "/logs/%(year)s/%(month)s/%(day)s/my_script_%(slot)s.log"
      formatter: simpleFormatter
      level: DEBUG
      maxBytes: 10485760
      delay: true  # If true, file is created only if needed/used. The file opening is delayed until the first call to emit()
    email:
      class: log.log_module.ThreadedTlsSMTPHandler #logging.handlers.SMTPHandler
      mailhost: !!python/tuple [<smtp server>, <port>]
      fromaddr: <source_email>
      toaddrs: [<dest_email_1>, <dest_email_2>]
      subject: Script Error
      credentials: !!python/tuple [<source_email>, <source_email_password>]
      secure: !!python/tuple [] # type SSL or TLS to use a secure protocol
      useThread: false # process and send email in a thread
      level: CRITICAL 
```

## How to use


### Import to a script

    import logging

    def main():
        ...
        configure_logging('my_config_file.yaml')
        ...

    def myfunction(arg1, arg2, logger=None):
        logger = logger or logging.getLogger("Mylogger")
        logger.info("Doing this ")


      
### How to log messages

#### Root logger

    # Using explicitely the root logger always logs to the console
    logging.info("This is an info of the root logger")

#### Unconfigured logger  

    # The unconfigured loggers are captured by the root logger (-> console)
    unconfigured_logger = logging.getLogger('unconfigured')
    unconfigured_logger.info(f"This is an info from an unknown / unconfigured"
                             f" source")

#### Configured logger
    # Logging from my_script
    my_script_logger = logging.getLogger('my_script')
    my_script_logger.debug("This is an debug from my_script")  # -> file handler
    my_script_logger.warning("This is a warning from my_script")  # -> console & file handler
    my_script_logger.critical("This is an error from my_script")  # -> console, sample & email


