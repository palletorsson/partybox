from django.db import models
from django.core.validators import MaxLengthValidator
from filebrowser.fields import FileBrowseField

class Post(models.Model):
    body = models.TextField(validators=[MaxLengthValidator(10000)])
    image = FileBrowseField("Image", max_length=200, directory="images/", extensions=[".jpg"], blank=True, null=True)
    document = FileBrowseField("PDF", max_length=200, directory="documents/", extensions=[".pdf",".doc", ".mp3"], blank=True, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.body