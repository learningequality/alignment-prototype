from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.views import View
from rest_framework.authtoken.models import Token


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
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            return redirect('https://hackathon.learningequality.org')

    else:
        f = UserCreationForm()

    return render(request, 'register.html', {'form': f})
