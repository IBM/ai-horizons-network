# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import logging


class LogWrapper:

	def __init__(self, logger):
		self.logger = logger

	def info(self, *args, sep=' '):
		self.logger.info(sep.join(map(str, args)))

	def debug(self, *args, sep=' '):
		self.logger.debug(sep.join(map(str, args)))

	def warning(self, *args, sep=' '):
		self.logger.warning(sep.join(map(str, args)))

	def error(self, *args, sep=' '):
		self.logger.error(sep.join(map(str, args)))

	def critical(self, *args, sep=' '):
		self.logger.critical(sep.join(map(str, args)))

	def exception(self, *args, sep=' '):
		self.logger.exception(sep.join(map(str, args)))

	def log(self, *args, sep=' '):
		self.logger.log(sep.join(map(str, args)))


class LOG:
	def __init__(self, log_fp):
		self.log_fp = log_fp
		# set up logging to file - see previous section for more details
		logging.basicConfig(level=logging.DEBUG,
							format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
							datefmt='%m-%d %H:%M',
							filename=self.log_fp,
							filemode='w')

		# define a Handler which writes INFO messages or higher to the sys.stderr
		# console_str = logging.StreamHandler()
		# console_str.setLevel(logging.INFO)
		# set a format which is simpler for console use
		self.formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		# tell the handler to use this format
		# console_str.setFormatter(self.formatter)
		# add the handler to the root logger
		console = logging.getLogger('')
		# console.addHandler(console_str)
		self.console = LogWrapper(console)
		return



	def get_logger(self, scope):
		return LogWrapper(logging.getLogger(scope))


