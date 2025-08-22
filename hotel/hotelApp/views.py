from rest_framework import viewsets
from .serializers import *
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Room
from django.db.models import Q
from datetime import date

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def list(self, request, *args, **kwargs):
        past_bookings = Booking.objects.filter(check_out__lte = date.today())
        past_bookings.delete()
        return super().list(request, *args, **kwargs)


    def create_or_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room_id = serializer.validated_data['room'].id
        room = Room.objects.get(id=room_id)

        new_check_in_date = serializer.validated_data['check_in']
        new_check_out_date = serializer.validated_data['check_out']

        overlapping_booking = Booking.objects.filter( Q(room=room) & Q(check_in__lte = new_check_out_date) & Q(check_out__gte = new_check_in_date) )
                                
        if(overlapping_booking):
            room_dates = []
            room_dates.append(f'Room #{room.id} is not available for the following dates:')

            for i in Booking.objects.filter(room=room):
                room_dates.append(f'{i.check_in.strftime("%d-%m-%Y")} to {i.check_out.strftime("%d-%m-%Y")}')
      
            return Response(
                                {
                                'message': room_dates,
                                'redirect_url': 'http://127.0.0.1:8000/payments/'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                  
        booking = serializer.save()
        return Response(
                            {
                                'message': f'Booking #{booking.id} created successfully✅',
                                'data': serializer.data,
                                'redirect_url': 'http://127.0.0.1:8000/payments/'
                            },
                            status=status.HTTP_201_CREATED
                        )        
        

    def create(self, request, *args, **kwargs):
        return self.create_or_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.create_or_update(request, *args, **kwargs)

        
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def list(self, request, *args, **kwargs):
        from .serializers import BookingInfoSerializer
        bookings = Booking.objects.all()

        serializer = BookingInfoSerializer(bookings , many=True)
        return Response(
                {
                    'Info':serializer.data
                }

        )
    
    def perform_create(self , serializer):
        booking = serializer.validated_data['booking']
        if(Payment.objects.filter(booking = booking , status='Completed')).exists():
            raise ValidationError(f'Booking has already a completed payment.')
        serializer.save(status = 'Completed')            

    #def update(self , request , *args , **kwargs):
        
    
