# -*- coding: utf-8 -*-
import pdfkit
from bs4 import BeautifulSoup
import code128
import datetime
import re
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
import config

class Invoice():
    targets = {
        "bic":"",
        "iban":"",
        "due_date":"",
        "number":"",
        "date":"",
        "reference":"",
        "payer_name":"",
        "message":"",
        "payer_adress_1":"",
        "payer_adress_2":"",
        "payer_adress_3":"",
        "total":""
    }
    DATEFORMAT = "%d.%m.%Y"

    def __init__(self):
        self.errors = []
        self.total = 0.00

    def load_from_data(self, data):
        try:
            self.set_bic(data.get('bic'))
            self.set_iban(data.get('iban'))
            self.set_due_date(data.get('due_date'))
            self.set_number(data.get('number'))
            self.set_date(data.get('date'))
            self.set_reference(data.get('reference'))
            self.set_message(data.get('message'))
            self.set_payer_name(data.get('payer_name'))
            self.set_payer_adress(data.get('payer_adress_1'), data.get('payer_adress_2'), data.get('payer_adress_3'))
            self.set_products(data.get('products'))
        except TypeError as type_error:
            print ("Unexpected format for"+str(type_error))
            self._set_state(str(type_error), str(type_error))

    def set_iban(self, value):
        if value == None:
            self._set_state("iban","Missing information for IBAN")
            return
        if re.compile("^[A-Za-z]{2}[0-9]{16}$").match(re.sub("\s+|\n+", "", value)):
            self._set_state("iban","")
            self.iban = value
            return
        self._set_state("iban", "Incorrect format for IBAN")

    def set_bic(self, value):
        if value == None:
            self._set_state("bic", "Missing information for BIC")
            return
        if re.compile("^[A-Za-z0-9]+$").match(re.sub("\s+|\n+", "", value)):
            self._set_state("bic","")
            self.bic = value
            return
        self._set_state("bic", "Incorrect format for BIC")

    def set_number(self, value):
        if value == None:
            self._set_state("number", "Missing information for invoice number")
            return
        if re.compile("^[0-9]+$").match(re.sub("\s+|\n+", "", str(value))):
            self._set_state("number","")
            self.number = value
            return
        self._set_state("number", "Incorrect format for invoice number")

    def set_due_date(self, value):
        try:
            if value == None:
                self._set_state("due_date", "Missing information for invoice due date")
                return
            if (datetime.datetime.strptime(value, self.DATEFORMAT) > datetime.datetime.today()):
                self.due_date = datetime.datetime.strptime(value, self.DATEFORMAT)
                self._set_state("due_date","")
                return
            self._set_state("due_date", "Incorrect format for due date")
        except ValueError as value_err:
            print (str(value_err))
            self._set_state("due_date", str(value_err))

    def set_date(self, value):
        try:
            if value == None:
                self._set_state("date", "Missing information for invoice date")
                return
            self.date = datetime.datetime.strptime(value, self.DATEFORMAT)
            self._set_state("date","")
        except ValueError as value_err:
            self._set_state("date", str(value_err))

    def set_reference(self, value):
        if value == None:
            self._set_state("reference", "Missing information for invoice reference")
            return
        if re.compile("(^$)|(^[0-9]{3,20}$)").match(re.sub("\s+|\n+", "", str(value))):
            self._set_state("reference","")
            self.reference = value
            return
        self._set_state("reference", "Incorrect format for invoice reference")

    def set_message(self, value):
        if re.compile(".").match(value):
            self._set_state("message","")
            self.message = value
            return
        self._set_state("message", "Incorrect format for invoice message")

    def set_payer_name(self, value):
        if value == None:
            self._set_state("payer_name", "Missing information for payer's name")
            return
        if re.compile(".").match(value):
            self.payer_name = value
            self._set_state("payer_name","")
            return
        self._set_state("payer_name", "Incorrect format for payer name")

    def set_payer_adress(self, value, *args):
        if re.compile(".").match(value):
            self.payer_adress_1 = value
            self.payer_adress_2 = "" if args[0] == None else args[0]
            self.payer_adress_3 = "" if args[1] == None else args[1]
            self._set_state("payer_adress","")
            return
        self._set_state("adress", "Incorrect format for adress")

    def set_products(self, value):
        self.products = []
        if (value == None):
            self._set_state("product", "No products in invoice")
        for item in value:
            if ('product' not in item or 'price_per' not in item or 'count' not in item):
                self._set_state("product", "Information for " + item + " missing")
            else:
                self.products.append(item)
                self._set_state("product", "")

    def _set_state(self, caller, value):
        self.targets[caller] = value

    def validate_input(self):
        self.errors.clear()
        for state in self.targets.values():
            if state != "":
                self.errors.append(state)

    def code_creator(self, VERSION="4", VARALLA="000"):
        iban = re.sub('\s+|[A-Za-z]+', '', self.iban)
        total = str(self.total).split(".")
        euros = total[0].zfill(6)
        cents = total[1].zfill(2)
        reference = str(self.reference).zfill(20)
        return (VERSION+iban+euros+cents+VARALLA+reference+self.due_date.strftime('%y%m%d'))

    def total_calculate(self):
        self.total = 0.00
        for item in self.products:
            item['total'] = item['price_per'] * item['count']
            self.total = self.total + item['price_per'] * item['count']

    def pdf_invoice_creator(self, TEMPLATE_HTML, OUTPUT_FILE_NAME):
        self.validate_input()
        if (len(self.errors) != 0):
            print ("\n".join(self.errors))
            return

        with open(os.path.abspath(TEMPLATE_HTML)) as html_file:
            parsed_page = BeautifulSoup(html_file, "lxml")

        self.total_calculate()

        for target in self.targets:
            for item in parsed_page.findAll(id=target):
                if type(self.__dict__[target]) == float:
                    item.string = format(self.__dict__[target], '.2f')
                elif type(self.__dict__[target]) == datetime.datetime:
                    item.string = str(self.__dict__[target].strftime('%d.%m.%Y'))
                else:
                    item.string = str(self.__dict__[target])

        for item in range (len(self.products)):
            for value in self.products[item]:
                src = "{a}_{d}".format(a=item+1, d=value)
                for x in parsed_page.findAll(id=src):
                    if type(self.products[item-1][value]) == float:
                        x.string = format(self.products[item-1][value],'.2f')
                    else:
                        x.string = str(self.products[item-1][value])

        code = BeautifulSoup(code128.svg(self.code_creator()), 'lxml')
        code.find('svg')['height'] = "40"
        code.find('svg')['width'] = "528"
        code.find('svg')['viewbox'] = "0 0 1058 50"
        code.find('svg')['preserveAspectRatio']="xMinYMin meet"
        parsed_page.find(id='barcode').append(code)

        self.pdf_file = pdfkit.from_string(str(parsed_page), False, options=config.PDFKIT_CONFIG)

        with open(OUTPUT_FILE_NAME, 'wb') as newfile:
            newfile.write(self.pdf_file)

        return True

    def merge_with_pdf(self, file2, filename):
        merger = PdfFileMerger()
        merger.append(PdfFileReader(self.pdf_file))
        merger.append(PdfFileReader(file2))
        merger.write(filename)
