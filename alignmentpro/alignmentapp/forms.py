from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from alignmentapp.models import BACKGROUNDS, SubjectArea, UserProfile


class UserProfileForm(ModelForm):
    # background = forms.ChoiceField(choices=BACKGROUNDS)
    subject_areas = forms.ModelMultipleChoiceField(queryset=SubjectArea.objects.all(), widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = UserProfile
        fields = ('background', 'subject_areas')
        labels = {
            'subject_areas': 'Subject Areas'
        }