from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.views import View
from rest_framework.authtoken.models import Token

from .forms import UserProfileForm


class HomeView(View):

    def get(self, request, *args, **kwargs):
        token_str = ''
        try:
            if request.user.is_authenticated:
                token, _created = Token.objects.get_or_create(user=request.user)
                token_str = token.key
        except Token.DoesNotExist:
            pass

        return render(request, 'home.html', {'token': token_str})


def register(request):
    if request.method == 'POST':
        uc_form = UserCreationForm(request.POST)
        up_form = UserProfileForm(request.POST)
        if uc_form.is_valid() and up_form.is_valid():
            user = uc_form.save()
            user_profile = up_form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            return redirect('https://hackathon.learningequality.org')

    else:
        uc_form = UserCreationForm()
        up_form = UserProfileForm()

    return render(request, 'register.html', {'registration_form': uc_form, 'survey_form': up_form})
