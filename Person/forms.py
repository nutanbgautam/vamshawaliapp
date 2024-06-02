from django.forms import inlineformset_factory
from dal import autocomplete
from django import forms
from .models import Person, PersonRelationship

class PersonRelationshipForm(forms.ModelForm):
    primaryPerson = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=autocomplete.ModelSelect2(url='person-autocomplete', attrs={'class': 'form-control'}),
        label=''
    )
    secondaryPerson = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=autocomplete.ModelSelect2(url='person-autocomplete', attrs={'class': 'form-control'}),
        label='Person'
    )
    relation = forms.ChoiceField(
        choices=PersonRelationship.RELATIONSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Person is your '
    )

    class Meta:
        model = PersonRelationship
        fields = ['primaryPerson', 'secondaryPerson', 'relation']

PersonRelationshipFormSet = inlineformset_factory(
    Person,
    PersonRelationship,
    form=PersonRelationshipForm,
    extra=1,
    can_delete=True,
    fk_name='primaryPerson'
)

# Code to be checked from here before adding to production

