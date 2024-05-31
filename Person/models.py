from django.db import models
from django.contrib.auth.models import User

class Person(models.Model):
    GENDER_CHOICES=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"Other")
    ]

    id                  = models.AutoField(primary_key=True)

    #Personal Details
    name                = models.CharField(max_length=100)
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
        return str(self.nepaliName+"- पुस्ता:"+str(self.pustaNumber))

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detail_person',kwargs={'pk':self.id})
    
    def age(self):
        from datetime import datetime
        if self.birth:
            return (datetime.now().date() - self.birth)
        else: return "No Birth Date Provided"

    def get_spouses(self):
        spousesA = PersonRelationship.objects.filter(primaryPerson=self,relation="Spouse")
        spousesA = [spouse.secondaryPerson for spouse in spousesA]
        spousesB = PersonRelationship.objects.filter(secondaryPerson=self,relation="Spouse")
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
    
class PersonRelationship(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Child',"Child"),
        ('Spouse',"Spouse")
    ]
    primaryPerson       = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='primary_person')
    relation            = models.CharField(max_length=8,choices=RELATIONSHIP_CHOICES,blank=False,default=None)
    secondaryPerson     = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='secondary_person')

    def __str__(self):
        return str(self.primaryPerson.name+" is "+self.relation+" of "+self.secondaryPerson.name)
    
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

    primaryPerson       = models.ForeignKey(Person,on_delete=models.CASCADE)
    suggestion          = models.CharField(max_length=200)

    name                = models.CharField(max_length=100,blank=True)
    contactOption       = models.CharField(max_length=15,choices=CONTACT_CHOICES,blank=True,default=None)
    contactDetail       = models.CharField(max_length=100,blank=True)

    created_on          = models.DateTimeField(auto_now_add=True)
    last_edited_on      = models.DateTimeField(auto_now=True)
    last_edited_by      = models.ForeignKey(User,on_delete=models.DO_NOTHING,default=1)    
