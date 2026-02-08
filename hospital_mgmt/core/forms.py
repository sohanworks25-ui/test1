from django import forms

from .models import OPDBill, OPDLineItem, PathologyBill, PathologyLineItem, Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "age", "sex", "mobile_number", "refer_doctor", "consultant_doctor"]


class OPDBillForm(forms.ModelForm):
    class Meta:
        model = OPDBill
        fields = ["patient", "discount", "paid_amount", "billing_date"]


class OPDLineItemForm(forms.ModelForm):
    class Meta:
        model = OPDLineItem
        fields = ["item", "quantity", "unit_price"]


class PathologyBillForm(forms.ModelForm):
    class Meta:
        model = PathologyBill
        fields = ["patient", "pathologist", "discount", "paid_amount", "billing_date"]


class PathologyLineItemForm(forms.ModelForm):
    class Meta:
        model = PathologyLineItem
        fields = ["test", "quantity", "unit_price"]
