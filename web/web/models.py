from django.db import models

class Audio_store(models.Model):
    record=models.FileField(upload_to='documents/')
    class Meta:
        db_table='Audio_store'

class Text_convert(models.Model):
    converted_text = models.TextField()
