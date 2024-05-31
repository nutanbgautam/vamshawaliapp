from django.shortcuts import get_object_or_404, redirect,render
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from Person.models import Person,Suggestion,ContactDetail,PersonRelationship
from django.db.models import Max
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse

#HTML Templates
person_create_template          = 'Person/create_person.html'
persons_list_template           = 'Person/list_persons.html'
person_detail_template          = 'Person/detail_person.html'
suggestion_create_template      = 'Suggestion/create_suggestion.html'
suggestions_list_template       = 'Suggestion/list_suggestions.html'
suggestion_detail_tempalte      = 'Suggestion/detail_suggestion.html'

#Person
class PersonsListView(ListView):
    model               = Person
    queryset            = Person.objects.all()
    template_name       = persons_list_template
    context_object_name = 'persons'
    ordering            = ['-personId']
    paginate_by         = 50 

class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    fields = ['name', 'nepaliName', 'gender', 'photo', 'birth', 'death', 'pustaNumber', 'aliveOrDead', 'bookReferenceNumber', 'remarks']
    template_name = person_create_template
    success_url = "/"

    def get_form(self, form_class=None):
        form = super(PersonCreateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class': 'form-control'})
        return form

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
    
class PersonUpdateView(LoginRequiredMixin,UpdateView): 
    model               = Person 
    fields              = ['name','nepaliName', 'gender', 'photo','birth','death','pustaNumber','aliveOrDead','bookReferenceNumber','address','cityOrCountry','contactDetails','emailAddress','remarks']
    success_url         = "/"

    def get_form(self, form_class=None):
        form = super(PersonUpdateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class' : 'form-control'})
        return form

def PersonDetailView(request,pk):
    person = get_object_or_404(Person, pk=pk)
    contactDetails = ContactDetail.objects.filter(primaryPerson=person)
    relationshipsA = list(PersonRelationship.objects.filter(primaryPerson=person))
    relationshipsB = list(PersonRelationship.objects.filter(secondaryPerson=person))
    relationshipsA.extend(relationshipsB)
    return render(request,person_detail_template,{"person":person,"contactDetails":contactDetails,"relationships":relationshipsA})

def delete_person(request, pk):
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
    fields              = ['primaryPerson', 'suggestion', 'name','contactOption','contactDetail']
    template_name       = suggestion_create_template
    success_url         = "/"

    def get_initial(self):
        initial = super().get_initial()
        person_id = self.kwargs.get('personid')
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
    fields              = ['primaryPerson', 'suggestion', 'name','contactOption','contactDetail']
    success_url         = "/"

    def get_form(self, form_class=None):
        form = super(SuggestionUpdateView, self).get_form(form_class)
        for visible in form.visible_fields():
            visible.field.widget.attrs.update({'class' : 'form-control'})
        return form

def SuggestionDetailView(request,pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    return render(request,suggestion_detail_tempalte,{"suggestion":suggestion})

def delete_suggestion(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    suggestion.delete()
    return redirect("/") 

def csvDataLoad(request):

    import csv
    from indic_transliteration import sanscript

    filename = 'data.csv'

    # List to hold the processed data
    data = []

    # Function to load the CSV and process rows
    def load_csv(filename):
        with open(filename, mode='r', newline='') as file:
            csvreader = csv.reader(file)
            
            # Skip the header row if there's one
            header = next(csvreader)
            
            # Variable to keep track of the current parent row data
            current_parent_row = None
            
            for row in csvreader:
                if row[0].strip():  # Check if the first column is not empty
                    # Separate out the 9th column data
                    primary_data = [row[5], row[6], row[7]]
                    current_parent_row = row[:5] + [[primary_data]] + row[8:]
                    data.append(current_parent_row)
                elif row[0].strip() == '' and any(row[i].strip() for i in [5, 6, 7]):  # Check if the first column is empty and any of 6th, 7th, or 8th column is not empty
                    if current_parent_row is not None:
                        additional_data = [row[5], row[6], row[7]]  # Collect the 6th, 7th, and 8th column data
                        current_parent_row[5].append(additional_data)

    # Call the function to load and process the CSV
    load_csv(filename)


    def nepali_to_roman(nepali_name):
        roman_nepali_name = sanscript.transliterate(nepali_name, sanscript.DEVANAGARI, sanscript.IAST)
        return roman_nepali_name


    def process_spouse_value(value):
        # Check if the value is equal to "......."
        if value == ".......":
            return ["Unknown"]
        
        # Check if the value contains "," and/or " र " and split accordingly
        if "," in value or " र " in value:
            # Split by comma if present
            if "," in value:
                value_list = value.split(",")
            else:
                value_list = [value]

            # Split each part by " र " if present
            processed_values = []
            for part in value_list:
                if " र " in part:
                    processed_values.extend(part.split(" र "))
                else:
                    processed_values.append(part)
            
            # Remove "." and whitespace from each processed value
            processed_values = [v.replace(".", "").strip() for v in processed_values]
            
            return processed_values
        
        # Return the original value if none of the conditions are met
        return [value]

    def get_max_and_increment():
        # Get the maximum value of the variable in all objects
        max_value = Person.objects.aggregate(Max('personId'))['personId__max']
        # Check if there are any objects in the database
        if max_value is not None:
            # Increment the maximum value by 1
            max_value += 1
        else:
            # If there are no objects, start from 1
            max_value = 1

        return max_value

    row_count = 0
    total_rows = len(data)

    for row in data:
        row_count += 1
        newPerson = Person()
        newPerson.personId = get_max_and_increment()
        newPerson.name = nepali_to_roman(row[0])
        newPerson.nepaliName = row[0]
        newPerson.gender = row[1]
        newPerson.pustaNumber = row[3]
        newPerson.bookReferenceNumber = row[4]
        newPerson.address = row[6]
        newPerson.cityOrCountry = row[7]
        newPerson.contactDetails = row[8]
        newPerson.emailAddress = row[9]
        if row[10] == "N":
            newPerson.aliveOrDead   = "Dead"
        elif row[10] == "Y":
            newPerson.aliveOrDead   = "Alive"
        else:
            newPerson.aliveOrDead   = "Unkown"
        newPerson.save()

        spouses = process_spouse_value(row[2]) 
        childrens = row[5] 

        for spouse in spouses:
            if spouse != "Unknown" and spouse!="":
                newSpouse = Person()
                newSpouse.name = nepali_to_roman(spouse)
                newSpouse.nepaliName = spouse
                if newPerson.gender == "M":
                    newSpouse.gender = "F"
                else:
                    newSpouse.gender = "M"
                newSpouse.personId  = 0
                newSpouse.pustaNumber = newPerson.pustaNumber
                newSpouse.save()

                newSpouseRelation = PersonRelationship()
                newSpouseRelation.primaryPerson = newSpouse
                newSpouseRelation.secondaryPerson = newPerson
                newSpouseRelation.relation = "Spouse"
                newSpouseRelation.save()

        for child in childrens:
            if child[0] != "निसन्तान" and child[2] == "******" and child[0] != "":
                newChild = Person()
                newChild.name = nepali_to_roman(child[0])
                newChild.nepaliName = child[0]
                newChild.gender = child[1]
                if newPerson.gender == "M":
                    newChild.pustaNumber = int(newPerson.pustaNumber)+1
                else:
                    newChild.pustaNumber = int(newPerson.pustaNumber)+1
                    newChild.personId = 0
                newChild.save()

                newChildRelation = PersonRelationship()
                newChildRelation.primaryPerson = newChild
                newChildRelation.secondaryPerson = newPerson
                newChildRelation.relation = "Child"
                newChildRelation.save()

    for row in data:
        selectedPersons = Person.objects.filter(bookReferenceNumber = row[4])
        selectedPerson = selectedPersons[0]

        childrens = row[5] 

        for child in childrens:
            try:
                if child[0] != "निसन्तान" and child[2] != "******" and child[0] != "" and child[2] != "":
                    bookReferenceNumber = child[2]
                    selectedChild = Person.objects.filter(bookReferenceNumber = bookReferenceNumber)

                    selectedChild = selectedChild[0]
                    newChildRelation = PersonRelationship()
                    newChildRelation.primaryPerson = selectedChild
                    newChildRelation.secondaryPerson = selectedPerson
                    newChildRelation.relation = "Child"
                    newChildRelation.save()

            except:pass

    return redirect(reverse('list_persons'))     


class SearchView(View):
    def get(self,request,*args,**kwargs):

        return render(request,'search_form.html')

    def post(self,request,*args,**kwargs):
        foundPersons = []
        personName = request.POST.get('personName')
        personPustaNumber = request.POST.get('personPustaNumber')
        personGrandfatherName = request.POST.get('personGrandfatherName')
        personBookReferenceNumber = request.POST.get('personBookReferenceNumber')
        personContactDetail = request.POST.get('personContactDetail')
        personId = request.POST.get('personId')
        isGautamVamsha = request.POST.get('isGautamVamsha')
        persons = Person.objects.all()
        try:
            if personName != "" and personName != None:
                persons = persons.filter(Q(name__icontains=personName) | Q(nepaliName__icontains=personName) )
        except:pass

        try:
            if personPustaNumber != "" and personPustaNumber != None:
                persons = persons.filter(pustaNumber = int(personPustaNumber))
        except:pass

        try:
            if personBookReferenceNumber != "" and personBookReferenceNumber != None:
                persons = persons.filter(bookReferenceNumber=personBookReferenceNumber)
        except:pass

        try:
            if personContactDetail != "" and personContactDetail != None:
                persons = persons.filter(contactDetails__icontains = personContactDetail)
        except:pass

        try:
            if personId != ""  and personId != None:
                persons = persons.filter(id = int(personId))
        except:pass

        try:
            if personGrandfatherName != "" and personGrandfatherName != None:

                # persons = [person for person in persons if person.get_parents[0].secondaryPerson.get_parents[0].nepaliName=="खगेन्द्रप्रसाद/खडानन्द" ]
                pass 
        except:pass

        try:
            if isGautamVamsha != ""  and isGautamVamsha != None:
                if isGautamVamsha == "on":
                    persons = persons.filter(personId__gt = 0)
        except:pass


        foundPersons = list(persons)
        return render(request,persons_list_template,{'persons':foundPersons})
    
def build_ancestor_tree(person, max_depth=10, current_depth=0):
    if current_depth > max_depth:
        return None

    parents = PersonRelationship.objects.filter(
        secondaryPerson=person, relation='Child'
    ).select_related('primaryPerson')

    parent_list = []
    for parent_relation in parents:
        parent = parent_relation.primaryPerson
        parent_tree = build_ancestor_tree(parent, max_depth, current_depth + 1)
        if parent_tree:
            parent_list.append(parent_tree)

    return {
        'name': person.nepaliName,
        'gender': person.gender,
        'children': parent_list
    }

def build_descendant_tree(person, max_depth=10, current_depth=0):
    if current_depth > max_depth:
        return None

    children = PersonRelationship.objects.filter(
        primaryPerson=person, relation='Child'
    ).select_related('secondaryPerson')

    children_list = []
    for child_relation in children:
        child = child_relation.secondaryPerson
        child_tree = build_descendant_tree(child, max_depth, current_depth + 1)
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
    return render(request, 'family_tree.html', context)



# Code to be checked from here before adding to production

