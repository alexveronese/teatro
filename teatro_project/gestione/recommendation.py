from cmath import sqrt

from .models import *


def get_user_shows(user: User):
    return Show.objects.filter(bookings__user=user)


def get_user_typev(user: User):
    s_watch = get_user_shows(user)
    types = ["Opera", "Concerto", "Danza", "Musical"]
    typev = {t: 0 for t in types}
    for s in s_watch:
        for t in types:
            if s.type == t:
                typev[t] += 1

    return typev


def get_nmost_similar(user: User, n=None):
    u_typev = get_user_typev(user)
    user_mag = 0
    # compute the magnitude of the user typev
    for t in u_typev:
        user_mag += u_typev[t] * u_typev[t]

    if user_mag == 0:
        return []

    user_mag_sqrt = sqrt(user_mag)

    # get all of the other user which have at least watched one movie
    other_users = list(User.objects.exclude(id=user.id))
    other_users = [u for u in other_users if len(Booking.objects.filter(user=u)) > 0]

    users_types = { u:get_user_typev(u) for u in other_users }
    # compute the cosine similarity
    res = [] # list of tuples (user, cos_similarity)
    for u in users_types:
        dot_prod = 0
        mag = 0
        tv = users_types[u]
        for t in tv:
            dot_prod += u_typev[t] * tv[t]
            mag += tv[t] * tv[t]
        res.append((u, dot_prod/(sqrt(mag)*user_mag_sqrt)))

    # sort by descending similarity
    res.sort(key=lambda ut: ut[1], reverse=True)
    if n != None:
        res = res[:n]
    return res


def get_recommended_movies(user: User, n):
    sim_us = get_nmost_similar(user, 20)
    us_movies = (get_user_shows(user))
    upcoming = Show.get_scheduled_shows()
    rec_dict = {}
    for u in sim_us:
        # upcoming movies seen by u and not by user
        shows = set(get_user_shows(u[0])).difference(us_movies).intersection(upcoming)
        for s in shows:
            if s in rec_dict:
                rec_dict[s] += u[1]
            else:
                rec_dict[s] = u[1]
        if len(rec_dict) >= n:
            break

    rec = [ (s, rec_dict[s]) for s in rec_dict ]
    rec.sort(key=lambda rm: rm[1], reverse=True)
    rec = [ r[0] for r in rec ]

    if len(rec) < n:
        # fill the result with the highest rated remaining movies
        all_movies = set(upcoming).difference(us_movies).difference(set(rec))
        fill_movies = sorted(list(all_movies), key=lambda m: m.get_score() if m.get_score() != None else 0 , reverse=True)[:n - len(rec)]
        rec += fill_movies
    return rec
