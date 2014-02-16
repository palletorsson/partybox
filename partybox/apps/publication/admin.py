from django.contrib import admin
from models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'body', 'datetime_created',)

admin.site.register(Post, PostAdmin)


