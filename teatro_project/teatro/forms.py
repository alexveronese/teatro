from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

class CreaUtenteSpettatore(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Spettatori")
        g.user_set.add(user)
        return user

class CreaUtenteOperatore(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Operatori")
        g.user_set.add(user)
        return user