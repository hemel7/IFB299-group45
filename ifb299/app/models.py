from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

###################
# User profile extends User model by linking it to the User model using OneToOne relationship
###################
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    postcode = models.IntegerField(null=True)
    CHOICES = (('STUDENT', 'Student'),('BUSINESSMAN', 'Businessman'),('TOURIST', 'Tourist'))
    role = models.CharField(
        max_length=20,
        blank=False,
        default='STUDENT',
        choices=CHOICES,
    )
    def __str__(self):
        return self.user.email


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

class Industry(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

###################
# get_absolute_url is required to be used for easy link setup
# If a template is passed a collection of instances of Place model,
# simply calling placeInstance.get_absolute_url will return the absolute URL.
###################
class Place(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    postcode = models.IntegerField()
    phone_number = models.IntegerField(null=True, blank=True)
    city_id = models.ForeignKey(City)
    category_id = models.ForeignKey(Category)
    industry = models.ForeignKey(Industry, null=True, blank=True)
    department = models.ManyToManyField(Department, blank=True, null=True)
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

class Review(models.Model):
    user = models.ForeignKey(User)
    place_id = models.ForeignKey(Place)
    comments = models.CharField(max_length=1000)
    CHOICES = ((1, 'One Star'),(2, 'Two Stars'),(3, 'Three Stars'),(4, 'Four Stars'),(5, 'Five Stars'))
    rating = models.IntegerField(
        blank = False,
        default = 3,
        choices = CHOICES,
    )
    def __str__(self):
        return self.comments


###################
# Saved place will have references to User model and Place models
# A user can have multiple places saved
# A place can be saved by multiple users
###################
class SavedPlace(models.Model):
    class Meta:
        unique_together = (('user', 'place'),)
    user = models.ForeignKey(User)
    place = models.ForeignKey(Place)

    def __str__(self):
        return self.user.username + self.place.name
