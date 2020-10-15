"""
    This file contains functions to simplify the development of peakfinder

"""
import os

def exists(path):
    """
        Esta funcion se encarga de verificar si un archivo o carpeta existe
    """
    if os.path.isdir(path) or os.path.exists(path):
        return True
    else: 
        return False


def percentage(percent, of):
	"""
        docstring
    """
	return int((percent * of) / 100.0)