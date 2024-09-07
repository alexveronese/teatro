from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from .models import *
from django.urls import reverse
from django.contrib.auth.models import Group

# Create your tests here.
class ShowScheduledViewTest(TestCase):
    def test_no_scheduled_shows(self):
        """
        Se non ci sono spettacoli in programma, la pagina show_list dovrebbe visualizzare "Nessuno spettacolo al momento"
        """
        response = self.client.get(reverse("gestione:scheduled_show"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nessuno spettacolo al momento")
        self.assertQuerySetEqual(response.context["object_list"], [])

    def test_scheduled_shows(self):
        """
        show_list dovrebbe mostrare gli spettacoli in ordine di data
        """
        s1 = Show(title="s1", date=datetime.today().date() + timedelta(2))
        s2 = Show(title="s2", date=datetime.today().date() + timedelta(1))
        s3 = Show(title="s3", date=datetime.today().date() + timedelta(3))
        s4 = Show(title="s4", date=datetime.today().date() - timedelta(1))
        s1.save()
        s2.save()
        s3.save()
        s4.save()

        response = self.client.get(reverse("gestione:scheduled_show"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Nessuno spettacolo al momento")
        self.assertQuerySetEqual(response.context["object_list"], [s2, s1, s3])

class OperatorTest(TestCase):
    def test_not_operator(self):
        """
        Utenti che non rientrano nel gruppo "Operatori" non dovrebbero avere accesso alla pagina all_bookings
        in cui vi è il riepilogo di tutte le prenotazioni degli utenti per ogni spettacolo
        """
        response = self.client.get(reverse("gestione:all_bookings_list"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?auth=notok&next=/gestione/prenotazionispettacoli/")

        u = User.objects.create_user(username="u1", password="samplepw1!")
        u.save()
        g = Group(name="Spettatori")
        g.save()
        g.user_set.add(u)
        self.client.login(username="u1", password="samplepw1!")
        response = self.client.get(reverse("gestione:all_bookings_list"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?auth=notok&next=/gestione/prenotazionispettacoli/")


    def test_is_operator(self):
        """
        "Operatori" e "Admin" dovrebbero avere accesso alla pagina all_bookings
        """
        m = User.objects.create_user(username="m1", password="samplepw1!")
        m.save()
        g = Group(name="Operatori")
        g.save()
        g.user_set.add(m)
        self.client.login(username="m1", password="samplepw1!")
        response = self.client.get(reverse("gestione:all_bookings_list"))
        self.assertEqual(response.status_code, 200)

        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse("gestione:all_bookings_list"))
        self.assertEqual(response.status_code, 200)



class ShowSeatsTests(TestCase):
    def test_init_seats(self):
        """
        All of the seats of a booking are correctly initialized to None (free)
        """
        s = Show()
        s.seat_rows = 5
        s.seat_palco_rows = 5
        s.seat_cols = 10
        s.init_seats()
        seats = {
            "A": [None] * 10,
            "B": [None] * 10,
            "C": [None] * 10,
            "D": [None] * 10,
            "E": [None] * 10,
            "F": [None] * 10,
            "G": [None] * 10,
            "H": [None] * 10,
            "I": [None] * 10,
            "J": [None] * 10
        }
        self.assertEqual(s.seats, seats)

    def test_set_reservation(self):
        """
        Bookings can only be made on free and existing seats
        """
        s = Show()
        s.seat_rows = 5
        s.seat_palco_rows = 5
        s.seat_cols = 10
        s.init_seats()

        s.set_reservation("A", 0, 2, 1)
        seats = {
            "A": [1, 1, None, None, None, None, None, None, None, None],
            "B": [None] * 10,
            "C": [None] * 10,
            "D": [None] * 10,
            "E": [None] * 10,
            "F": [None] * 10,
            "G": [None] * 10,
            "H": [None] * 10,
            "I": [None] * 10,
            "J": [None] * 10
        }
        self.assertEqual(s.seats, seats)
        self.assertRaises(Exception, s.set_reservation, "L", 0, 1, 2)
        self.assertRaises(Exception, s.set_reservation, "A", 1, 2, 3)
        self.assertRaises(Exception, s.set_reservation, "B", 2, 15, 4)
        s.set_reservation("B", 3, 1, 5)
        seats["B"] = [None, None, None, 5, None, None, None, None, None, None]
        self.assertEqual(s.seats, seats)

    def test_remove_reservation(self):
        """
        Removing a booking only frees the seats of said booking
        """
        s = Show()
        s.seat_rows = 5
        s.seat_palco_rows = 5
        s.seat_cols = 10
        s.init_seats()
        s.set_reservation("A", 0, 2, 1)
        s.set_reservation("B", 3, 1, 2)
        s.remove_reservation(1)
        seats = {
            "A": [None] * 10,
            "B": [None, None, None, 2, None, None, None, None, None, None],
            "C": [None] * 10,
            "D": [None] * 10,
            "E": [None] * 10,
            "F": [None] * 10,
            "G": [None] * 10,
            "H": [None] * 10,
            "I": [None] * 10,
            "J": [None] * 10
        }
        self.assertEqual(s.seats, seats)

    def test_get_free_seats(self):
        """
        Number of free seats is correctly calculated and it gets lower when new reservations are made
        """
        s = Show()
        s.seat_rows = 5
        s.seat_palco_rows = 5
        s.seat_cols = 10
        s.init_seats()
        self.assertEqual(s.get_free_seats(), 10*10)
        s.set_reservation("A", 0, 2, 1)
        self.assertEqual(s.get_free_seats(), 10*10 - 2)
        s.set_reservation("B", 3, 1, 2)
        self.assertEqual(s.get_free_seats(), 10*10 - 2 - 1)