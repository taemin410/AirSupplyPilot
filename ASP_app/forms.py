from django import forms
from .models import Clinic, ClinicDistances
from datetime import datetime

class StatusChangeForm(forms.Form):
    CHOICES = (('Queued for Processing','Queued for Processing'),
        ('Processing by Warehouse','Processing by Warehouse'),
        ('Queued for Dispatch','Queued for Dispatch'),
        ('Dispatched','Dispatched'),
        ('Delivered','Delivered'))
    ordID = forms.IntegerField()
    choice = forms.ChoiceField(choices=CHOICES)
    # datetime = forms.DateTimeField()

class DispatchForm(forms.Form):
    ordID = forms.IntegerField()
    ordID = forms.CharField(widget = forms.HiddenInput(), required = False)


def getClinics():
    some = set()
    allClinics = Clinic.objects.all()
    for clin in allClinics:
        some.update([(clin.pk, clin)])
    return some


########################### Ordering medicine forms ############################

class StartOrderForm(forms.Form):
    CHOICES = ((0,'Low'),
        (1,'Medium'),
        (2,'High'))
    priority = forms.ChoiceField(choices=CHOICES)

class OrderSuppliesForm(forms.Form):
    orderID = forms.IntegerField()
    priority = forms.CharField(max_length=128)
    medicine = forms.IntegerField()
    quantity = forms.IntegerField()

class ChangeSuppliesForm(forms.Form):
    orderID = forms.IntegerField()
    priority = forms.CharField(max_length=128)
    quantity = forms.IntegerField()
    itemID = forms.IntegerField()

class DeleteSuppliesForm(forms.Form):
    orderID = forms.IntegerField()
    priority = forms.CharField(max_length=128)
    itemID = forms.IntegerField()
    delete = forms.CharField(max_length=32)

class CancelOrderForm(forms.Form):
    orderID = forms.IntegerField()
    cancel = forms.CharField(max_length=16)

class ConfirmOrderForm(forms.Form):
    orderID = forms.IntegerField()
    confirm = forms.CharField(max_length=16)

class AddDistanceForm(forms.Form):
    distance = forms.FloatField()
    currentClin = forms.ChoiceField(choices=getClinics())
    nextClin = forms.ChoiceField(choices=getClinics())

class DeleteOrderForm(forms.Form):
    orderID = forms.IntegerField()
    cancel = forms.CharField(max_length=16)
