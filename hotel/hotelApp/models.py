from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator , MaxValueValidator
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

# source myenv/bin/activate


class Room(models.Model):
    number = models.PositiveIntegerField(unique=True , validators=[MinValueValidator(1)] , verbose_name='Room number' , help_text='Rooms with room number greater than 1')
    type = models.CharField(max_length=20 , choices=[
        ('Single' , 'Single'),
        ('Double' , 'Double'),
        ('Suite' , 'Suite'),
        ('Studio' , 'Studio'),
        ('Deluxe room' , 'Deluxe room'),
        ('Villa' , 'Villa'),
        ('Family room' , 'Family room')
    ]
    , verbose_name="Room type")

    description = models.CharField(max_length=500 , null=True , blank=True)
    price_per_night = models.DecimalField(max_digits=10 , decimal_places=2 , verbose_name='Price/night ($)')


    def __str__(self):
        return f'Room {self.number} - {self.type}'


class Customer(AbstractUser):
    COUNTRY_CODE_CHOICES = [
    ('+30', 'Greece (+30)'),
    ('+44', 'United Kingdom (+44)'),
    ('+49', 'Germany (+49)'),
    ('+33', 'France (+33)'),
    ('+39', 'Italy (+39)'),
    ('+34', 'Spain (+34)'),
    ('+358', 'Finland (+358)'),
    ('+31', 'Netherlands (+31)'),
    ('+46', 'Sweden (+46)'),
    ('+41', 'Switzerland (+41)'),
    ('+43', 'Austria (+43)'),
    ('+351', 'Portugal (+351)'),
    ('+420', 'Czech Republic (+420)'),
    ('+32', 'Belgium (+32)'),
    ('+370', 'Lithuania (+370)'),
    ('+372', 'Estonia (+372)'),
    ('+371', 'Latvia (+371)'),
    ('+48', 'Poland (+48)'),
    ('+386', 'Slovenia (+386)'),
    ('+385', 'Croatia (+385)'),
]
    
    phone_regex = RegexValidator(
    regex=r'^\d{6,15}$',
    message="Enter a valid phone number (6-15 digits)."
    )    

    country_code = models.CharField(max_length=5, choices=COUNTRY_CODE_CHOICES, default='+30')
    phone_number = models.CharField(validators=[phone_regex], max_length=15 , null=False , blank=False)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)] , default=18 , null=False , blank=False)
    email = models.EmailField(unique=True) # override
    first_name = models.CharField(verbose_name='First name')
    last_name = models.CharField(verbose_name='Last name')


    class Meta:
        unique_together = ('country_code' , 'phone_number')        

    def save(self, *args, **kwargs):
        if not self.username:
            firstLastName = f"{self.first_name.lower()}-{self.last_name.lower()}"
            username = firstLastName

            counter = 1
            while Customer.objects.filter(username=username).exists():
                username = f"{firstLastName}-{counter}"
                counter += 1

        self.username = username            
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'
    


class Booking(models.Model):
    customer = models.ForeignKey(Customer , on_delete=models.CASCADE , related_name='bookings')
    room = models.ForeignKey(Room , on_delete=models.CASCADE , related_name='bookings')
    check_in = models.DateField(auto_now=False , null=False , blank=False , verbose_name='Check-in Date')
    check_out = models.DateField(auto_now=False , null=False , blank=False , verbose_name='Check-out Date')
    created_at = models.DateTimeField(auto_now_add=True)
    people = models.IntegerField(validators=[MinValueValidator(1) , MaxValueValidator(20)] , verbose_name='Number of people')
    #days = θα βγαινει η διαφορα απο το check-out -  check-in


    def __str__(self):
        return f'{self.id}'



class Payment(models.Model):
    booking = models.ForeignKey(Booking , on_delete=models.CASCADE , related_name='payments')
    amount = models.DecimalField(max_digits=10 , decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20 , choices=
                              [
                                  ('Pending' , 'Pending'),
                                  ('Completed' , 'Completed'),
                                  ('Failed' , 'Failed'),
                                  ('Cancelled' , 'Cancelled')
                              ] , default='Pending')
    

    #def __str__(self):
    #    return f'Amount of booking #{self.booking}: {self.amount}\nPayment Date: {self.payment_date}\nPayment status: {self.status}'