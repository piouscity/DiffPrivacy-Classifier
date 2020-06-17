import logging
import traceback
from sklearn.model_selection import train_test_split

from settings import DATASET_PATH, TRAIN_PATH, TEST_PATH, TRAIN_DATA_SIZE
from src.exceptions import BaseException
from src.file_handler import import_dataset, export_dataset


try:
    print("Importing dataset...")
    dataset = import_dataset(DATASET_PATH)
    train_dataset, test_dataset = train_test_split(
        dataset, train_size=TRAIN_DATA_SIZE
        )
    export_dataset(TRAIN_PATH, train_dataset)
    export_dataset(TEST_PATH, test_dataset)
    print("Dataset splitted with ratio {}".format(TRAIN_DATA_SIZE))
except BaseException as e:
    print("{} - {}".format(e.code, e.detail))
except:
    print("Uncatched exception")
    traceback.print_exc()