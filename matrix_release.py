import logging
import traceback

from settings import MATRIX_PATH, COVERED_MATRIX_PATH, LOG_FILE, LOG_LEVEL, \
    NEW_DIM, EDP
from src.exceptions import BaseException
from src.file_handler import import_matrix, export_matrix
from src.coverer.routine import generate_dp_matrix


try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    matrix = import_matrix(MATRIX_PATH)
    dp_matrix = generate_dp_matrix(matrix, NEW_DIM, EDP)
    export_matrix(COVERED_MATRIX_PATH, dp_matrix)
    print("Process completed")
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()
