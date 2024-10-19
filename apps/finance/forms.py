from django.forms import inlineformset_factory, modelformset_factory ,ModelForm, Select,DateInput
from .models import Due
from .models import Invoice, InvoiceItem, Receipt

InvoiceItemFormset = inlineformset_factory(
    Invoice, InvoiceItem, fields=["description", "amount"], extra=1, can_delete=True
)

InvoiceReceiptFormSet = inlineformset_factory(
    Invoice,
    Receipt,
    fields=("amount_paid", "date_paid", "comment"),
    extra=0,
    can_delete=True,
)

Invoices = modelformset_factory(Invoice, exclude=(), extra=4)



class DueForm(ModelForm):
    class Meta:
        model = Due
        fields = ['due_status', 'amount', 'due_date']
        widgets = {
            'due_status': Select(choices=Due.due_choice),
            'due_date': DateInput(attrs={'type': 'date'}),
        }