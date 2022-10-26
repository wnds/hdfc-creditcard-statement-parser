
# HDFC Bank (India) Credit Card Statement Parser

The python based utility is used to parse PDF statements issued by HDFC Bank Credit Card Division.


## Acknowledgements

 - [HDFC Statement Parser](https://github.com/santosh1994/hdfc-creditcard-statement-parser)
## Installation

Install and run project with python 3.x

```bash
  pip install -r requirements.txt 
```
    
## Usage

```bash
python run.py --statement-path <path-to-pdf-statment> --password <pdf-password-optional> --show-diners-rewards <flag-for-rewards>
```
```
--statement-path - Path to pdf statement file.
--password - <Optional> Password to open the pdf statement.
--show-rewards - <optional> Add Rewards column in output file. Default True
```

## Output

Creates a file named `output.csv` in the current execution folder.

