from django.contrib import admin

from .models import Medicine, Clinic, Order, OrderedItems, ClinicDistances#, ClinicManager, WarehousePersonnel, Dispatcher
# Register your models here.



def specifyRole():
    pass

def sendToken():
    pass

def sendResetUrl():
    pass

def viewRegisteredUsers():
    pass


admin.site.add_action(specifyRole)
admin.site.add_action(sendToken)
admin.site.add_action(sendResetUrl)
admin.site.add_action(viewRegisteredUsers)
#admin.site.add_action(CustomUser)

admin.site.register(Medicine)
#admin.site.register(Clinic)
admin.site.register(Order)
admin.site.register(OrderedItems)
admin.site.register(ClinicDistances)
#admin.site.register(CustomUser)


#
# admin.site.register(ClinicManager)
# admin.site.register(WarehousePersonnel)
# admin.site.register(Dispatcher)
