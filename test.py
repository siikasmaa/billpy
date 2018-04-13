# -*- coding: utf-8 -*-
import unittest
from writer import Invoice
import datetime

test_values = {
    'bic': 'NDEAFIHH',
    'iban': 'FI46 1111 2222 3333 44',
    'due_date': (datetime.datetime.today() + datetime.timedelta(days=3)).strftime("%d.%m.%Y"),
    'date': datetime.datetime.today().strftime("%d.%m.%Y"),
    'number': 123123123,
    'reference': 12312312,
    'message': 'Testmessage',
    'payer_name': 'Albin Albinsson',
    'payer_adress_1': 'Adress one',
    'payer_adress_2': 'Adress two',
    'payer_adress_3': 'Adress three',
    'total': 0.00,
    'products': [
    {
        'product':'Test',
        'price_per':5.00,
        'count':10
    },
    {
        'product':'Test2',
        'price_per':6.76,
        'count':32
    },
    {
        'product':'Test3',
        'price_per':2.13,
        'count':2
    }]
}

class TestInvoice(unittest.TestCase):
    def test_regular_functionality(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.validate_input()
        test_invoice = "test_invoice/test_invoice.html"
        self.assertEqual(len(inv.errors), 0, msg="\n"+"\n".join(inv.errors))
        self.assertTrue(inv.pdf_invoice_creator(test_invoice, "./output.pdf"), msg="\n"+"\n".join(inv.errors))

    def test_no_data(self):
        inv = Invoice()
        inv.validate_input()
        self.assertNotEqual(len(inv.errors), 0, msg="\n"+"\n".join(inv.errors))

    def test_failed_iban(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.set_iban("31 6601 0003 7474 82")
        inv.validate_input()
        self.assertIn("Incorrect format for IBAN", inv.errors, msg="\n"+"\n".join(inv.errors))
        self.assertEqual(len(inv.errors), 1, msg="\n"+"\n".join(inv.errors))

    def test_failed_bic(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.set_bic("")
        inv.validate_input()
        self.assertIn("Incorrect format for BIC", inv.errors, msg="\n"+"\n".join(inv.errors))
        self.assertEqual(len(inv.errors), 1, msg="\n"+"\n".join(inv.errors))

    def test_failed_number(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.set_number("AABAFI22")
        inv.validate_input()
        self.assertIn("Incorrect format for invoice number", inv.errors, msg="\n"+"\n".join(inv.errors))
        self.assertEqual(len(inv.errors), 1, msg="\n"+"\n".join(inv.errors))
        inv.set_number("")
        inv.validate_input()
        self.assertIn("Incorrect format for invoice number", inv.errors, msg="\n"+"\n".join(inv.errors))
        self.assertEqual(len(inv.errors), 1, msg="\n"+"\n".join(inv.errors))

    def test_failed_date(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.set_date("12.31.2017")
        inv.validate_input()
        self.assertEqual(len(inv.errors), 1, msg="\n"+"\n".join(inv.errors))

    def test_total_count(self):
        inv = Invoice()
        inv.load_from_data(test_values)
        inv.total_calculate()
        self.assertEqual(inv.total, 270.58, msg="\n"+"\n".join(inv.errors))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
