from django import forms
from authtools.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from .models import Clinic

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('name', 'email', 'first_name', 'last_name', 'clinic')
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password')
        
class CustomUserSignUpForm(UserChangeForm):
    
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('name', 'email', 'first_name', 'last_name', 'role', 'clinic', 'password')
    
    def __init__(self, *args, **kwargs):
        super(CustomUserSignUpForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['role'].disabled = True
        if 'clinic' in self.fields.keys():
            self.fields['clinic'].queryset = Clinic.objects.all()
            self.fields['clinic'].help_text = 'Only change this value if you are a Clinic Manager.'
            self.fields['clinic'].required = False
        
class TokenForm(forms.Form):
    token = forms.CharField(max_length=50, required=True)