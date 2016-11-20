from __future__ import unicode_literals
from django.db import models

class Person(models.Model):
    amnh_id = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, default='')
    GENDER_CHOICES = ((0, 'N/A'), (1, 'Female'), (2, 'Male'))
    gender = models.PositiveSmallIntegerField(
        choices=GENDER_CHOICES,
        default=0,
    )
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Expedition(models.Model):
    amnh_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(default='')
    start_year = models.PositiveSmallIntegerField(blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    members = models.ManyToManyField(Person)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class FieldNote(models.Model):
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default='')
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class Location(models.Model):
    name = models.CharField(max_length=200)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class FieldEntry(models.Model):
    fieldnote = models.ForeignKey(FieldNote, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    ENTRY_TYPE_CHOICES = ((0, 'Text'), (1, 'Image'), (2, 'Video'))
    entry_type = models.PositiveSmallIntegerField(
        choices=ENTRY_TYPE_CHOICES,
        default=0,
    )
    description = models.TextField(default='')
    url = models.URLField(default='')
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
