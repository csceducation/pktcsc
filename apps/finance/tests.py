from django.test import TestCase
from django.utils import timezone
from apps.staffs.models import Staff
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from .models import Invoice, InvoiceItem, Receipt, Due

class InvoiceTestCase(TestCase):
    def setUp(self):
        # Set up initial data for testing
        self.staff = Staff.objects.get(id=1)
        self.student = Student.objects.get(id=2)
        self.invoice = Invoice.objects.create(student=self.student)
        self.invoice_item = InvoiceItem.objects.create(invoice=self.invoice, description="Tuition Fee", amount=1000)
        self.due = Due.objects.create(invoice=self.invoice, amount=1000, due_date=timezone.now().date())

    def test_invoice_balance(self):
        # Test the balance calculation
        self.assertEqual(self.invoice.balance(), 1000)

    def test_receipt_payment(self):
        # Test receipt payment and its impact on dues and invoice balance
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=500, received_by=self.staff)
        self.assertEqual(self.invoice.balance(), 500)
        self.assertEqual(Due.objects.get(invoice=self.invoice).amount, 500)

    def test_receipt_full_payment(self):
        # Test full payment via receipt and its impact on dues
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=1000, received_by=self.staff)
        self.assertEqual(self.invoice.balance(), 0)
        self.assertFalse(Due.objects.filter(invoice=self.invoice).exists())

    def test_due_deletion_on_payment(self):
        # Test that dues are deleted and logged correctly on full payment
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=1000, received_by=self.staff)
        self.assertEqual(self.invoice.get_past_dues[0]['amount'], '1000')

    def test_partial_payment_and_new_due_creation(self):
        # Test partial payment and creation of new due
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=500, received_by=self.staff)
        new_due_date = timezone.now().date() + timezone.timedelta(days=30)
        self.invoice.update_dues_based_on_receipt(600, new_due_date, next_due_amount=100)
        self.assertEqual(Due.objects.get(invoice=self.invoice).amount, 600)

    def test_due_extension(self):
        # Test extending due date
        new_due_date = timezone.now().date() + timezone.timedelta(days=30)
        self.due.extend_due(new_due_date)
        self.assertTrue(self.due.extended)
        self.assertEqual(self.due.due_date, new_due_date)

# Log all actions and account for amount flow
import logging

class TestLogger:
    def __init__(self):
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('test_log.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def log_action(self, action, details):
        self.logger.info(f"{action}: {details}")

test_logger = TestLogger()

class InvoiceTestCaseWithLogging(TestCase):
    def setUp(self):
        self.staff = Staff.objects.get(id=1)
        self.student = Student.objects.get(id=1)
        self.invoice = Invoice.objects.create(student=self.student)
        self.invoice_item = InvoiceItem.objects.create(invoice=self.invoice, description="Tuition Fee", amount=1000)
        self.due = Due.objects.create(invoice=self.invoice, amount=1000, due_date=timezone.now().date())
        test_logger.log_action("Setup", f"Created invoice {self.invoice} with due {self.due.amount}")

    def test_receipt_payment_with_logging(self):
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=500, received_by=self.staff)
        test_logger.log_action("Receipt Created", f"Receipt {receipt.Bill_No} for amount {receipt.amount_paid}")
        self.assertEqual(self.invoice.balance(), 500)
        test_logger.log_action("Balance Updated", f"New balance for invoice {self.invoice.id} is {self.invoice.balance()}")

    def test_receipt_full_payment_with_logging(self):
        receipt = Receipt.objects.create(Bill_No="12345", invoice=self.invoice, amount_paid=1000, received_by=self.staff)
        test_logger.log_action("Full Payment Receipt Created", f"Receipt {receipt.Bill_No} for amount {receipt.amount_paid}")
        self.assertEqual(self.invoice.balance(), 0)
        test_logger.log_action("Balance Cleared", f"Invoice {self.invoice.id} balance is now {self.invoice.balance()}")
        self.assertFalse(Due.objects.filter(invoice=self.invoice).exists())
        test_logger.log_action("Due Cleared", f"All dues cleared for invoice {self.invoice.id}")

    # Additional tests with logging as needed

if __name__ == '__main__':
    TestCase.main()
