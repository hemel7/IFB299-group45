from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, JsonResponse, QueryDict
from django.views import generic
from django.contrib import auth
from django.contrib.auth.models import User
from .models import UserProfile, Place, SavedPlace, Review, Category as Category_model
from django.contrib.auth import authenticate, login
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .forms import MyRegistrationForm, UserProfileForm, UpdateUserForm, ReviewForm

###################
# Some view functions will redirect users to index if they are not logged in
# In that case, next parameter will be appended with the redirect uri.
# This uri will be passed to a hidden input field in loginForm to be sent to the auth view function
###################
def index(request):
    if request.method == 'GET':
        args = {}
        args.update(csrf(request))
        args['user_form'] = MyRegistrationForm()
        args['profile_form'] = UserProfileForm()
        if (request.GET.get('next')):
            args['redirect'] = request.GET.get('next')
        if request.user.is_authenticated() and not request.user.is_superuser:
            profile = UserProfile.objects.filter(user=request.user).first()
            args['role'] = profile.role
        return render(request, 'index.html', args)

###################
# Uses custom query_set
# Retrieve parameter from URL using self.kwargs[paramname]
# filter accepts variable names separated by __
###################
class Category(generic.ListView):
    model = Place
    template_name = 'category.html'
    context_object_name = 'place_list'
    def get_queryset(self):
        self.query = self.kwargs['category']
        return Place.objects.filter(category_id__name__icontains=self.query)

    def get_context_data(self, **kwargs):
        ctx = super(Category, self).get_context_data(**kwargs)
        ctx['category'] =self.kwargs['category']
        return ctx

class AllCategories(generic.ListView):
    model = Place
    template_name = 'allCategories.html'
    context_object_name = 'place_list'

###################
# This view function is called when user submits the registration form
# Only if the form is valid the detail will be save to the database.
# Otherwise, index.html will be rendered with the forms (with error messages)
###################
def register_user(request):
    args = {}
    args.update(csrf(request))
    if (request.method == 'GET' or request.user.is_authenticated):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        user_form = MyRegistrationForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            profile = profile_form.save(commit = False)
            profile.user = new_user
            profile.save()
            args['successMessage'] = "You have successfully registered"
            user_form = MyRegistrationForm()
            profile_form = UserProfileForm()
    args['user_form'] = user_form
    args['profile_form'] = profile_form
    return render(request, 'index.html', args)

###################
# This view function is called when user submits the registration form
# Only if the form is valid the detail will be save to the database.
# Otherwise, index.html will be rendered with the forms (with error messages)
###################
def auth_view(request):
    if request.user.is_authenticated():
        return HttpResponseForbidden();

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    redirect = request.POST.get('redirectUri', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        if (redirect):
            return HttpResponseRedirect(redirect)
        return HttpResponseRedirect('/')
    else:
        user_form = MyRegistrationForm()
        profile_form = UserProfileForm()
        args = {}
        args.update(csrf(request))
        args['user_form'] = user_form
        args['profile_form'] = profile_form
        args['loginError'] = "Sorry, that's not a valid username or password"
        return render(request, 'index.html', args)

##########################
# This function is called when user requests /account/logout
##########################
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/')

##########################
# This function is called when use requests /search
# @method_decorator(login_required) will ensure that only logged in users can use this view class
# Otherwise the user will be redirected.
# get_context_data overrides the default method to add mroe context variables to be accessed in the template
##########################
class Search(generic.ListView):
    model = Place
    template_name = 'search.html'
    context_object_name = 'place_list'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Search, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.query = self.request.GET.get('q')
        return Place.objects.filter(name__icontains=self.query)
    def get_context_data(self, **kwargs):
        ctx = super(Search, self).get_context_data(**kwargs)
        ctx['pagination'] = self.paginate_by
        ctx['count'] = self.get_queryset().count()
        return ctx

##########################
# This view function is for an AJAX request from the search page to 
# Request the same search result but in different order. 
##########################
def search_ordered(request, **kwargs):
    if request.method == 'GET':
        query = request.GET.get('q')
        order = kwargs['order']
        if (order == 'alphabetically'):
            places = Place.objects.filter(name__icontains=query).order_by('name')
        else:
            places = Place.objects.filter(name__icontains=query)

        places_list = [];
        for place in places:
            places_list.append({"id":place.id, "name":place.name, "city": place.city_id.name, "address": place.address, "category": place.category_id.name})
        return JsonResponse({"result" : places_list});
    else :
        return JsonResponse({"error":"Cannot POST to this route"});
        # send error message


class PlaceDetail(generic.DetailView):
    model = Place
    template_name = 'placeDetail.html'
    context_object_name = 'place'
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaceDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(PlaceDetail, self).get_context_data(**kwargs)
        place = Place.objects.get(pk=self.kwargs['pk'])
        savedPlace = SavedPlace.objects.filter(user=self.request.user, place=place).first()
        if savedPlace:
            ctx['saved'] = True
        return ctx

class PlaceDetail(generic.DetailView):
    model = Place
    template_name = 'placeDetail.html'
    context_object_name = 'place'
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaceDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(PlaceDetail, self).get_context_data(**kwargs)
        place = Place.objects.get(pk=self.kwargs['pk'])
        savedPlace = SavedPlace.objects.filter(user=self.request.user, place=place).first()
        if savedPlace:
            ctx['saved'] = True
        return ctx

##########################
# This function handles all requests for reviews
##########################
@csrf_exempt
def reviews(request, **kwargs):
    if request.method == 'GET':
        place = Place.objects.get(pk=kwargs['pk'])
        reviews = Review.objects.filter(place_id=place)
        reviews_list = []
        for review in reviews:
            reviews_list.append({"name": review.user.username, "comment": review.comments, "rating": review.rating})
        return JsonResponse({"result" : reviews_list})
    if request.method == 'POST':
        comments = request.POST['comment']
        rating = request.POST['rating']
        place = Place.objects.get(pk=kwargs['pk'])
        review = Review.objects.filter(user=request.user, place_id=place).count()
        if review > 0:
            return HttpResponseForbidden()
        else:
            Review.objects.create(user=request.user, place_id=place,comments=comments, rating=rating)
            return JsonResponse({"name" : request.user.username, 'comment': comments, 'rating': rating})

##########################
# This function handles all requests for account information or updates
##########################
@csrf_exempt
def account(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        print(request.user.id)
        user_profile = UserProfile.objects.filter(user_id=kwargs['pk']).first()
        return render(request, 'AccountInformation.html', {"user_profile": user_profile})
    elif request.method == 'PUT':
        print(request.user.id)
        print(kwargs['pk'])
        data = json.loads(request.body)
        qdict = QueryDict('', mutable=True)
        qdict.update(data)
        form = UpdateUserForm(qdict, instance=request.user)
        if form.is_valid():
            user = request.user
            user.first_name = qdict['first_name']
            user.last_name = qdict['last_name']
            user.email = qdict['email']
            user.userprofile.phone_number = qdict['phone_number']
            user.userprofile.address = qdict['address']
            user.userprofile.postcode = qdict['postcode']
            user.userprofile.role = qdict['role']
            user.save()
            user.userprofile.save()
            return JsonResponse({
                "username": user.username,
                "first_name" : user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.userprofile.phone_number,
                "address": user.userprofile.address,
                "postcode": user.userprofile.postcode,
                "role": user.userprofile.role
                })
        else:
            return HttpResponseForbidden()   
    elif request.method == 'DELETE':
        auth.logout(request)
        user = User.objects.get(pk = kwargs['pk'])
        user.userprofile.delete()
        user.delete()
        return JsonResponse({"error": None, "result": 'success'})

##########################
# This function handles all requests for saved_places
##########################
@csrf_exempt
def saved_places(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        user_saved_places = SavedPlace.objects.filter(user=request.user)
        return render(request, 'saved_places.html', {"saved_places": user_saved_places})
    elif request.method == 'POST':
        place = Place.objects.get(pk=kwargs['pk'])
        savedPlace = SavedPlace.objects.filter(user=request.user, place=place).first()
        if savedPlace:
            return HttpResponseForbidden()
        else:
            SavedPlace.objects.create(place=place, user=request.user)
            return JsonResponse({"error": None, "result": 'success'})
    elif request.method == 'DELETE':
        place = Place.objects.get(pk=kwargs['pk'])
        savedPlace = SavedPlace.objects.filter(user=request.user, place=place).first()
        if not savedPlace:
            return HttpResponseForbidden()
        else:
            savedPlace.delete()
            return JsonResponse({"error": None, "result": 'success'})
    
def contact(request):
    args = {}
    return render(request, 'contact.html', args)
