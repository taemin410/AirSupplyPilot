import io
import os
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from .models import *
from users.models import Clinic
from datetime import datetime
from .forms import *
from django import template
register = template.Library()

from users.forms import CustomUserChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# for the routeplanning
import itertools

import csv
from django.template import Context, loader
from django.core.mail import EmailMessage

# Create your views here.
from django.views.generic import TemplateView

############################## The basic dashboard #############################

def dash(request):
    return render(request, 'ASP_app/dashboard.html')


################################ Ordering items ################################

def startOrder(request):
    if request.user.is_authenticated and request.user.role == "Clinic Manager":
        if request.method == "POST":
            form = StartOrderForm(request.POST)
            if form.is_valid():
                clinic = request.user.clinic
                prio = form.cleaned_data['priority']
                order = Order(priority=prio, destination=clinic)
                order.status = "Incomplete"
                order.save()
                medicines = {'medicines': Medicine.objects.values(), 'order':order}
                medicines['current'] = os.getcwd()
                return render(request, 'ASP_app/orderSupplies.html', medicines)

        clinics = {"clinics": Clinic.objects.values()}
        return render(request, 'ASP_app/startOrder.html', clinics)
    else:
        return redirect('/dashboard')


def orderSupplies(request):
    if request.user.is_authenticated and  request.user.role == "Clinic Manager":
        if request.method == "POST":
            if OrderSuppliesForm(request.POST).is_valid():
                orders = newMedicineOrder(request.POST)
                orders['current'] = os.getcwd()
                return render(request, 'ASP_app/orderSupplies.html', orders)

            elif ChangeSuppliesForm(request.POST).is_valid():
                orders = changeMedicineOrder(request.POST)
                orders['current'] = os.getcwd()
                return render(request, 'ASP_app/orderSupplies.html', orders)

            elif DeleteSuppliesForm(request.POST).is_valid():
                orders = deleteMedicineOrder(request.POST)
                orders['current'] = os.getcwd()
                return render(request, 'ASP_app/orderSupplies.html', orders)

            elif CancelOrderForm(request.POST).is_valid():
                CancelOrderedItems(request.POST)
                return redirect('/orderStatus')

            elif ConfirmOrderForm(request.POST).is_valid():
                ConfirmOrderedItems(request.POST)
                return redirect('/orderStatus')

        medicines = {'medicines': Medicine.objects.values()}
        return render(request, 'ASP_app/orderSupplies.html', medicines)
    else:
        return redirect('/dashboard')

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

def ConfirmOrderedItems(form):
    processedForm = ConfirmOrderForm(form)
    processedForm.is_valid()
    id = processedForm.cleaned_data['orderID']
    order = Order.objects.get(pk=id)
    order.status = "Queued for Processing"
    order.save()


###################### Viewing the orders and their status #####################

def orderStatus(request):
    if request.user.is_authenticated and request.user.role == "Clinic Manager":
        if request.method == "POST":
            form = StatusChangeForm(request.POST)
            if form.is_valid():
                order = Order.objects.get(id=form.cleaned_data['ordID'])

                # update dispatch / delivery time for the HA
                if form.cleaned_data['choice'] == "Dispatched":
                    order.dispatchTime = datetime.now()
                elif form.cleaned_data['choice'] == "Delivered":
                    order.deliveryTime = datetime.now()

                # update order status
                order.status = form.cleaned_data['choice']
                order.save()
                orders = {'orders':Order.objects.filter(destination=request.user.clinic)}
                return redirect('/orderStatus', orders)

        orders = {'orders':Order.objects.filter(destination=request.user.clinic)}
        return render(request, 'ASP_app/orderStatus.html', orders)
    else:
        return redirect('/dashboard')

def downloadLabel(request):
    if request.user.is_authenticated and (request.user.role == "Clinic Manager" or request.user.role == "Warehouse Personnel"):
        orderID = request.GET.get('order')
        orderItems = OrderedItems.objects.filter(orderID=orderID)
        destination = Order.objects.get(pk=orderID).destination.name
        # the creation of the actual pdf

        pdf_buffer = io.BytesIO()
        my_doc = SimpleDocTemplate(pdf_buffer)
        sample_style_sheet = getSampleStyleSheet()

        flowables = []

        paragraph_1 = Paragraph("Order ID: " + str(orderID), sample_style_sheet['Heading1'])
        paragraph_2 = Paragraph("Content of order",          sample_style_sheet['BodyText'])
        flowables.append(paragraph_1)
        flowables.append(paragraph_2)

        for item in orderItems:
            text = "medicine: {}, quantity: {}, category: {}".format(item.medicine.description, item.quantity, item.medicine.category)
            paragraph = Paragraph( text, sample_style_sheet['BodyText'])
            flowables.append(paragraph)

        paragraph = Paragraph("Final destination: " + destination,  sample_style_sheet['BodyText'])
        flowables.append(paragraph)

        my_doc.build(flowables)

        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shippingLabel_'+orderID+'.pdf"'

        response.write(pdf_value)
        return response
    else:
        return redirect('/dashboard')

def cancelOrder(request):
    if request.user.is_authenticated and request.user.role == "Clinic Manager":
        if request.method == "POST":
            form = CancelOrderForm(request.POST)
            if form.is_valid():
                id = form.cleaned_data['orderID']
                items = OrderedItems.objects.filter(orderID=id)
                for item in items:
                    item.delete()
                order = Order.objects.get(pk=id)
                order.delete()
        orders = {'orders':Order.objects.filter(destination=request.user.clinic)}
        return render(request, 'ASP_app/orderStatus.html', orders)
    else:
        return redirect('/dashboard')

##################### Warehouse Personnel view and functions ###################

def priorityQueue(request):
    if request.user.is_authenticated and request.user.role == "Warehouse Personnel":
        if request.method == "POST":
            form = StatusChangeForm(request.POST)
            if form.is_valid():
                order = Order.objects.get(id=form.cleaned_data['ordID'])
                order.status = form.cleaned_data['choice']
                order.save()
        orders = {'orders':Order.objects.all().order_by('-priority')}
        return render(request, 'ASP_app/priorityQueue.html', orders)
    else:
        return redirect('/dashboard')

def packing(request):
    if request.user.is_authenticated and request.user.role == "Warehouse Personnel":
        if request.method == "POST":
            form = StatusChangeForm(request.POST)
            if form.is_valid():
                order = Order.objects.get(id=form.cleaned_data['ordID'])
                order.status = form.cleaned_data['choice']
                order.save()
                orderItems = OrderedItems.objects.filter(orderID=order.id)
                curOrder = {'order':order,'orderItems':orderItems}
                return render(request, 'ASP_app/packing.html', curOrder)
        elif request.method == "GET":
            ordID = request.GET.get('order')
            if not ordID:
                return render(request, 'ASP_app/packing.html', '')
            order = Order.objects.get(id=ordID)
            orderItems = OrderedItems.objects.filter(orderID=order.id)
            curOrder = {'order':order,'orderItems':orderItems}
            return render(request, 'ASP_app/packing.html', curOrder)
        return render(request, 'ASP_app/packing.html', '')
    else:
        return redirect('/dashboard')


####################### Dispatcher views and functions #########################

def dispatch(request):
    #show orders that are in 'Queued for Dispatch' status
    #With ~25.0 kg ordered by priority
    if request.user.is_authenticated and request.user.role == "Dispatcher":
        #the order is arranged by priority
        orders = {'orders':Order.objects.filter(status='Queued for Dispatch').order_by('-priority')}

        ordlist=[]

        maxweight=25.0
        curweight=0
        curweight+=1.2; #container weight is 1.2kg
        counter=0
        #counts the number of orders from priority list of orders that does not exceed 25kg total
        for order in Order.objects.filter(status='Queued for Dispatch').order_by('-priority'):
            if curweight+order.totalWeight()<maxweight:
                curweight+=order.totalWeight()
            else:
                break
            counter+=1
        orders = {'orders' : Order.objects.filter(status='Queued for Dispatch').order_by('-priority'),
                  'counter' : counter, 'ordlist' : ordlist,
        }
        #pass data of orders and counter
        return render(request, 'ASP_app/dispatch.html', orders)
    else:
        return redirect('/dashboard')

def dispatching(request):
    #page that confirms dispatch and show csv download menu
    if request.user.is_authenticated and request.user.role == "Dispatcher":
        ordlist=[]
        #get number of orders from priority queue
        if request.method == "POST":
            counter=int(request.POST['counter'])

        #store number of orders in dictionary
        orders={'orders' : Order.objects.filter(status='Queued for Dispatch').order_by('-priority')[:counter],
            'counter' : counter, 'ordlist' : ordlist,
        }
        orderstring=''

        for order in orders['orders']:
            ordlist.append(order.pk)
            orderstring+=str(order.pk)+","

        orderstring=orderstring[:-1]
        orders['ordlist']=orderstring

        #sum total weight of orders to be loaded
        sum=0.0
        for order in orders['orders']:
            sum+=order.totalWeight()
        sum+=1.2
        sum=round(sum,2)
        orders['sum']=sum

        return render(request, 'ASP_app/dispatching.html', orders)
    else:
        return redirect('/dashboard')

def csvView(request):
    if request.method =="POST":
        counter=int(request.POST['counter'])
    #accept counter as the indicater for orders to be dispatched

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Destination.csv"'

    orders = {'orders': Order.objects.filter(status='Queued for Dispatch').order_by('-priority')[:counter]}

    #empty list to store data
    data=[]
    for clinic in getRouteFromDict(orders['orders']):
        data.append((clinic.name, clinic.longitude,
                    clinic.latitude, clinic.altitude  ))
    t = loader.get_template('CSV_file_format.txt')
    c = dict({
        'data': data,
    })
    response.write(t.render(c))
    return response

def confirmDispatch(request):
    ordlist=""
    if request.method == "POST":
        counter=int(request.POST['counter'])
        ordlist+=str(request.POST['ordlist'])

    words = ordlist.split(",")

    #store number of orders in dictionary
    orders={'orders' : Order.objects.filter(status='Queued for Dispatch').order_by('-priority')[:counter],
        'counter' : counter, 'ordlist': ordlist,
    }
    name=[]
    orderids=dict()

    for order in orders['orders']:
        order.status = 'Dispatched'
        order.dispatchTime= datetime.now()
        order.save()
        name.append(order.destination)
        if order.destination in orderids:
            orderids[order.destination].append( order.pk )
        else:
            orderids[order.destination]= [order.pk]
    #make dictionary for orderids for clinics

    clinics={}
    for i in range(len(words)):
        clinics[name[i]]=Clinic.objects.filter(name=name[i])

    users=CustomUser.objects.filter(role="Clinic Manager")
    pdfemaildic=dict()
    userlist=[]

    for user in users:
        if user.clinic in clinics:
            userlist.append((user.clinic,user.email))

    for clinicb in userlist:
        if clinicb[0] in orderids:
            sendEmailPDF(request,clinicb[1],orderids[clinicb[0]])
            #send orderids and its clinic manager's email addresses

    return redirect('/dispatch')

def sendEmailPDF(request,email,orderids):

    #get list of orderIDs for that order
    orderID = orderids

    pdf_buffer = io.BytesIO()
    my_doc = SimpleDocTemplate(pdf_buffer)
    sample_style_sheet = getSampleStyleSheet()

    flowables = []

    #loop through each order to write in pdf file
    for orderid in orderID:
        orderItems = OrderedItems.objects.filter(orderID=orderid)
        destination = Order.objects.get(pk=orderid).destination.name

        paragraph_1 = Paragraph("Order ID: " + str(orderid), sample_style_sheet['Heading1'])
        paragraph_2 = Paragraph("Content of order",          sample_style_sheet['BodyText'])
        flowables.append(paragraph_1)
        flowables.append(paragraph_2)

        for item in orderItems:
            text = "medicine: {}, quantity: {}, category: {}".format(item.medicine.description, item.quantity, item.medicine.category)
            paragraph = Paragraph( text, sample_style_sheet['BodyText'])
            flowables.append(paragraph)

        paragraph = Paragraph("Final destination: " + destination,  sample_style_sheet['BodyText'])
        flowables.append(paragraph)

        my_doc.build(flowables)

    pdf_value = pdf_buffer.getvalue()
    pdf_buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="some_file.pdf"'

    response.write(pdf_value)

    #email message template
    email = EmailMessage(
        'Hello   ' + email,
        'Hi this is the confirmation for order ID:  '+ str(orderID) +' \n' +
        "The items are listed in the attached pdf file.  "  ,
        'EASTERNLONGLIONS@gmail.com',
        [email],
        ['cc@example.com'],
        reply_to=['EASTERNLONGLIONS@gmail.com'],
        headers={'Message-ID': 'Confirmation'},
    )
    email.attach('Confirmation.pdf', pdf_value, 'application/pdf')
    email.send(fail_silently=False)

    return response






##################### User views and User related function #####################

def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomUserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'ASP_app/userProfile.html', args)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ASP_app/change_password.html', {
        'form': form
    })

################################### routing ####################################

def addDistance(request):
    if request.method == "POST":
        form = AddDistanceForm(request.POST)
        if form.is_valid():
            clin1 = Clinic.objects.get(pk=form.cleaned_data['currentClin'])
            clin2 = Clinic.objects.get(pk=form.cleaned_data['nextClin'])
            dist = form.cleaned_data['distance']
            newDist = ClinicDistances(distance=dist, currentClinic=clin1, nextClinic=clin2)
            newDist.save()
            newDistReversed = ClinicDistances(distance=dist, currentClinic=clin2, nextClinic=clin1)
            newDistReversed.save()
            form = {'form': AddDistanceForm, 'added':"jaay"}
            return render(request, 'ASP_app/addDistance.html', form)

    form = {'form': AddDistanceForm, 'added':"nog niet"}
    return render(request, 'ASP_app/addDistance.html', form)


def DeleteOrder(request):
    if request.method == "POST":
        form = DeleteOrderForm(request.POST)
        processedForm.is_valid()
        id = processedForm.cleaned_data['orderID']
        order = Order.objects.get(orderID=id)
        order.delete()

def getRouteFromDict(ordersDict):
    sepMagic = separate(ordersDict)
    path = routeSorter(sepMagic)[0] # remove [0] to get the distance as [1]
    return path

def getRoute(request):
    orders = Order.objects.all()
    sepMagic = separate(orders)
    magic = routeSorter(sepMagic)[0] # remove [0] to get the distance as [1]
    paths = {'ordered':sepMagic,'paths':magic[0], 'dist':magic[1]}
    return render(request, "ASP_app/pathViewer.html", paths)

def distill(orderList):
    distilledOrders = []
    for order in orderList:
        inIt = False
        for distillOrder in distilledOrders:
            if order.destination.name == distillOrder.destination.name:
                if order.priority > distillOrder.priority:
                    distillOrder.priority = order.priority
                else:
                    inIt = True
        if not inIt:
            distilledOrders.append(order)
    return distilledOrders

def separate(orderList):
    orderList = distill(orderList)
    high = []
    medium = []
    low = []
    for order in orderList:
        if order.priority == 0:
            low.append(order.destination)
        elif order.priority == 1:
            medium.append(order.destination)
        elif order.priority == 2:
            high.append(order.destination)
    return [high, medium, low]

def routeSorter(orderedClinics):
    start = Clinic.objects.get(name="Queen Mary Hospital")
    goal = Clinic.objects.get(name="Queen Mary Hospital")
    routes = []

    if orderedClinics[0] != [] and orderedClinics[1] != [] and orderedClinics[2] != []:
        for med in range(len(orderedClinics[1])):
            highRoute, highDist = routeFinder(start, orderedClinics[0], orderedClinics[1][med])
            restMediumClinics = orderedClinics[1][:]
            del restMediumClinics[med]

            for low in range(len(orderedClinics[2])):
                medRoute, medDist = routeFinder(highRoute[-1], restMediumClinics, orderedClinics[2][low])
                restLowClinics = orderedClinics[2][:]
                del restLowClinics[low]

                lowRoute, lowDist = routeFinder(medRoute[-1], restLowClinics, goal)

                distance = highDist + medDist + lowDist
                allRoute = highRoute[:-1] + medRoute[:-1] + lowRoute
                routes.append((allRoute, distance))

    elif orderedClinics[0] != [] and orderedClinics[1] != []:
        for med in range(len(orderedClinics[1])):
            highRoute, highDist = routeFinder(start, orderedClinics[0], orderedClinics[1][med])
            restMediumClinics = orderedClinics[1][:]
            del restMediumClinics[med]

            medRoute, medDist = routeFinder(highRoute[-1], restMediumClinics, goal)

            distance = highDist + medDist
            allRoute = highRoute[:-1] + medRoute
            routes.append((allRoute, distance))


    elif orderedClinics[0] != [] and orderedClinics[2] != []:
        for low in range(len(orderedClinics[2])):
            highRoute, highDist = routeFinder(start, orderedClinics[0], orderedClinics[2][low])
            restLowClinics = orderedClinics[2][:]
            del restLowClinics[low]

            lowRoute, lowDist = routeFinder(highRoute[-1], restLowClinics, goal)

            distance = highDist + lowDist
            allRoute = highRoute[:-1] + lowRoute
            routes.append((allRoute, distance))

    elif orderedClinics[1] != [] and orderedClinics[2] != []:
        for low in range(len(orderedClinics[2])):
            medRoute, medDist = routeFinder(start, orderedClinics[1], orderedClinics[2][low])
            restLowClinics = orderedClinics[2][:]
            del restLowClinics[low]

            lowRoute, lowDist = routeFinder(medRoute[-1], restLowClinics, goal)

            distance = medDist + lowDist
            allRoute = medRoute[:-1] + lowRoute
            routes.append((allRoute, distance))


    elif orderedClinics[0] != []:
        highRoute, highDist = routeFinder(start, orderedClinics[0], goal)

        distance = highDist
        allRoute = highRoute
        routes.append((allRoute, distance))

    elif orderedClinics[1] != []:
        medRoute, medDist = routeFinder(start, orderedClinics[1], goal)

        distance = medDist
        allRoute = medRoute
        routes.append((allRoute, distance))

    elif orderedClinics[2] != []:
        lowRoute, lowDist = routeFinder(start, orderedClinics[2], goal)

        distance = lowDist
        allRoute = lowRoute
        routes.append((allRoute, distance))
    else:
        routes = (["error"],9999)

    return min(routes, key = lambda t: t[1])


def routeFinder(current, possibleNext, goal, path=[], dist=0):
    if possibleNext == []:
        return [current]+[goal], compDist([current]+[goal])

    possibleRoutes = list(itertools.permutations(possibleNext))
    distances = []

    for route in possibleRoutes:
        distance = compDist([current] + list(route) + [goal])
        distances.append(distance)
    route = [current] + list(possibleRoutes[distances.index(min(distances))]) + [goal]
    return route, min(distances)

def compDist(route):
    current = route[0]
    distance = 0
    for next in range(1,len(route)):
        distance += getDist(current,route[next])
        current = route[next]
    return distance

def getDist(cur, next):
    ClinicDistances.objects.filter(currentClinic=cur)
    for distance in ClinicDistances.objects.filter(currentClinic=cur):
        if distance.nextClinic == next:
            return distance.distance
    if cur == next:
        return 1
    else:
        return 999999
