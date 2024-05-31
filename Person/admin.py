from django.contrib import admin
from django.apps import apps
from .models import Person,PersonRelationship

class PersonAdmin(admin.ModelAdmin):
    search_fields = ['nepaliName', 'name', 'bookReferenceNumber']

class PersonRelationshipAdmin(admin.ModelAdmin):
    search_fields = ['primaryPerson__nepaliName', 'primaryPerson__name', 'secondaryPerson__nepaliName', 'secondaryPerson__name']
    autocomplete_fields = ['primaryPerson', 'secondaryPerson']

admin.site.register(Person, PersonAdmin)
admin.site.register(PersonRelationship, PersonRelationshipAdmin)


models=apps.get_models()

for model in models:
    if model is not Person:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass



