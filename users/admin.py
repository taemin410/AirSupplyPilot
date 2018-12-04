from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.crypto import get_random_string
from authtools.admin import NamedUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .models import Clinic

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework.authtoken.models import Token

User = get_user_model()

class CustomUserAdmin(NamedUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['name', 'email', 'first_name', 'last_name', 'role', 'clinic']
    
    add_fieldsets = (
        (None, {
            'description': (
                "Enter the new user's role and email address and click save."
                " The user will be emailed a link allowing them to register to"
                " the site and set their password, username, lastname, firstname and if necessary clinic."
            ),
            'fields': ('email', 'role'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change and (not form.cleaned_data['password1'] or not obj.has_usable_password()):
            obj.set_password(get_random_string())
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)

        if reset_password:
            plaintext = get_template('signup_mail.txt')
            html = get_template('signup_mail.html')
            token = Token.objects.get(user=obj).key

            subject, from_email, to = 'Sign Up', 'ASP@HealthAutority.com', obj.email
            text_content = plaintext.render({'token': token})
            html_content = html.render({'token': token})
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Clinic)