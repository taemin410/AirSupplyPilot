import datetime

from django.db import models
from django.utils import timezone
from django import forms
import os
from django.contrib.auth.models import AbstractUser
# Create your models here.

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

LOW = 0
MEDIUM = 1
HIGH = 2

PRIORITY_CHOICES = (
    (LOW, 'Low'),
    (MEDIUM, 'Medium'),
    (HIGH, 'High'),
)

STATUS_CHOICES = (
    ('Queued for Processing','Queued for Processing'),
    ('Processing by Warehouse','Processing by Warehouse'),
    ('Queued for Dispatch','Queued for Dispatch'),
    ('Dispatched','Dispatched'),
    ('Delivered','Delivered')
)

class Medicine(models.Model):
    category = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
    shippingWeight = models.FloatField()
    picture = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return "medicine: {}, category: {}, weight: {}".format(self.description, self.category, self.shippingWeight)

class Clinic(models.Model):
    name = models.CharField(max_length=256)
    longitude =models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.IntegerField()

    def __str__(self):
        return "clinic: {}".format(self.name)

class Order(models.Model):
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    status = models.CharField(choices=STATUS_CHOICES, max_length=256, blank=True)
    orderTime = models.DateTimeField(auto_now_add=True, blank=True)
    dispatchTime = models.DateTimeField(blank=True, null=True)
    deliveryTime = models.DateTimeField(blank=True, null=True)
    destination = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    def totalWeight(self):
        orderItems = OrderedItems.objects.filter(orderID=self.pk)
        total = 0
        for item in orderItems:
            total += item.weight()
        return round(total,2)

    def getContents(self):
        orderItems = OrderedItems.objects.filter(id=self.id)
        return [Medicine.objects.get(id=item.id).description for item in orderItems]

    def choices(self):
        return ['Queued for Processing', 'Processing by Warehouse','Queued for Dispatch', 'Dispatched', 'Delivered']

    def __str__(self):
        return "orderID: {}, for: {}, priority: {}".format(self.pk, self.destination.name, self.priority)

class OrderedItems(models.Model):
    quantity = models.IntegerField()
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    orderID = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return "order for: {}, medicine: {}, quantity: {}".format(self.orderID, self.medicine, self.quantity)

    def weight(self):
        itemWeight = self.quantity * self.medicine.shippingWeight
        return round(itemWeight,2)

class ShippingLabel(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # contents = models.CharField(max_length=512) #OrderedItems.getContents(orderID) # does this even work?
    finalDestination = models.CharField(max_length=256)

    def contents(self):
        return OrderedItems.objects.filter(orderID=self.order.pk)

class Dispatch(models.Model):
    orderID = models.ForeignKey(Order, on_delete=models.CASCADE)
    droneID = models.IntegerField()

class User(models.Model):
    email = models.EmailField("email address", unique=True)
    username = models.CharField("username", max_length=30, blank=True, unique=True)
    firstname= models.CharField("firstname",blank=True, max_length=20)
    lastname = models.CharField("lastname", blank=True, max_length=20)
    password= models.CharField("password", blank=True, max_length=30)

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.username

    def getusername(self):
        for user in User:
            spcificuser= User.objects.get(id=user.username)
        return specificuser

class ProcessedDispatch(models.Model):
    dispatchID = models.ForeignKey(Dispatch, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)

#
# class CustomUser(AbstractUser):
#     pass
#
# class ClinicManager(CustomUser):
#     clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
#
#     def placeOrder():
#         pass
#
#     def viewOrders():
#         pass
#
#     def cancelOrder():
#         pass
#
#     def updateOrderStatus():
#         pass
#
# class WarehousePersonnel(CustomUser):
#
#     def viewOrder():
#         pass
#
#     def removeOrder():
#         pass
#
#     def updateOrderStatus():
#         pass
#
# class Dispatcher(CustomUser):
#
#     def viewOrder():
#         pass
#
#     def removeOrder():
#         pass
#
#     def updateOrderStatus():
#         pass
#
#     def downloadItinerary():
#         pass
