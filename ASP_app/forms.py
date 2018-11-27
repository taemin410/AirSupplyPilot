from django import forms
from .models import Order

from .models import Clinic

class StatusChangeForm(forms.Form):
    CHOICES = (('Queued for Processing','Queued for Processing'),
        ('Processing by Warehouse','Processing by Warehouse'),
        ('Queued for Dispatch','Queued for Dispatch'),
        ('Dispatched','Dispatched'),
        ('Delivered','Delivered'))
    ordID = forms.IntegerField()
    choice = forms.ChoiceField(choices=CHOICES)

class DispatchForm(forms.Form):
    counter = forms.IntegerField()
    #ordID = forms.CharField(widget = forms.HiddenInput(), required = False)

class orderForm(forms.ModelForm):
	ordQuantity = forms.IntegerField()

class dispatchingForm(forms.ModelForm):
    class Meta:
        model= Order
        fields = '__all__'



def getClinics():
    some = set()
    allClinics = Clinic.objects.all()
    for clin in allClinics:
        some.update([(clin.pk, clin.pk)])
    return some


########################### Ordering medicine forms ############################

class StartOrderForm(forms.Form):
    CHOICES = (('Low','Low'),
        ('Medium','Medium'),
        ('High','High'))
    priority = forms.ChoiceField(choices=CHOICES)
    destination = forms.ChoiceField(choices=getClinics())

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
