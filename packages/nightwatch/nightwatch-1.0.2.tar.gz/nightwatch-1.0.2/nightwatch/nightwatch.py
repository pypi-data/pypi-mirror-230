import logging
import json

class Nightwatch:
  def __init__(self, log_file_name='app.log', log_level=logging.INFO):
    # Create or open the log file in append mode
    self.log_file_name = log_file_name
    self.log_level = log_level

    # Create a logger
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(self.log_level)

    # Create a file handler
    file_handler = logging.FileHandler(self.log_file_name)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    self.logger.addHandler(file_handler)

  def log(self, message, data, log_level=logging.INFO, logger = True, console = False):
    try:
      message = self.message_format(message, data)
      if logger == True:
        if log_level == logging.DEBUG:
          self.logger.debug(message)
        elif log_level == logging.INFO:
          self.logger.info(message)
        elif log_level == logging.WARNING:
          self.logger.warning(message)
        elif log_level == logging.ERROR:
          self.logger.error(message)
        elif log_level == logging.CRITICAL:
          self.logger.critical(message)
      if  console == True:
        print(message)
    except Exception as e:
      print('Error in log')
      print(e)
  
  def message_format(self, message_string, data = {}):
    try:
      message_string += ' '
      if isinstance(data, list) or isinstance(data, dict) or isinstance(data, tuple):
        message_string += json.dumps(data) if len(data) > 2 else ''
      elif isinstance(data, str):
        message_string += data
      elif isinstance(data, int) or isinstance(data, float) or isinstance(data, bool):
        message_string += str(data)
      elif data is None:
        message_string += 'None'
    except Exception as e:
      print('Error in message formatting')
      print(e)
    return message_string

  def info(self, message, data = {}, logger = True, console = False):
    self.log(message, data, logging.INFO, logger, console)

  def debug(self, message, data = {}, logger = True, console = False):
    self.log(message, data, logging.DEBUG, logger, console)

  def warning(self, message, data = {}, logger = True, console = False):
    self.log(message, data, logging.WARNING, logger, console)

  def error(self, message, data = {}, logger = True, console = False):
    self.log(message, data, logging.ERROR, logger, console)

  def critical(self, message, data = {}, logger = True, console = False):
    self.log(message, data, logging.CRITICAL, logger, console)
