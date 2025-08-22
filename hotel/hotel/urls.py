from django.contrib import admin
from django.urls import path , include
from rest_framework.routers import DefaultRouter
from hotelApp.views import *

router = DefaultRouter()
router.register(r'rooms' , RoomViewSet)
router.register(r'customers' , CustomerViewSet)
router.register(r'bookings' , BookingViewSet)
router.register(r'payments' , PaymentViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , include(router.urls))
]
