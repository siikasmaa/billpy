[![Build Status](https://travis-ci.com/siikasmaa/billpy.svg?token=eGWizcfFhAAVAJdsNSUW&branch=master)](https://travis-ci.com/siikasmaa/billpy)

# BillPy
A simple python module for creating pdf invoices from custom html.

### Requirements
writer.py uses [wkhtmlpdf](https://wkhtmltopdf.org/downloads.html) for creating pdf files.

Python requirements can be installed inside the project folder with

```python
pip install -r requirements.txt
```

### How to use
Import writer.py to your project and provide your html invoice with id's for each field. The module tags information with keys:

|             Fields |
|--------------------|
|          ```date```|
|      ```due_date```|
|          ```iban```|
|           ```bic```|
|    ```payer_name```|
|        ```number```|
|     ```reference```|
|       ```message```|
|```payer_adress_1```|
|```payer_adress_2```|
|```payer_adress_3```|

For now, you can load invoice data with python dictionary object, example can be found below.

### Example
```python
from writer import Invoice

values = {
    'bic': 'BICCODE',
    'iban': 'FI00 1111 2222 3333 44',
    'due_date': '23.3.2018',
    'date': '10.3.2018',
    'number': 123123123,
    'reference': 12312312,
    'message': 'Foo',
    'payer_name': 'Bar',
    'products': [{
        'product': 'foo',
        'count': 1,
        'price_per': 2.00
    }]
}

inv = Invoice()
inv.load_from_data(values)
inv.validate_input()
inv.pdf_invoice_creator('invoice.html', "./output.pdf")
```
