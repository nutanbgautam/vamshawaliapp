from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

class Person(models.Model):
    GENDER_CHOICES=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"Other")
    ]

    id                  = models.AutoField(primary_key=True)

    #Personal Details
    name                = models.CharField(max_length=100,blank=True,null=True)
    nepaliName          = models.CharField(max_length=100)
    gender              = models.CharField(max_length=1,choices=GENDER_CHOICES,blank=False,default=None)
    photo               = models.ImageField(upload_to="person/images",max_length=200,blank=True,null=True)
    birth               = models.DateField(blank=True,null=True)
    death               = models.DateField(blank=True,null=True)
    aliveOrDead         = models.CharField(max_length=7,blank=True,default="Unkown")

    #Vamshawali Details
    personId            = models.IntegerField(default=0)
    pustaNumber         = models.BigIntegerField(null=True,blank=True)
    bookReferenceNumber = models.CharField(max_length=100,blank=True)

    #Additional Details
    remarks             = models.CharField(max_length=1000,blank=True)

    #Contact Details beside Contact Object
    address             = models.CharField(max_length=200,blank=True)
    cityOrCountry       = models.CharField(max_length=200,blank=True)
    contactDetails      = models.CharField(max_length=200,blank=True)
    emailAddress        = models.CharField(max_length=200,blank=True)

    created_on          = models.DateTimeField(auto_now_add=True)
    last_edited_on      = models.DateTimeField(auto_now=True)
    last_edited_by      = models.ForeignKey(User,on_delete=models.DO_NOTHING,default=1)

    def __str__(self):
        parent_name = ""
        grandfather_name = ""
        greatgrandfather_name = ""

        if self.gender == 'M':
            relationAttribute = ["छोरा","नाती","पनाती","सिर्मान",""]
        elif self.gender == 'F':
            relationAttribute = ["छोरी","नातिनी","पनातिनी","सिर्मती",""]
        
        # Fetching the father's name
        father_relation = PersonRelationship.objects.filter(primaryPerson=self, relation='Child').select_related('secondaryPerson').first()
        if father_relation:
            parent_name = father_relation.secondaryPerson.nepaliName
            # Fetching the grandfather's name
            grandfather_relation = PersonRelationship.objects.filter(primaryPerson=father_relation.secondaryPerson, relation='Child').select_related('secondaryPerson').first()

            if grandfather_relation:
                grandfather_name = grandfather_relation.secondaryPerson.nepaliName
                greatgrandfather_relation = PersonRelationship.objects.filter(primaryPerson=grandfather_relation.secondaryPerson, relation='Child').select_related('secondaryPerson').first()
                if greatgrandfather_relation is not None:
                    greatgrandfather_name = greatgrandfather_relation.secondaryPerson.nepaliName

        # If no father is found, try to find mother
        if not parent_name:
            mother_relation = PersonRelationship.objects.filter(secondaryPerson=self, relation='Child').select_related('primaryPerson').first()
            if mother_relation:
                father_relation = PersonRelationship.objects.filter(primaryPerson=mother_relation.primaryPerson, relation='Child').select_related('secondaryPerson').first()
                if father_relation:
                    parent_name = father_relation.secondaryPerson.nepaliName
                    # Fetching the grandfather's name
                    grandfather_relation = PersonRelationship.objects.filter(primaryPerson=father_relation.secondaryPerson, relation='Child').select_related('secondaryPerson').first()
                    if grandfather_relation:
                        grandfather_name = grandfather_relation.secondaryPerson.nepaliName
                        if greatgrandfather_relation is not None:
                            greatgrandfather_name = greatgrandfather_relation.secondaryPerson.nepaliName

        if not greatgrandfather_name:
            if not grandfather_name:
                return f"{self.nepaliName} : पुस्ता - {self.pustaNumber}"
            return f"{grandfather_name} को {relationAttribute[1]}, {parent_name} को {relationAttribute[0]}, {self.nepaliName} : पुस्ता - {self.pustaNumber}"
        return f"{greatgrandfather_name} को {relationAttribute[2]}, {grandfather_name} को {relationAttribute[1]}, {parent_name} को {relationAttribute[0]}, {self.nepaliName} : पुस्ता - {self.pustaNumber}"

        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detail_person',kwargs={'pk':self.id})
    
    def age(self):
        from datetime import datetime
        if self.birth:
            return (datetime.now().date() - self.birth).days
        else: return "No Birth Date Provided"

    def get_spouses(self):
        spousesA = PersonRelationship.objects.filter(primaryPerson=self,relation="Spouse").select_related('secondaryPerson')
        spousesA = [spouse.secondaryPerson for spouse in spousesA]
        spousesB = PersonRelationship.objects.filter(secondaryPerson=self,relation="Spouse").select_related('primaryPerson')
        spousesB = [spouse.primaryPerson for spouse in spousesB]
        spousesA.extend(spousesB)
        return spousesA
    
    def get_parents(self):
        parents  = PersonRelationship.objects.filter(primaryPerson=self,relation="Child")
        return parents

    def get_childrens(self):
        childs = []
        children = PersonRelationship.objects.filter(secondaryPerson=self, relation='Child').select_related('primaryPerson')
        for child_relation in children:
            child = child_relation.primaryPerson
            childs.append(child)
        return childs

    def get_descendants(self):
        descendants = []
        def fetch_descendants(person):
            children = PersonRelationship.objects.filter(secondaryPerson=person, relation='Child').select_related('primaryPerson')
            for child_relation in children:
                child = child_relation.primaryPerson
                descendants.append(child)
                fetch_descendants(child)

        fetch_descendants(self)
        return descendants

    def get_ancestors(self, max_depth=10):
        ancestors = []
        def fetch_ancestors(person,depth):
            if depth > 0:
                parents = PersonRelationship.objects.filter(primaryPerson=person, relation='Child').select_related('secondaryPerson')
                for parent_relation in parents:
                    parent = parent_relation.secondaryPerson
                    ancestors.append(parent)
                    fetch_ancestors(parent, depth - 1)

        fetch_ancestors(self, max_depth)
        return ancestors
    
    def save(self,*args,**kwargs):
        def get_max_and_increment():
            # Get the maximum value of the variable in all objects
            max_value = Person.objects.aggregate(Max('personId'))['personId__max']
            # Check if there are any objects in the database
            if max_value is not None:
                # Increment the maximum value by 1
                max_value += 1
            elif max_value == None:
                max_value = 0
            else:
                # If there are no objects, start from 1
                max_value = 1
            
            return max_value
                
        import nepali_roman as nr
        #Save Romanized Nepali Name if not provided
        if self.nepaliName and not self.name:
            self.name =nr.romanize_text(self.nepaliName).lower() 

        super(Person,self).save()
        try:
            #Get Pusta Number from Parent then set self Pusta Number
            if len(self.get_parents())>0:
                for parent in self.get_parents():
                    if parent.secondaryPerson.personId >0 :
                        self.pustaNumber = parent.secondaryPerson.pustaNumber + 1
                        self.personId = get_max_and_increment()

        except Exception as e:print("Exception ",e)

        super(Person,self).save()


class PersonRelationship(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Child',"Child"),
        ('Spouse',"Spouse")
    ]
    primaryPerson       = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='primary_person')
    relation            = models.CharField(max_length=8,choices=RELATIONSHIP_CHOICES,blank=False,default=None)
    secondaryPerson     = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='secondary_person')

    def __str__(self):
        primary_person = self.primaryPerson
        secondary_person = self.secondaryPerson


        # Fetching primary person's father and grandfather
        primary_father_name = ""
        primary_grandfather_name = ""
        primary_father_relation = PersonRelationship.objects.filter(primaryPerson=primary_person, relation='Child').select_related('secondaryPerson').first()
        if primary_father_relation:
            primary_father_name = primary_father_relation.secondaryPerson.nepaliName
            primary_grandfather_relation = PersonRelationship.objects.filter(primaryPerson=primary_father_relation.secondaryPerson, relation='Child').select_related('secondaryPerson').first()
            if primary_grandfather_relation:
                primary_grandfather_name = primary_grandfather_relation.secondaryPerson.nepaliName

        # Fetching secondary person's father and grandfather
        secondary_father_name = ""
        secondary_grandfather_name = ""
        secondary_father_relation = PersonRelationship.objects.filter(primaryPerson=secondary_person, relation='Child').select_related('secondaryPerson').first()
        if secondary_father_relation:
            secondary_father_name = secondary_father_relation.secondaryPerson.nepaliName
            secondary_grandfather_relation = PersonRelationship.objects.filter(primaryPerson=secondary_father_relation.secondaryPerson, relation='Child').select_related('secondaryPerson').first()
            if secondary_grandfather_relation:
                secondary_grandfather_name = secondary_grandfather_relation.secondaryPerson.nepaliName
        
        if self.primaryPerson.personId == 0:
            return f"{primary_person.nepaliName} is {self.relation} of {secondary_person.nepaliName} Father: {secondary_father_name} Grandfather: {secondary_grandfather_name}"
        elif self.secondaryPerson.personId == 0:
            return f"Father: {primary_father_name} || Grandfather: {primary_grandfather_name} ||{primary_person.nepaliName} is {self.relation} of {secondary_person.nepaliName}"
        else:
            return f"Father: {primary_father_name} || Grandfather: {primary_grandfather_name} ||{primary_person.nepaliName} is {self.relation} of {secondary_person.nepaliName} || Father: {secondary_father_name} || Grandfather: {secondary_grandfather_name} ||"

    def save(self,*args,**kwargs):
        super(PersonRelationship,self).save()
        super(Person,self.primaryPerson).save()

class ContactDetail(models.Model):
    CONTACT_CHOICES =[
        ('Facebook',"Facebook"),
        ('Instagram',"Instagram"),
        ('LinkedIn',"LinkedIn"),
        ('MobileNumber',"MobileNumber"),
        ('HomeAddress',"HomeAddress"),
        ('Email',"Email")
    ]

    primaryPerson       = models.ForeignKey(Person,on_delete=models.CASCADE)
    contactOption       = models.CharField(max_length=15,choices=CONTACT_CHOICES,blank=False,default=None)
    contactDetail       = models.CharField(max_length=100)

    def __str__(self):
        return str(self.primaryPerson.name+" "+self.contactOption+" is "+self.contactDetail)


class Suggestion(models.Model):
    CONTACT_CHOICES =[
        ('Facebook',"Facebook"),
        ('Instagram',"Instagram"),
        ('LinkedIn',"LinkedIn"),
        ('MobileNumber',"MobileNumber"),
        ('HomeAddress',"HomeAddress"),
        ('Email',"Email")
    ]

    primaryPerson           = models.ForeignKey(Person,on_delete=models.CASCADE)
    suggestion              = models.CharField(max_length=200)
    photo                   = models.ImageField(upload_to="suggestion/person/images",max_length=200,blank=True,null=True)

    suggestorName           = models.CharField(max_length=100,blank=True)
    suggestorContactOption  = models.CharField(max_length=15,choices=CONTACT_CHOICES,blank=True,default=None)
    suggestorContactDetail  = models.CharField(max_length=100,blank=True)

    created_on              = models.DateTimeField(auto_now_add=True)
    last_edited_on          = models.DateTimeField(auto_now=True)
    last_edited_by          = models.ForeignKey(User,on_delete=models.DO_NOTHING,default=1)    
