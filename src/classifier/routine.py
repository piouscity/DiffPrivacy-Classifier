from .C45 import C45
from settings import CLASS_ATTRIBUTE
from src.utility import RecordCounter


def transform_dataset(dataset):
    attributes = list(dataset[0].keys())
    class_values = []
    append_attributes = []
    for item in attributes:
        if item.startswith(CLASS_ATTRIBUTE):
            class_values.append(item.split(':')[-1])
        else:
            append_attributes.append(item)
    trans_data = []
    for item in dataset:
        append_item = {
            append_attribute: item[append_attribute]
            for append_attribute in append_attributes
        }
        for class_value in class_values:
            class_item = {CLASS_ATTRIBUTE: class_value}
            for i in range(item[CLASS_ATTRIBUTE + ':' + class_value]):
                trans_data.append({**append_item, **class_item})
    return trans_data


def calculate_classification_accuracy(train_dataset, test_dataset):
    model = C45(train_dataset)
    model.generate_decision_tree()
    test_records = len(test_dataset)
    accurate_records = 0
    for item in test_dataset:
        prediction = model.get_prediction(item)
        if prediction == item[CLASS_ATTRIBUTE]:
            accurate_records += 1
    return float(accurate_records) / test_records


def calculate_lower_bound_accuracy(train_dataset, test_dataset):
    counter = RecordCounter()
    for item in train_dataset:
        counter.record(item[CLASS_ATTRIBUTE])
    max_frequent = 0
    decision = None
    for key, value in counter.count.items():
        if value > max_frequent:
            max_frequent = value
            decision = key
    test_records = len(test_dataset)
    accurate_records = 0
    for item in test_dataset:
        if item[CLASS_ATTRIBUTE] == decision:
            accurate_records += 1
    return float(accurate_records) / test_records

