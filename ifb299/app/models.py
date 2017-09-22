from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=200, null=True)
    postcode = models.IntegerField(null=True)
    CHOICES = (('STUDENT', 'Student'),('BUSINESSMAN', 'Businessman'),('TOURIST', 'Tourist'))
    role = models.CharField(
        max_length=20,
        blank=False,
        default='STUDENT',
        choices=CHOICES,
    )

class State(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
# To get a list of places in a city, get a city object c and c.place_set.all()
class City(models.Model):
    name = models.CharField(max_length=200)
    #  on_delete=models.CASCADE is the default for ForeignKey
    state = models.ForeignKey(State)
    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    postcode = models.IntegerField()
    city_id = models.ForeignKey(City)
    category_id = models.ForeignKey(Category)
    date = models.DateTimeField('Date Uploaded')

    class Meta:
        ordering = ['date']

    def get_absolute_url(self):
         """
         Returns the url to access a particular instance of MyModelName.
         """
         return reverse('app:place_detail', args=[self.id])

    def __str__(self):
        return self.name
