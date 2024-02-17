from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class LoginForm(forms.Form):    
    username = forms.CharField(label="Enter first name",max_length=50)  
    password  = forms.CharField(label="Enter last name", max_length = 50)  

class CodeForm(forms.Form):
    language = forms.CharField()
    code = forms.CharField(widget=forms.Textarea())


#class CodeSubmissionForm(forms.Form):
    
