from typing import Any

from django.db.models import QuerySet

from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
import json

# pipenv install django-braces
from braces.views import GroupRequiredMixin

def gestione_home(request):
    return render(request,template_name="gestione/home.html")

class ShowListView(ListView):
    title = "Archivio:"
    model = Show
    template_name = "gestione/show_list.html"

    def get_queryset(self):
        return Show.objects.all().order_by("date")


def search(request):

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            sstring = form.cleaned_data.get("search_string")
            where = form.cleaned_data.get("search_where")
            return redirect("gestione:found_results", sstring, where)
    else:
        form = SearchForm()

    return render(request, template_name="gestione/ricerca.html", context={"form": form})


class ShowFindView(ShowListView):
    title = "La tua ricerca ha dato come risultato"

    def get_queryset(self):
        sstring = self.request.resolver_match.kwargs["sstring"]
        where = self.request.resolver_match.kwargs["where"]

        if "Titolo" in where:
            qq = self.model.objects.filter(title__icontains=sstring)
        elif "Tipo" in where:
            qq = self.model.objects.filter(type__icontains=sstring)
        else:
            qq = self.model.objects.filter(company__icontains=sstring)

        return qq


class ShowScheduledView(ListView):
    title = "Spettacoli in programma:"
    model = Show
    template_name = "gestione/show_list.html"

    def get_queryset(self):
        return Show.objects.filter(date__gte=timezone.now()).order_by("date")


class ShowScoredView(ListView):
    title = "Spettacoli più votati:"
    model = Show
    template_name = "gestione/show_list.html"

    def get_queryset(self):
        for s in Show.objects.filter(date__lt=datetime.today().date()):
            if s.get_score() == None:
                s.score = 0
            else:
                s.score = s.get_score()

            s.save()

        return Show.objects.filter(date__lt=datetime.today().date(), score__gt=0).order_by("-score")


class ShowDetailView(DetailView):
    model = Show
    template_name = "gestione/info_show.html"

    def get_show_score(self):
        return self.get_object().get_score()

    def can_user_review(self):
        if self.request.user.is_authenticated:
            return self.get_object().can_user_review(self.request.user.id)
        return False

    def can_user_book(self):
        if self.request.user.is_authenticated:
            return self.get_object().can_user_book(self.request.user.id)
        return False

    def user_made_review(self):
        if self.request.user.is_authenticated:
            return self.get_object().user_made_review(self.request.user.id)
        return False


class MyReviewsView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "gestione/my_reviews.html"

    def get_queryset(self) -> QuerySet[Any]:
        user = User.objects.filter(id=self.request.user.id)[0]
        return Review.objects.filter(user=user)


@login_required
def delete_review(request, pk):
    rev = get_object_or_404(Review, pk=pk)
    if rev.user != request.user:
        return redirect(reverse("gestione:my_reviews") + "?delete=err")
    rev.delete()
    return redirect(reverse("gestione:my_reviews") + "?delete=ok")


@login_required
def deleteBooking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    show = booking.show.pk
    if(is_manager(request.user) == False):
        if booking.user != request.user:
            return redirect(reverse("gestione:my_bookings") + "?delete=err")
    booking.show.remove_reservation(booking.id)
    booking.show.save()
    booking.delete()
    if(is_manager(request.user) == True):
        return redirect(reverse("gestione:all_bookings_list") + "?delete=ok")

    return redirect(reverse("gestione:my_bookings") + "?delete=ok")


@login_required
def my_bookings(request):
    user = get_object_or_404(User, pk=request.user.pk)
    ctx = {
        "upcoming_book" : user.bookings.filter(show__date__gte=timezone.now()).order_by('show__date'),
        "old_book" : user.bookings.filter(show__date__lt=timezone.now()).order_by('-show__date'),
        "num_bookings" : user.bookings.count() > 0
    }
    return render(request, template_name="gestione/my_bookings.html", context=ctx)


@login_required
def leave_review(request, pk):
    show = get_object_or_404(Show, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            score = form.cleaned_data.get("score")
            text = form.cleaned_data.get("text")
            r = Review()
            r.show = show
            r.user = request.user
            r.score = score
            r.text = text
            r.save()
            return redirect("gestione:show_detail", pk)

    form = ReviewForm()
    return render(request, template_name="gestione/leave_review.html", context={"show":show, "form": form})


#view per prenotazione posti
@login_required
def make_booking(request, pk):
    s = get_object_or_404(Show, pk=pk)
    if s.date < datetime.today().date():
        return HttpResponseNotFound("")
    if request.method == "POST":
        ress = Booking.objects.filter(user=request.user,show=s)
        if len(ress) > 0:
            r = ress[0]
            s = r.show
            s.remove_reservation(r.id)
            r.seats = []
        else:
            r = Booking()
            r.user = request.user
            r.show = s
            r.save()

        resp = json.loads(request.body)
        try:
            print("prova a salvare")
            for seat in resp["reserving_seats"]:
                print("try")
                r.set_seat_from_idx(int(seat))
            r.save()
            s.save()
        except Exception as e:
            print(e)
            r.delete()
            print("errore")
            return HttpResponse(reverse("gestione:my_bookings") + "?makeres=err")
        return HttpResponse(reverse("gestione:my_bookings") + "?makeres=ok")
    return render(request, template_name="gestione/make_booking.html", context={"show": s})


@login_required
def get_booking_seats(request, pk):
    s = get_object_or_404(Show, pk=pk)
    user = request.user
    r = Booking.objects.filter(user=user, show=s)
    # print(f"requesting seats of {pk}")
    info = {
        "seats": s.seats,
        "rows": s.seat_rows,
        "palco_rows" : s.seat_palco_rows,
        "cols": s.seat_cols
    }
    if len(r) > 0:
        info["res_id"] = r[0].id
    return HttpResponse(json.dumps(info))


# views per solo Operatori
class CreateShowView(GroupRequiredMixin, CreateView):
    group_required = ["Operatori"]
    title = "Aggiungi uno spettacolo"
    form_class = CreateShowForm
    template_name = "gestione/create_entry.html"
    success_url = reverse_lazy("gestione:home")

class RemoveShowView(GroupRequiredMixin, ShowListView):
    group_required = ["Operatori"]
    title = "Elimina Spettacolo"
    header = title

def is_manager(user):
    ret = user.groups.filter(name="Operatori").exists() or user.is_staff
    return ret

@user_passes_test(is_manager)
def delete_show(request, pk):
    show = get_object_or_404(Show, pk=pk)
    show.delete()
    return redirect(reverse("gestione:remove_show") + "?delete=ok")

class BookingsListView(GroupRequiredMixin, ListView):
    group_required = ["Operatori"]
    model = Booking
    title = "Prenotazioni"
    template_name = "gestione/booking_list.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["show_title"] = get_object_or_404(Show, pk=self.kwargs.get("pk")).title
        return ctx

    def get_queryset(self):
        show = get_object_or_404(Show, pk=self.kwargs.get("pk"))
        return show.bookings.filter(show__id=show.id).order_by("-show__date")


class BookingsUsersListView(GroupRequiredMixin, ListView):
    group_required = ["Operatori"]
    model = Booking
    template_name = "gestione/user_booking_list.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["user_name"] = get_object_or_404(User, pk=self.kwargs.get("pk")).username
        return ctx

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get("pk"))
        return user.bookings.all()

@user_passes_test(is_manager)
def all_bookings_list(request):
    ctx = {
        "upcoming_shows" : Show.objects.all().filter(date__gte=timezone.now()).order_by('date'),
        "old_shows" : Show.objects.all().filter(date__lt=timezone.now()).order_by('-date'),
        "num_bookings" : Booking.objects.all().count() > 0
    }
    return render(request, template_name="gestione/all_bookings.html", context=ctx)














