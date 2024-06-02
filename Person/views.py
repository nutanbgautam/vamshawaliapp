from django.shortcuts import get_object_or_404, redirect,render
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from Person.models import Person,Suggestion,ContactDetail,PersonRelationship
from django.urls import reverse,reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Person
from dal import autocomplete
from .forms import PersonRelationshipFormSet
import re

#HTML Templates
person_create_template          = 'Person/create_person.html'
persons_list_template           = 'Person/list_persons.html'
person_detail_template          = 'Person/detail_person.html'
suggestion_create_template      = 'Suggestion/create_suggestion.html'
suggestions_list_template       = 'Suggestion/list_suggestions.html'
suggestion_detail_tempalte      = 'Suggestion/detail_suggestion.html'
family_tree_template            = 'family_tree.html'
search_form_template            = 'search_form.html'

#Person CURD
class PersonsListView(ListView):
    model               = Person
    queryset            = Person.objects.all()
    template_name       = persons_list_template
    context_object_name = 'persons'
    ordering            = ['id']
    paginate_by         = 50 

class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    fields = ['name', 'nepaliName', 'gender', 'photo', 'birth', 'death', 'pustaNumber', 'aliveOrDead', 'bookReferenceNumber', 'remarks']
    template_name = 'Person/create_person.html'
    success_url = reverse_lazy('list_persons')

    def get_form(self, form_class=None):
        form = super(PersonCreateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class': 'form-control'})
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['relationships'] = PersonRelationshipFormSet(self.request.POST)
        else:
            data['relationships'] = PersonRelationshipFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        relationships = context['relationships']
        if relationships.is_valid():
            self.object = form.save()
            relationships.instance = self.object
            relationships.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q) | qs.filter(nepaliName__icontains=self.q) | qs.filter(bookReferenceNumber__icontains=self.q)

        return qs

class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    fields = ['name', 'nepaliName', 'gender', 'photo', 'birth', 'death', 'pustaNumber', 'aliveOrDead', 'bookReferenceNumber', 'remarks', 'address', 'cityOrCountry', 'contactDetails', 'emailAddress']
    template_name = 'Person/update_person.html'
    success_url = reverse_lazy('list_persons')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['relationships'] = PersonRelationshipFormSet(self.request.POST, instance=self.object)
        else:
            data['relationships'] = PersonRelationshipFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        relationships = context['relationships']
        if relationships.is_valid():
            self.object = form.save()
            relationships.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

def PersonDetailView(request,pk):
    person = get_object_or_404(Person, pk=pk)
    contactDetails = ContactDetail.objects.filter(primaryPerson=person)
    relationshipsA = list(PersonRelationship.objects.filter(primaryPerson=person))
    relationshipsB = list(PersonRelationship.objects.filter(secondaryPerson=person))
    relationshipsA.extend(relationshipsB)
    return render(request,person_detail_template,{"person":person,"contactDetails":contactDetails,"relationships":relationshipsA})

def PersonDelete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    person.delete()
    return redirect(reverse('list_persons')) 

#Suggestion

class SuggestionsListView(LoginRequiredMixin,ListView):
    model               = Suggestion
    queryset            = Suggestion.objects.all()
    template_name       = suggestions_list_template
    context_object_name = 'suggestions'
    ordering            = ['id']
    paginate_by         = 20 

class SuggestionCreateView(CreateView):
    model               = Suggestion
    fields              = ['primaryPerson', 'suggestion','photo', 'suggestorName','suggestorContactOption','suggestorContactDetail']
    template_name       = suggestion_create_template
    success_url         = reverse_lazy('list_persons')

    def get_initial(self):
        initial = super().get_initial()
        person_id = self.kwargs.get('pk')
        if person_id:
            person = get_object_or_404(Person, pk=person_id)
            initial['primaryPerson'] = person
        return initial

    def get_form(self, form_class=None):
        form = super(SuggestionCreateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class' : 'form-control'})
        return form
    
class SuggestionUpdateView(LoginRequiredMixin,UpdateView): 
    model               = Suggestion 
    fields              = ['primaryPerson', 'suggestion','photo', 'suggestorName','suggestorContactOption','suggestorContactDetail']
    success_url         = reverse_lazy('list_suggestions')

    def get_form(self, form_class=None):
        form = super(SuggestionUpdateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class' : 'form-control'})
        return form

def SuggestionDetailView(request,pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    return render(request,suggestion_detail_tempalte,{"suggestion":suggestion})

def SuggestionDelete(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    suggestion.delete()
    return redirect(reverse('list_suggestions')) 

#Search Functionality

class SearchView(View):
    def get(self, request, *args, **kwargs):
        return render(request, search_form_template)
    

    def post(self, request, *args, **kwargs):
        person_filters = {}
        person_filters['pustaNumber'] = request.POST.get('personPustaNumber')
        person_filters['bookReferenceNumber'] = request.POST.get('personBookReferenceNumber')
        person_filters['contactDetails__icontains'] = request.POST.get('personContactDetail')
        person_filters['id'] = request.POST.get('personId')

        is_gautam_vamsha = request.POST.get('isGautamVamsha')

        persons = Person.objects.all()

        def is_romanized_nepali(text):
            # Common Romanized Nepali patterns/characters
            romanized_nepali_patterns = re.compile(r'[अ-ह]')
            return bool(romanized_nepali_patterns.search(text))
        
        if request.POST.get('personName') is not None:
            if is_romanized_nepali(request.POST.get('personName')):
                person_filters['nepaliName__icontains'] = request.POST.get('personName')
            else:
                person_filters['name__icontains'] = request.POST.get('personName')


        for key, value in person_filters.items():
            print(f"Key = {key}, Value = {value}")
            if value is not None and value != "":
                if key == 'pustaNumber' or key == 'id':
                    persons = persons.filter(**{key: int(value)})
                else:
                    persons = persons.filter(**{key: value})

        if is_gautam_vamsha == "on":
            persons = persons.filter(personId__gt=0)

        found_persons = list(persons)

        return render(request, persons_list_template, {'persons': found_persons})

#Utility Functions

def csvDataLoad(request):
    from .utility_functions import csv_data_load
    return redirect(reverse('list_persons'))

#Family Tree

def build_descendant_tree(person, max_depth=5, current_depth=0):
    if current_depth > max_depth:
        return None

    parents = PersonRelationship.objects.filter(
        secondaryPerson=person, relation='Child'
    ).select_related('primaryPerson')

    parent_list = []
    for parent_relation in parents:
        parent = parent_relation.primaryPerson
        parent_tree = build_descendant_tree(parent, max_depth, current_depth + 1)
        if parent_tree:
            parent_list.append(parent_tree)

    return {
        'name': person.nepaliName,
        'gender': person.gender,
        'children': parent_list
    }

def build_ancestor_tree(person, max_depth=10, current_depth=0):
    # if current_depth > max_depth:
    #     return None

    children = PersonRelationship.objects.filter(
        primaryPerson=person, relation='Child'
    ).select_related('secondaryPerson')

    children_list = []
    for child_relation in children:
        child = child_relation.secondaryPerson
        child_tree = build_ancestor_tree(child, max_depth, current_depth + 1)
        if child_tree:
            children_list.append(child_tree)

    return {
        'name': person.nepaliName,
        'gender': person.gender,
        'children': children_list
    }

def family_tree(request, pk):
    person = get_object_or_404(Person, pk=pk)
    ancestors_tree = build_ancestor_tree(person)
    descendants_tree = build_descendant_tree(person)

    context = {
        'person': person,
        'ancestors_tree': ancestors_tree,
        'descendants_tree': descendants_tree,
    }
    return render(request, family_tree_template, context)



# Code to be checked from here before adding to production
