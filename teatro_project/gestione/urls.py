from django.urls import path
from .views import *

app_name = "gestione"

urlpatterns = [
    path("", gestione_home, name="home"),
    path("listaspettacoli/", ShowListView.as_view(),name="show_list"),
    path("listaspettacoli/in_programma/", ShowScheduledView.as_view(),name="scheduled_show"),
    path("listaspettacoli/votazioni/", ShowScoredView.as_view(), name="scored_show"),
    path("ricerca/", search, name="find_show"),
    path("ricerca/<str:sstring>/<str:where>/", ShowFindView.as_view(), name="found_results"),


    path("prenota/<pk>/", make_booking, name="makebooking"),
    path("prenota/scegliposto/<pk>/", get_booking_seats, name="screeningseats"),

    path("prenotazioni/", my_bookings, name="my_bookings"),
    path("infospettacolo/<pk>/", ShowDetailView.as_view(), name="show_detail"),
    path("recensione/<pk>/", leave_review, name="leave_review"),
    path("mierecensioni/", MyReviewsView.as_view(), name="my_reviews"),
    path("eliminarec/<pk>/", delete_review, name ="delete_review"),
    path("eliminaprenot/<pk>/", deleteBooking, name="delete_booking"),

    path("crea_spettacolo/", CreateShowView.as_view(), name="create_show"),
    path("elimina_spettacolo/<pk>/", delete_show, name="delete_show"),
    path("elimina_spettacolo/", RemoveShowView.as_view(), name="remove_show"),
    path("prenotazionispettacolo/<pk>/", BookingsListView.as_view(),name="booking_list"),
    path("prenotazioniutenti/<pk>/", BookingsUsersListView.as_view(),name="user_booking_list"),
    path("prenotazionispettacoli/", all_bookings_list, name="all_bookings_list"),
]