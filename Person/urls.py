from django.urls import path
from Person.views import PersonCreateView,PersonUpdateView,PersonDetailView,PersonsListView,delete_person
from Person.views import SuggestionCreateView,SuggestionUpdateView,SuggestionDetailView,SuggestionsListView,delete_suggestion
from Person.views import csvDataLoad,SearchView,family_tree

urlpatterns = [
    #Person
    path('',PersonsListView.as_view(),name="list_persons"),
    path('detail/person/<int:pk>',PersonDetailView,name="detail_person"),
    path('create/person',PersonCreateView.as_view(),name="create_person"),
    path('update/person/<int:pk>',PersonUpdateView.as_view(),name="update_person"),
    path('delete/person/<int:pk>/', delete_person, name='delete_person'),
    #Suggestion
    path('suggestions',SuggestionsListView.as_view(),name="list_suggestions"),
    path('suggestion/<int:pk>',SuggestionDetailView,name="detail_suggestion"),
    path('create/suggestion/<int:personid>',SuggestionCreateView.as_view(),name="create_suggestion"),
    path('update/suggestion/<int:pk>',SuggestionUpdateView.as_view(),name="update_suggestion"),
    path('delete/suggestion/<int:pk>/', delete_suggestion, name='delete_suggestion'),

    path('data/load',csvDataLoad, name="csv_dataLoad"),

    path('search',SearchView.as_view(), name='search'),

    path('tree/person/<int:pk>', family_tree, name='family_tree'),
    
    # Code to be checked from here before adding to production
    


]
