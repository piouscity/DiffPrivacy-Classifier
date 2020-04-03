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
- **Lower bound Accuracy (LA)**: Accuracy on the raw data with all attributes (except for the class attribute) removed
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
