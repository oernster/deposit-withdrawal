from django.db import models


class Commitment(models.Model):
    identifier = models.IntegerField()
    date = models.DateField()
    amount = models.FloatField()
    fund = models.CharField(max_length=50)


class Investment(models.Model):
    name = models.CharField(max_length=50)
    commitments = models.ManyToManyField(Commitment)