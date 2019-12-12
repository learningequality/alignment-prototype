##################################################
# MIT License
#
# Copyright (c) 2019 Learning Equality
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
##################################################

from django.conf import settings
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

        return render(request, 'home.html', {'token': token_str, 'admin': request.user.is_superuser})


def register(request):
    if request.method == 'POST':
        uc_form = UserCreationForm(request.POST)
        up_form = UserProfileForm(request.POST)
        if uc_form.is_valid() and up_form.is_valid():
            user = uc_form.save()
            user_profile = up_form.save(commit=False)

            # Because the user hasn't signed in, we need to manually add the user
            # to the UserProfile object.
            user_profile.user = user
            user_profile.save()

            # Needed to commit the save above to have the UserProfile created
            # before updating subject_areas, so one more save needed...
            for area in up_form.cleaned_data['subject_areas']:
                user_profile.subject_areas.add(area)
            user_profile.save()
            return redirect('/')

    else:
        uc_form = UserCreationForm()
        up_form = UserProfileForm()

    return render(request, 'register.html', {'registration_form': uc_form, 'survey_form': up_form})
