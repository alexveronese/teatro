from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from gestione.models import *
from gestione.recommendation import get_recommended_movies
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

HOMEPAGE_MAX_MOVIES = 5
def teatro_home(request):
    shows = Show.get_scheduled_shows()
    ctx = {
        "shows": shows[:HOMEPAGE_MAX_MOVIES],
        "see_more": len(shows) > HOMEPAGE_MAX_MOVIES,
        "recommended": None
    }
    if request.user.is_authenticated:
        rec = get_recommended_movies(request.user, HOMEPAGE_MAX_MOVIES)
        ctx["recommended"] = rec if len(rec) > 0 else None

    return render(request, template_name="home.html", context=ctx)

class UserCreateView(CreateView):
    form_class = CreaUtenteSpettatore
    template_name = "user_create.html"
    success_url = reverse_lazy("login")

class OperatoreCreateView(PermissionRequiredMixin, UserCreateView):
    permission_required = "is_staff"
    form_class = CreaUtenteOperatore