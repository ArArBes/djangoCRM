from django.db import models

class Company(models.Model):
    title = models.CharField(max_length=100, unique=True)
    inn = models.CharField(max_length=12, unique=True)
    owner = models.OneToOneField(
        'authenticate.User',
        on_delete=models.CASCADE,
        related_name='owned_company'
    )

    def __str__(self):
        return f"Компания {self.title}, владелец {self.owner.email}"

class Storage(models.Model):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='storage'
    )
    address = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"Склад компании {self.company.title}"