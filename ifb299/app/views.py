from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import MyRegistrationForm, UserProfileForm


from .models import Place

class HttpResponseUnauthorized(HttpResponseRedirect):
    status_code = 401

class HttpResponseNotFound(HttpResponseRedirect):
    status_code = 404

def index(request):
    if request.method == 'GET':
        args = {}
        args.update(csrf(request))
        args['user_form'] = MyRegistrationForm()
        args['profile_form'] = UserProfileForm()
        return render(request, 'index.html', args)

def register_user(request):

    if request.method == 'POST':
        user_form = MyRegistrationForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)
        print('i received request')
        if user_form.is_valid() and profile_form.is_valid():
            print('form was valid');
            new_user = user_form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            profile = profile_form.save(commit = False)
            profile.user = new_user
            profile.save()
            return HttpResponseRedirect('/account/register_success')
    args = {}
    args.update(csrf(request))
    args['user_form'] = user_form
    args['profile_form'] = profile_form
    return render(request, 'index.html', args)


def register_success(request):
    if request.user.is_authenticated():
        return HttpResponseNotFound('/')
    return render(request, 'register_success.html')


def auth_view(request):
    if request.user.is_authenticated():
        return HttpResponseNotFound('/')
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/account/invalid')

def invalidLogin(request):
    if request.user.is_authenticated():
        return HttpResponseNotFound('/')
    return render(request, 'invalidLogin.html')

def logout(request):
    if not request.user.is_authenticated():
        return HttpResponseNotFound('/')
    auth.logout(request)
    return render(request, 'logout.html')

def search_ordered(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        # places = Place.objects.filter(name_icontains=query).order_by()

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

class PlaceDetail(generic.DetailView):
    model = Place
    template_name = 'placeDetail.html'
    context_object_name = 'place'
    
class AccountInformation(generic.ListView):
    model = UserProfile
    template_name = 'AccountInformation.html'
    context_object_name = 'users'
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
class EditAccountInformation(generic.ListView):
    model = UserProfile
    template_name = 'EditAccount.html'
    context_object_name = 'users'
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
