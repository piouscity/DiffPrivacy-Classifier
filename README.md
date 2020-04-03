# DiffPrivacy-Classifier

An implementation of the **DiffGen** algorithm in:

>N.Mohammed, R.Chen, B.C.M.Fung, and P.S.Yu. 
>Differentially private data release for data mining. 
>In 7th SIGKDD International Conference on Knowledge Discovery and Data Mining. 
>ACM, New York, New York, USA, pages 493-501, 2011.

Basic steps of the program:

- Import *dataset* and *taxonomy tree*
- Split the dataset into *training* set and *testing* set
- *Anonymize* both training set and testing set
- Run *classifier* on plain dataset and anonymized dataset
- *Compare* the result between 2 cases

Output of the program:

- **Classification Accuracy (CA)**: Accuracy of classifying anonymized dataset
- **Baseline Accuracy (BA)**: Accuracy of classifying plain dataset
- **Lower bound Accuracy (LA)**: Accuracy on the raw data with all attributes 
(except for the class attribute) removed
- **Cost quality**: `BA - CA`
- **Benefit**: `CA - LA`

## Prerequisite

Create/Open a _Python virtual environment_ if needed.

Install prerequisite packages:
```
pip install -r requirements.txt
```

## Run

It is simple. Just run `main.py` file (no parameters required):
```
python3 main.py
```
The result would be something like this

>Importing dataset...
>
>Anonymizing dataset...
>
>Classifying and calculating...
>
>Baseline accuracy (BA): 78.40212166418034 %
>
>Classification accuracy (CA): 77.43992153016185 %
>
>Lower bound accuracy (LA): 75.84949444720704 %
>
>Cost quality: 0.9622001340184982 %
>
>Benefit: 1.590427082954815 %
>
>Press any key to continue . . .

## Configuration

To configure the parameters of the program, open file `settings.py` 
and modify its constants:

- **LOG_FILE**: Path to the log file
- **LOG_LEVEL**: Level of logging. Choices are: 
`logging.DEBUG`, `logging.INFO`, `logging.WARN`, `logging.ERROR`
- **DATASET_PATH**: Path to import the dataset
- **TAXO_TREE_PATH**: Path to import the taxonomy tree file
- **TRAIN_PATH**: Path to export training set
- **TEST_PATH**: Path to export testing set
- **COVERED_TRAIN_PATH**: Path to export anonymized training set
- **COVERED_TEST_PATH**: Path to export anonymized testing set
- **CLASS_ATTRIBUTE**: Classificating attribute of the dataset
- **MISSING_VALUE**: The value which represents missing values in dataset
- **TRAIN_DATA_SIZE**: Ratio of splitting dataset into training and testing set
- **UTILITY_FUNCTION**: Utility function to be used in DiffGen. Choices are:
`information_gain`, `max_gain`
- **DIGIT**: Rounding digit of numeric attributes when splitting
- **EDP**: e (in e-DP)
- **STEPS**: Number of specializations
