import logging
import numpy
import traceback

from sklearn.datasets import make_blobs
from settings import MATRIX_PATH, COVERED_MATRIX_PATH, LOG_FILE, LOG_LEVEL, \
    NEW_DIM, EDP, SAMPLES, ORG_DIM, DEVIATION, BOX
from src.exceptions import BaseException
from src.file_handler import export_matrix
from src.coverer.routine import generate_dp_matrix
from src.utility import scatter_plot


CLUSTERS = 2


try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    center_arr = numpy.zeros((CLUSTERS, ORG_DIM))
    center_arr[0][0] = BOX
    center_arr[1][0] = -BOX
    matrix, cluster = make_blobs(
        n_samples=SAMPLES,
        n_features=ORG_DIM,
        centers=center_arr,
        cluster_std=DEVIATION,
        )
    scatter_plot(matrix)
    dp_matrix = generate_dp_matrix(matrix, NEW_DIM, EDP)
    scatter_plot(dp_matrix)
    export_matrix(MATRIX_PATH, matrix, cluster)
    export_matrix(COVERED_MATRIX_PATH, dp_matrix, cluster)
    print("Process completed")
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()
