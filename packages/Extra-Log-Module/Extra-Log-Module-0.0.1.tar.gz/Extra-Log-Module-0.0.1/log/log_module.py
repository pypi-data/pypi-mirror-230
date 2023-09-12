import logging.config
import logging.handlers
import os
import smtplib
import threading
import yaml

SESSION_INFO = {}


def configure_logging(config_file=None, session_info={}):
    """
    It loads and configures the log.
    ARGUMENTS:
        config_file {string} -- The path of the YAML log configuration file.
        session_info {dict} -- A dictionary with session information to be
                              used in the definition of log file names or
                              other.
    """
    if not config_file:
        config_file = os.getenv("LOG_CONFIGURATIONS")
    # Updates global variable with session information to be used by other classes
    SESSION_INFO.update(session_info)
    # Loading and configuring logging with the subset of the dict
    global_config = yaml.load(open(config_file, encoding='utf-8').read(),
                              Loader=yaml.UnsafeLoader)
    logging.config.dictConfig(global_config['logging'])


def getLogger_LogFilePath(logger):
    """It returns the log file path of a logger object if it contains
    a FileHandler.
    ARGUMENTS:
        logger {logging.Logger} -- The logger object.
    RETURNS:
        [string] -- A string with the log file path.
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return f"{handler.baseFilename}"


class DynamicRotatingFilenameHandler(logging.handlers.RotatingFileHandler):
    """
    A class that extends the 'logging.handlers.RotatingFileHandler' to be used
    for creating a Rotating File Handler with a dynamic log filename. It tries
    to replace the filename keywords by the respective values in a session
    information dictionary.
    ARGUMENTS:
        See logging.handlers.RotatingFileHandler args.

    USAGE:
        Example, in the following YAML configuration:
        ----------------------
        handlers:
        logfile:
            class: log.log_module.DynamicRotatingFilenameHandler
            filename: "%(algorithm)s_%(slot)s_DGP.log"
        ----------------------
        The filename is replaced by:
            "myAlg_YYYYMMDD.log"
        only if the SESSION_INFO dict contains:
            {'algorithm': 'myAlg',
            'slot': 'YYYYMMDD'}
    """
    def __init__(self, filename="logfile.log", **kw):
        try:
            # Tries to replace filename keywords by Session information
            filename = filename % SESSION_INFO
            # Creates file directory if needed
            filename = os.path.abspath(filename)
            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        except:
            pass
        super(DynamicRotatingFilenameHandler, self).__init__(filename=filename,
                                                             **kw)


class ThreadedTlsSMTPHandler(logging.handlers.SMTPHandler):
    """
    A class that extends the 'logging.handlers.SMTPHandler' to be used by
    the email handler. It allows to use thread to avoid blocking the program
    during connection and email sending.
    ARGUMENTS:
        useThread {boolean} -- Thread flag to choose to connect and send
                               the email as a thread.
        See the other logging.handlers.SMTPHandler args.

    USAGE:
    To use this class, set its name on log YAML handler configuration. Example:
    ----------------------
    handlers:
      my_email_handler:
        class: log.log_module.ThreadedTlsSMTPHandler
        useThread: false
        secure: !!python/tuple []
        mailhost: !!python/tuple [MAILHOST, MAILPORT]
        fromaddr: FROM_ADDR@SERVER.COM
        toaddrs: [TO_ADDR@SERVER.COM]
        subject: My subject
        credentials: !!python/tuple [USERNAME, PASSWORD]
        level: CRITICAL
    ----------------------
    """
    def __init__(self, useThread=False, **kw):
        self.useThread = useThread
        super(ThreadedTlsSMTPHandler, self).__init__(**kw)

    def smtpThreadHolder(self):
        if self.secure:
            smtp = smtplib.SMTP_SSL(self.mailhost, self.mailport,
                                    timeout=self.timeout)
        else:
            smtp = smtplib.SMTP(self.mailhost, self.mailport,
                                timeout=self.timeout)

        if self.username:
            if self.secure:
                smtp.ehlo()
                smtp.starttls()  # smtp.starttls(*self.secure)
                smtp.ehlo()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, self.msg)
            smtp.quit()

    def emit(self, record):
        try:
            import smtplib
            from email.utils import formatdate
            if not self.mailport:
                self.mailport = smtplib.SMTP_PORT
            msg = self.format(record)
            self.msg = (f"From: {self.fromaddr}\r\nTo: {self.toaddrs}\r\n"
                        f"Subject: {self.getSubject(record)}\r\n"
                        f"Date: {formatdate()}\r\n\r\n{msg}")
            if self.useThread:
                thread = threading.Thread(target=self.smtpThreadHolder,
                                          args=())
                thread.daemon = True
                thread.start()
            else:
                self.smtpThreadHolder()
            print("  ---------------------------------------------------------")
            print(f"  AN ALARM EMAIL MESSAGE WAS SENT TO: {self.toaddrs}")
            print("  ---------------------------------------------------------")
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
