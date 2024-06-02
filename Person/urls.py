from django.urls import path
from Person.views import PersonCreateView,PersonUpdateView,PersonDetailView,PersonsListView,PersonDelete
from Person.views import SuggestionCreateView,SuggestionUpdateView,SuggestionDetailView,SuggestionsListView,SuggestionDelete
from Person.views import csvDataLoad,SearchView,family_tree,PersonAutocomplete

urlpatterns = [
    #Person
    path('',PersonsListView.as_view(),name="list_persons"),
    path('detail/person/<int:pk>',PersonDetailView,name="detail_person"),
    path('create/person',PersonCreateView.as_view(),name="create_person"),
    path('update/person/<int:pk>',PersonUpdateView.as_view(),name="update_person"),
    path('delete/person/<int:pk>/', PersonDelete, name='delete_person'),
    #Suggestion
    path('suggestions',SuggestionsListView.as_view(),name="list_suggestions"),
    path('suggestion/<int:pk>',SuggestionDetailView,name="detail_suggestion"),
    path('create/suggestion/<int:pk>',SuggestionCreateView.as_view(),name="create_suggestion"),
    path('update/suggestion/<int:pk>',SuggestionUpdateView.as_view(),name="update_suggestion"),
    path('delete/suggestion/<int:pk>/', SuggestionDelete, name='delete_suggestion'),
    #Utilities
    path('data/load',csvDataLoad, name="csv_dataLoad"),
    #Search
    path('search',SearchView.as_view(), name='search'),
    #Family Tree
    path('tree/person/<int:pk>', family_tree, name='family_tree'),

    path('person-autocomplete/', PersonAutocomplete.as_view(), name='person-autocomplete'),

    # Code to be checked from here before adding to production

]
