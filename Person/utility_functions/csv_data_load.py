from Person.models import Person, PersonRelationship
from django.db.models import Max
from django.urls import reverse
from django.shortcuts import redirect
import nepali_roman as nr

def csv_data_load():

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


    def process_spouse_value(value):
        # Check if the value is equal to "......."
        if value == "...":
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
        newPerson.name = nr.romanize_text(row[0]).lower() 
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
                newSpouse.name = nr.romanize_text(spouse).lower() 
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
            if "निसन्तान" not in child[0] and child[2] == "******" and child[0] != "" and child[0] != "": 
                newChild = Person()
                newChild.name = nr.romanize_text(child[0]).lower()
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
