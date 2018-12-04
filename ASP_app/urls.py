from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
#from .views import HomePageView

urlpatterns = [
    # path(website extensie, view als in pagina laten zien, extra argumenten, name als in hoe django er universeel naar kan verwijzen)
    path('', views.dash, name='dashboard'),
    #path('', views.index, name='index'),
    path('orderSupplies/', views.orderSupplies, name='orderSupplies'),


    path('dashboard/', views.dash, name='dashboard'),
    path('orderSupplies/', views.orderSupplies, name='orderSupplies'),

    path('startOrder/', views.startOrder, name='startOrder'),

    path('priorityQueue/', views.priorityQueue, name='priorityQueue'),
    path('orderStatus/', views.orderStatus, name='orderStatus'),
    path('profile/', views.edit_profile, name='profile'),
    path('dispatch/', views.dispatch, name='dispatch'),
    path('dispatching/', views.dispatching, name='dispatching'),
    path('csv/', views.csvView, name='csv'),
    path('confirmDispatch/', views.confirmDispatch, name='confirmDispatch'),
    path('packing/', views.packing, name='packing'),
    path('sendEmailPDF/', views.sendEmailPDF, name='sendEmailPDF'),

    ## still testing
    path('downloadlabel', views.downloadLabel, name='download'),

    path('addDistance', views.addDistance, name='addDist'),
    path('cancelOrder/', views.cancelOrder, name='cancelOrder'),

    path('test', views.getRoute, name='test'),
    path('change_password/', views.change_password, name='change_password'),
]
