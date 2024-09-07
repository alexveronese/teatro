from datetime import datetime, timezone

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Show(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    company = models.CharField(max_length=100)
    date = models.DateField(default=None, null=True, blank=True)
    hour = models.TimeField(default="21:00", null=True, blank=True)
    cover = models.ImageField(upload_to="gestione/covers", default="gestione/covers/default.png")
    seats = models.JSONField(default=dict)
    seat_rows = models.IntegerField(default=15, validators=[
        MinValueValidator(1),
        MaxValueValidator(26),
    ])
    seat_cols = models.IntegerField(default=20, validators=[
        MinValueValidator(1)
    ])

    seat_palco_rows = models.IntegerField(default=5, validators=[
        MinValueValidator(1),
        MaxValueValidator(26),
    ])

    score = models.IntegerField(default=0)

    def clean(self):
        super().clean()


    def init_seats(self):
        rows = self.seat_rows
        cols = self.seat_cols
        p_rows = self.seat_palco_rows
        s = {}
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for r in range(0, rows + p_rows):
            s[letters[r]] = [None] * cols
        self.seats = s


    def get_seat_reserv(self, row, col, convert_col=False):
        if convert_col:
            col -= 1

        if self.seats.get(row) == None or col < 0 or col >= self.seat_cols:
            raise Exception("Illegal argument in get_seat_reserv(), got row=" + str(self.seat_rows) + " col=" + str(self.seat_cols))

        return self.seats.get(row)[col]

    def set_reservation(self, row, start_col, seats_number, res_id, convert_col=False):
        if convert_col:
            start_col -= 1

        for c in range(start_col, start_col + seats_number):
            if self.get_seat_reserv(row, c, False) != None:
                raise Exception(f"Tried reserving already occupied seats {row} {c}!")

        r = self.seats.get(row)
        for c in range(start_col, start_col + seats_number):
            r[c] = res_id
        self.seats[row] = r

    def remove_reservation(self, res_id):
        for r in self.seats:
            row = self.seats.get(r)
            row = [None if e == res_id else e for e in row]
            self.seats[r] = row


    def get_free_seats(self):
        free = 0
        for r in self.seats:
            row = self.seats[r]
            for s in row:
                if s == None: free += 1
        return free



    def scheduled(self):
        if self.date > datetime.today().date():
            return True
        return False

    def bookable(self):
        if self.get_free_seats() == 0:
            return False
        return True

    def get_score(self):
        revs = self.reviews.all()
        n = len(revs)
        if n == 0: return None
        s = 0
        for r in revs:
            s += r.score
        return s/n

    def can_user_review(self, user_id):
        if len(Review.objects.filter(user__id=user_id, show=self)) > 0:
            return False

        ress = Booking.objects.filter(show=self, user__id=user_id).order_by("-show__date")
        if len(ress) == 0:
            return False

        if ress[0].show.date > datetime.today().date():
            return False

        return True

    def user_made_review(self, user_id):
        ress = Review.objects.filter(show=self, user__id=user_id)
        if len(ress) == 0:
            return False

        return True

    def can_user_book(self, user_id):
        if len(Booking.objects.filter(user__id=user_id, show=self)) > 0:
            return False

        return True


    def get_scheduled_shows():
        upcoming = Show.objects.filter(date__gte=datetime.today().date()).order_by("date")
        return upcoming

class Booking(models.Model):
    show = models.ForeignKey(Show,on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, default=None, related_name='bookings')
    seats = models.JSONField(default=list)

    def set_seats(self, row, start_col, seats_number):
        self.show.set_reservation(row, start_col, seats_number, self.id)
        self.show.save()
        for c in range(start_col, start_col + seats_number):
            self.seats.append((row, c))

    def set_seat_from_idx(self, idx):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        row = letters[idx // self.show.seat_cols]
        col = (idx % self.show.seat_cols)

        self.show.set_reservation(row, col, 1, self.id)
        print("here")
        self.seats.append((row, col))

    def get_seats(self):
        retval = ""
        l = sorted(self.seats)
        for s in l:
            retval += str(s[0]) + str(s[1] + 1) + ", "
        return retval[:-2]

    def user_has_reviewed(self):
        return len(self.user.reviews.filter(show=self.show)) > 0

    def __str__(self):
        return str(self.show) + " reserved by " + str(self.user)

    class Meta:
        unique_together = (('show', 'user'))

class Review(models.Model):
    text = models.CharField(default="",max_length=250)
    score = models.PositiveIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    show = models.ForeignKey(Show,on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='reviews')


    def __str__(self):
        return self.user.username + " gave " + self.show.title + " a " + str(self.score) + "/10"

    class Meta:
        unique_together = (('show', 'user'))
