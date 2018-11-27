from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import Context, loader
import csv
from datetime import datetime

from .models import *
from .forms import *

import io
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# Create your views here.
from django.views.generic import TemplateView

############################## The basic dashboard #############################

def dash(request):
    return render(request, 'ASP_app/dashboard.html')


################################ Ordering items ################################

def startOrder(request):
    if request.method == "POST":
        form = StartOrderForm(request.POST)
        if form.is_valid():
            print("startorder is valid")
            clinic = Clinic.objects.get(pk=form.cleaned_data['destination'])
            prio = form.cleaned_data['priority']
            newOrder = Order(priority=prio, destination=clinic)
            newOrder.save()
            medicines = {'medicines': Medicine.objects.values(), 'order':newOrder}
            return render(request, 'ASP_app/orderSupplies.html', medicines)

    clinics = {"clinics": Clinic.objects.values()}
    return render(request, 'ASP_app/startOrder.html', clinics)


def orderSupplies(request):
    if request.method == "POST":
        if OrderSuppliesForm(request.POST).is_valid():
            orders = newMedicineOrder(request.POST)
            return render(request, 'ASP_app/orderSupplies.html', orders)

        elif ChangeSuppliesForm(request.POST).is_valid():
            orders = changeMedicineOrder(request.POST)
            return render(request, 'ASP_app/orderSupplies.html', orders)

        elif DeleteSuppliesForm(request.POST).is_valid():
            orders = deleteMedicineOrder(request.POST)
            return render(request, 'ASP_app/orderSupplies.html', orders)

        elif CancelOrderForm(request.POST).is_valid():
            CancelOrderedItems(request.POST)
            return redirect('/dashboard')

        elif ConfirmOrderForm(request.POST).is_valid():
            return redirect('/dashboard')

    medicines = {'medicines': Medicine.objects.values()}
    return render(request, 'ASP_app/orderSupplies.html', medicines)

def getOrderParams(processedForm):
    ordID = processedForm.cleaned_data['orderID']
    ord = Order.objects.get(pk=ordID)
    returnDict = {
                    'items':OrderedItems.objects.filter(orderID=ord),
                    'medicines': Medicine.objects.values(),
                    'order':ord,
                }
    return returnDict

def itemExists(medicine, ord):
    orderItems = OrderedItems.objects.filter(orderID=ord.pk)
    for item in orderItems:
        if item.medicine == medicine:
            return item

def newMedicineOrder(form):
    processedForm = OrderSuppliesForm(form)
    processedForm.is_valid()
    quant = processedForm.cleaned_data['quantity']
    med = Medicine.objects.get(pk=processedForm.cleaned_data['medicine'])
    ord = Order.objects.get(pk=processedForm.cleaned_data['orderID'])
    if itemExists(med, ord):
        item = itemExists(med, ord)
        changeMedicineOrder(item=itemExists(med, ord), quantity=quant)
    else:
        newItem = OrderedItems(quantity=quant, medicine=med, orderID=ord)
        newItem.save()
    return getOrderParams(processedForm)

def changeMedicineOrder(form=None, item=None, quantity=None):
    if form:
        processedForm = ChangeSuppliesForm(form)
        processedForm.is_valid()
        item = OrderedItems.objects.get(id=processedForm.cleaned_data['itemID'])
        item.quantity = processedForm.cleaned_data['quantity']
        item.save()
        return getOrderParams(processedForm)
    elif item and quantity:
        item = OrderedItems.objects.get(pk=item.pk)
        item.quantity += quantity
        item.save()

def deleteMedicineOrder(form):
    processedForm = DeleteSuppliesForm(form)
    processedForm.is_valid()
    OrderedItems.objects.filter(id=processedForm.cleaned_data['itemID']).delete()

    return getOrderParams(processedForm)

def CancelOrderedItems(form):
    processedForm = CancelOrderForm(form)
    processedForm.is_valid()
    id = processedForm.cleaned_data['orderID']
    items = OrderedItems.objects.filter(orderID=id)
    for item in items:
        item.delete()
    order = Order.objects.get(pk=id)
    order.delete()

###################### Viewing the orders and their status #####################

def orderStatus(request):
    if request.method == "POST":
        form = StatusChangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['ordID']:
                new_order = Order.objects.get(id=form.cleaned_data['ordID'])
            else:
                pass
            new_order.status = form.cleaned_data['choice']
            new_order.save()

            orders = {'orders':Order.objects.all(), 'isWarehouse':True}
            return redirect('/orderStatus', orders)

    orders = {'orders':Order.objects.all(), 'isWarehouse':True}
    return render(request, 'ASP_app/orderStatus.html', orders)

def downloadLabel(request):
    orderID = request.GET.get('order')
    orderItems = OrderedItems.objects.filter(orderID=orderID)
    destination = Order.objects.get(pk=orderID).destination.name
    print("ik kom in downloadLabel")
    # the creation of the actual pdf

    pdf_buffer = io.BytesIO()
    my_doc = SimpleDocTemplate(pdf_buffer)
    sample_style_sheet = getSampleStyleSheet()

    flowables = []

    paragraph_1 = Paragraph("<h1>Order ID: " + str(orderID) + "</h1>", sample_style_sheet['Heading1'])
    paragraph_2 = Paragraph("<h3>Content of order</h3>",               sample_style_sheet['BodyText'])
    flowables.append(paragraph_1)
    flowables.append(paragraph_2)

    for item in orderItems:
        text = "<p>medicine: {}, quantity: {}, category: {} </p>".format(item.medicine.description, item.quantity, item.medicine.category)
        paragraph = Paragraph( text, sample_style_sheet['BodyText'])
        flowables.append(paragraph)

    paragraph = Paragraph("<h3>Final destination: </h3>" + destination,  sample_style_sheet['BodyText'])
    flowables.append(paragraph)

    my_doc.build(flowables)

    pdf_value = pdf_buffer.getvalue()
    pdf_buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="some_file.pdf"'

    response.write(pdf_value)
    return response


##################### Warehouse Personnel view and functions ###################

def priorityQueue(request):
    if request.method == "POST":
        form = StatusChangeForm(request.POST)
        if form.is_valid():
            new_order = Order.objects.get(id=form.cleaned_data['ordID'])
            new_order.status = form.cleaned_data['choice']
            new_order.save()

            orders = {'orders':Order.objects.all()}
            return redirect('/priorityQueue', orders)

    orders = {'orders':Order.objects.all()}

    return render(request, 'ASP_app/priorityQueue.html', orders)

def packing(request):
    if request.method == "POST":
        form = StatusChangeForm(request.POST)
        if form.is_valid():
            order = Order.objects.get(id=form.cleaned_data['ordID'])
            order.status = form.cleaned_data['choice']
            order.save()

            orderItems = OrderedItems.objects.filter(orderID=order.id)

            curOrder = {'order':order,'orderItems':orderItems}
            return render(request, 'ASP_app/packing.html', curOrder)
    return render(request, 'ASP_app/packing.html', '')

####################### Dispatcher views and functions #########################

def dispatch(request):
    #show orders that are in 'Queued for Dispatch' status
    #With ~5.0 kg ordered by priorityQueue

    orders = {'orders':Order.objects.filter(status='Queued for Dispatch').order_by('priority')}
    # if not orders:
    #     orders= {'orders':Order.objects.all().filter(priority='Medium' or 'Low')}

    maxweight=5.0
    curweight=0
    counter=0
    for order in Order.objects.filter(status='Queued for Dispatch').order_by('-priority'):
        if curweight+order.totalWeight()<maxweight:
            curweight+=order.totalWeight()
        else:
            break
        counter+=1

    orders = {'orders' : Order.objects.filter(status='Queued for Dispatch').order_by('-priority')[:counter],
              'counter' : counter,

    }

    return render(request, 'ASP_app/dispatch.html', orders)

def dispatching(request):
    #page that confirms dispatch and show csv download menu

    #get number of orders from priority queue
    if request.method == "POST":
        counter=int(request.POST['counter'])

    #store number of orders in dictionary
    orders={'orders' : Order.objects.filter(status='Queued for Dispatch').order_by('-priority')[:counter],
        'counter' : counter,
    }

    for order in orders['orders']:
        order.status = 'Dispatched'
        order.dispatchTime= datetime.now()
        order.save()

    #sum total weight of orders to be loaded
    sum=0
    for order in orders['orders']:
        sum+=order.totalWeight()
    orders['sum']=sum

    return render(request, 'ASP_app/dispatching.html', orders)

def csvView(request):
    if request.method =="POST":
        counter=int(request.POST['counter'])

    print (counter)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Destination.csv"'

    orders = {'orders': Order.objects.all().order_by('-priority')[:counter]}

    #empty list to store data
    data=[]
    for order in orders['orders']:
        data.append((order.id , order.destination, order.destination.longitude,
                    order.destination.latitude, order.destination.altitude  ))
    #print (data)
    t = loader.get_template('CSV_file_format.txt')
    c = dict({
        'data': data,
    })
    response.write(t.render(c))
    return response




def splitOrders(orderDict):
    maxWeight = 5.0
    dispatches = {"0" : []}
    current = 0
    totWeight = 0
    for order in orderDict['orders']:
        if order.status == "Queued for Dispatch":
            if totWeight + order.totalWeight() > maxWeight:
                current += 1
                dispatches[str(current)] = [order]
                totalWeight = order.totalWeight()
            else:
                dispatches[str(current)].append(order)
                dispatches[str(current)].append(order)
                totWeight += order.totalWeight()
                print("total weight: {}".format(totWeight))
    print(dispatches["0"])
    return {'orders': dispatches}

def getPriorityOrders(orderdict):

    maxWeight=5.0
    curweight=0
    orderd=dict()
    orderlist=[]

    for order in orderdict['orders']:
        if order.priority=='High':
            orderd['order']=order
            orderlist.append(order)
        #print(order)
    orderd['order']=orderlist
    #print(orderd)
    #print (orderl['prior'])
    return orderd




##################### User views and User related function #####################

def profile(request):
    users= {'users': User.objects.values() }
    return render(request, 'ASP_app/userProfile.html', users)
