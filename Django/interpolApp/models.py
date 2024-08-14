from django.db import models

class Notice(models.Model):
    entity_id = models.CharField(max_length=100, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    forename = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    nationalities = models.JSONField(null=True, blank=True)  
    self_url = models.URLField(max_length=200, null=True, blank=True)
    images_url = models.URLField(max_length=200, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=200, null=True, blank=True)

    distinguishing_marks = models.CharField(max_length=255, null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    eyes_colors_id = models.JSONField(null=True, blank=True) 
    sex_id = models.CharField(max_length=5, null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, null=True, blank=True)
    arrest_warrants = models.JSONField(null=True, blank=True)  
    country_of_birth_id = models.CharField(max_length=5, null=True, blank=True)
    hairs_id = models.JSONField(null=True, blank=True)  
    languages_spoken_ids = models.JSONField(null=True, blank=True)  
    height = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.forename} {self.name} - {self.entity_id}"
