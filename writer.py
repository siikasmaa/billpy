# -*- coding: utf-8 -*-
import pdfkit
from bs4 import BeautifulSoup
import code128
import datetime
import re
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
import openpyxl
import config

class Invoice():
    def __init__(self, data, DATEFORMAT="%d.%m.%Y"):
        try:
            self.bic = data['bic']
            self.iban = data['iban']
            self.due_date = datetime.datetime.strptime(data['due_date'], DATEFORMAT)
            self.number = data['number']
            self.date = datetime.datetime.strptime(data['date'], DATEFORMAT)
            self.reference = data['reference']
            self.message = data['message']
            self.payer_name = data['payer_name']
            self.payer_adress_1 = data['payer_adress_1']
            self.payer_adress_2 = data['payer_adress_2']
            self.payer_adress_3 = data['payer_adress_3']
            self.total = 0.00
            self.products = data['products']
            self.errors = []
            self.targets = ["bic", "iban", "due_date", "number", "date", "reference", "message", "payer_name", "payer_adress_1", "payer_adress_2", "payer_adress_3", "total"]
        except KeyError as failed_key:
            print ("Missing information for ", failed_key)
        except ValueError as value_err:
            print ("Non expected format for ", value_err)

    def validate_input(self):
        self.errors.clear()
        if not (re.compile("^[A-Za-z]{2}[0-9]{16}$").match(re.sub('\s+', '', self.iban))):
            self.errors.append("Iban is not in correct format")
        if not (re.compile("^[0-9]{1,6}\.[0-9]{1,2}$").match(str(self.total))):
            self.errors.append("Total is not in correct format")
        if not (re.compile("(^$)|(^[0-9]{3,20}$)").match(str(self.reference))):
            self.errors.append("Reference is not in correct format")
        if (self.due_date < datetime.datetime.today() or self.due_date < self.date):
            self.errors.append("Due date is not eligible")
        if (len(self.bic) != 8):
            self.errors.append("BIC not in correct format")
        if (len(self.products) == 0):
            self.errors.append("No products in invoice")
        for item in self.products:
            if ('product' not in item or 'price_per' not in item or 'count' not in item):
                self.errors.append("Information on product missing")

    def code_creator(self, VERSION="4", VARALLA="000"):
        iban = re.sub('\s+|[A-Za-z]+', '', self.iban)
        total = str(self.total).split(".")
        euros = total[0].zfill(6)
        cents = total[1].zfill(2)
        reference = str(self.reference).zfill(20)
        return (VERSION+iban+euros+cents+VARALLA+reference+self.due_date.strftime('%y%m%d'))

    def total_calculate(self):
        for item in self.products:
            item['total'] = item['price_per'] * item['count']
            self.total += item['price_per'] * item['count']

    def pdf_invoice_creator(self, TEMPLATE_HTML="/Users/jarl-ottosiikasmaa/Documents/Projects/lasku/Fakturapohja.htm", OUTPUT_FILE_NAME="/Users/jarl-ottosiikasmaa/Documents/Projects/lasku/out.pdf"):
        self.validate_input()
        if (len(self.errors) != 0):
            print ("\n".join(self.errors))
            return

        with open(os.path.abspath(TEMPLATE_HTML)) as html_file:
            parsed_page = BeautifulSoup(html_file, 'lxml')

        self.total_calculate()

        for target in self.targets:
            for item in parsed_page.findAll(id=target):
                if type(self.__dict__[target]) == float:
                    item.string = format(self.__dict__[target], '.2f')
                if type(self.__dict__[target]) == datetime.datetime:
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

        pdfkit.from_string(str(parsed_page), OUTPUT_FILE_NAME, options=config.PDFKIT_CONFIG)

    def merge_with_pdf(self, file2, filename):
        merger = PdfFileMerger()
        merger.append(PdfFileReader(self.pdf_file))
        merger.append(PdfFileReader(file2))
        merger.write(filename)

    def excel_data(workbook_file): #WORK ON
        wb = openpyxl.load_workbook(workbook_file, data_only=True)
        sheet = wb.active
        return sheet
