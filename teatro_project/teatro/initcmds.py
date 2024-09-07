from gestione.models import *
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
import copy
import random
from django.contrib.auth.models import Group, Permission

def erase_db():
    print("Cancello il DB")
    Show.objects.all().delete()
    Booking.objects.all().delete()
    Review.objects.all().delete()
    User.objects.all().delete()
    print("DB vuoto")


def init_db():
    if len(Show.objects.all()) != 0:
        return

    titles = {}
    companies = {}
    types = ["Opera", "Danza", "Concerto", "Musical"]

    for i in range(1, 11):
        titles[i] = "Spettacolo" + str(i)
        companies[i] = "Compagnia" + str(i)

    for i in range(1, 11):
        s = Show()
        s.title = titles[i]
        s.company = companies[i]
        s.type = types[random.randint(0, len(types)-1)]
        s.date = datetime.today().date() + timedelta(random.randint(1, 365))
        s.init_seats()
        s.save()

    """
    I have created 10 scheduled shows. Now I can create Users
    """

    if len(User.objects.all()) <= 1:
        print("Creando gli Spettatori")
        for i in range(1, 5):
            u = User.objects.create_user(username="user" + str(i), password="samplepw1!")
            g = Group.objects.get(name="Spettatori")
            g.user_set.add(u)
            print("Creato user" + str(i) + " che si chiama:  " + u.username)
            u.save()

        print("Creando l'utente Operatore")
        m = User.objects.create_user(username="Operatore1", password="samplepw1!")
        g = Group.objects.get(name="Operatori")
        g.user_set.add(m)


    """
    Now I can add Bookings to Shows
    """

    bookings = {
        "user1": {"row": "A", "start": 3, "count": 2},
        "user2": {"row": "C", "start": 0, "count": 3},
    }



    for sr in bookings:
        mvs = set(Show.objects.filter(title__contains="1") |
                  Show.objects.filter(title__contains="2") |
                  Show.objects.filter(title__contains="3") |
                  Show.objects.filter(title__contains="4") |
                  Show.objects.filter(title__contains="5"))
        for m in mvs:
            r = Booking()
            r.user = User.objects.filter(username__exact=sr)[0]
            r.show = m
            r.save()
            r.set_seats(bookings[sr]["row"], bookings[sr]["start"], bookings[sr]["count"])
            r.save()


    """
    I change the date field on last three shows for letting the users leaving a review
    """
    last_shows = set(Show.objects.filter(title__contains="4") |
                     Show.objects.filter(title__contains="5"))
    for ls in last_shows:
        ls.date = datetime.today().date() - timedelta(random.randint(365, 700))
        ls.save()

    for u in User.objects.all():
        mvs = []

        for s in Show.objects.all():
            if s.can_user_review(u.id):
                mvs.append(s)

        t = "Ti consiglio di andare a vedere questo spettacolo in futuro!"
        for s in mvs:
            r = Review()
            r.user = u
            r.show = s
            score = random.randint(1, 5)
            r.score = score
            r.text = t
            r.save()
            s.score = s.get_score()
            s.save()

    print("Inizializzazione DB completata")


def init_groups():
    spettatori = Group.objects.get_or_create(name="Spettatori")
    spettatori_perms = ["add_booking", "change_booking", "delete_booking",
                            "add_review", "delete_review"]
    for p in spettatori_perms:
        spettatori[0].permissions.add(Permission.objects.get(codename=p))

    operatori = Group.objects.get_or_create(name="Operatori")
    operatori_perms = ["add_booking", "change_booking", "delete_booking",
                            "add_review", "delete_review",
                            "add_show", "delete_show"]
    for p in operatori_perms:
        operatori[0].permissions.add(Permission.objects.get(codename=p))


print("DUMP DB")