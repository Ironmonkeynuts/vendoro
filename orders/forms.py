from django import forms


class QuantityAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
