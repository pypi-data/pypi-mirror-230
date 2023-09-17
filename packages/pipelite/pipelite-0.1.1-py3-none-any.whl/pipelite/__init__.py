__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

import argparse
from pipelines.pipelineProcess import pipelineProcess
from config.cmdLineConfig import cmdLineConfig


def main() -> None:
	"""Entry point for the application script"""
	
	# Get configuration from cmdline & ini file
	config = cmdLineConfig.readConfig(argparse.ArgumentParser())
	# Get the logger
	log = pipelineProcess.getLogger(config)
	# Execute the pipeline 
	pipelineProcess(config, log).process()