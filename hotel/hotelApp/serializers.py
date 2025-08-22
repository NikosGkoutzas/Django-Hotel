from rest_framework import serializers
from .models import *
from django import forms
from datetime import date , datetime


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'



class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(read_only=True)
    username = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id' , 'username' , 'first_name' , 'last_name' , 'email' , 'country_code' , 'phone_number' , 'age']
        widgets = {
            'country_code': forms.Select(),
            'phone_number': forms.TextInput()
        }



class BookingSerializer(serializers.ModelSerializer):  
    customer_details = serializers.SerializerMethodField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset = Customer.objects.all().distinct())
 
    class Meta:        
        model = Booking
        fields = ['id' , 'customer' , 'customer_details' , 'check_in' , 'check_out' , 'room' , 'people']
    
    def get_customer_details(self , obj): # otan kanw GET pairnw auta anti gia customer.id
        return f"{obj.customer.first_name} {obj.customer.last_name} ({obj.customer.email})"

    def validate(self , data):
        #request = self.context.get("request") 

        if(data['check_in'] > data['check_out']):    
            raise serializers.ValidationError(f'The check-out date must come after the check-in date.')
        if(data['check_in'] == data['check_out']): 
            raise serializers.ValidationError(f'A minimum of one night must be booked.')
        elif(data['check_in'] < date.today()):
            raise serializers.ValidationError(f'The check-in date must be on or after {date.today().strftime("%d-%m-%Y")}.')
        elif(data['check_out'] < date.today()):
            raise serializers.ValidationError(f'The check-out date must be on or after {date.today().strftime("%d-%m-%Y")}.')
            
        return data



class BookingInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    payment_id = serializers.SerializerMethodField()
    from .models import Payment

    class Meta:
        model = Booking
        fields = ['payment_id' , 'id' , 'name' , 'email' , 'room' , 'check_in' , 'check_out' , 'people' , 'amount' , 'status']

    def get_name(self , obj):
        return f'{obj.customer.first_name} {obj.customer.last_name}'
    
    def get_email(self , obj):
        return f'{obj.customer.email}'
    
    def get_amount(self , obj):
        return f'{abs(obj.check_in - obj.check_out).days * obj.room.price_per_night * obj.people} $'

    def get_status(self , obj):
        payment = obj.payments.first()
        if(payment):
            return payment.status
        return Payment._meta.get_field('status').get_default() # pairnei to meta antikeimeno apo to PaymentSerializer

    def get_payment_id(self, obj):
        payment = obj.payments.first()
        if(payment):
            return payment.id
        return f'Not created yet.' 


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id' , 'booking' , 'amount' , 'payment_date' , 'status']
        read_only_fields = ['amount' , 'status']

    def create(self , validated_data):
        booking = validated_data['booking']
        amount = abs(booking.check_in - booking.check_out).days * booking.people * booking.room.price_per_night
        validated_data['amount'] = amount
        return super().create(validated_data)
