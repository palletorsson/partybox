from django.db import models
from django.core.validators import MaxLengthValidator

class Post(models.Model):
    body = models.TextField(validators=[MaxLengthValidator(10000)])
    docfile = models.FileField("upload jpg, png, pfd or mp3", upload_to='documents/%Y/%m/%d' , blank=True, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.body
