from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.db.transaction import commit
from django.template.defaulttags import comment

from .models import UserAccount


########### User Registration Form ##########
class userRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        out_user = super().save(commit=False)
        if commit == True:
            out_user.save()
            UserAccount.objects.create(user=out_user)
        return out_user


########### User Update Form ##########
class userUpdateForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']