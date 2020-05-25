import logging
import numpy
import traceback

from sklearn.datasets import make_blobs
from settings import MATRIX_PATH, COVERED_MATRIX_PATH, LOG_FILE, LOG_LEVEL, \
    NEW_DIM, EDP, SAMPLES, ORG_DIM, CLUSTERS, DEVIATION, BOX, CLUSTER_PATH
from src.exceptions import BaseException
from src.coverer.routine import generate_dp_matrix


try:
    logging.basicConfig(filename=LOG_FILE, filemode='w',level=LOG_LEVEL)
    matrix, cluster = make_blobs(
        n_samples=SAMPLES,
        n_features=ORG_DIM,
        centers=CLUSTERS,
        cluster_std=DEVIATION,
        center_box=(-BOX, BOX)
        )
    dp_matrix = generate_dp_matrix(matrix, NEW_DIM, EDP)
    numpy.savetxt(MATRIX_PATH, matrix, delimiter=',', fmt='%f')
    numpy.savetxt(COVERED_MATRIX_PATH, dp_matrix, delimiter=',', fmt='%f')
    numpy.savetxt(CLUSTER_PATH, cluster, fmt='%d')
    print("Process completed")
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()
