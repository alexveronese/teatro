from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import NumberInput

from .models import *

class CreateShowForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "addshow_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit","Aggiungi Spettacolo"))


    class Meta:
        CHOICES = {"Opera": "Opera", "Concerto": "Concerto", "Danza": "Danza", "Musical": "Musical"}
        model = Show
        fields = ["title","type","company", "date", "hour", "cover"]
        widgets = {
            "type": forms.Select(choices=CHOICES),
            "date" : forms.SelectDateWidget(),
            "hour" : forms.TimeInput()
        }

    def save(self, commit=True):
        s = super().save(commit)
        s.init_seats()
        if commit:
            s.save()
        return s



class SearchForm(forms.Form):

    CHOICE_LIST = [("Titolo","Cerca tra i titoli"), ("Tipo","Cerca tra le tipologie"), ("Compagnia Teatrale","Cerca tra le compagnie teatrali")]
    helper = FormHelper()
    helper.form_id = "search_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit","Cerca"))
    search_where = forms.ChoiceField(label="Dove?", required=True, choices=CHOICE_LIST)
    search_string = forms.CharField(label="Cerca qualcosa",max_length=100, min_length=3, required=True)


class ReviewForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "review_crispy_form"
    helper.form_method = "POST"
    score = forms.IntegerField(label="Score", max_value=5, min_value=0)
    text = forms.CharField(label="Text", widget=forms.Textarea, max_length=300)
    helper.add_input(Submit("submit", "Lascia una recensione!"))

    class Meta:
        model = Review
        fields = ["score", "text"]