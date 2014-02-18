from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from apps.publication.forms import PostForm
from models import Post
from forms import PostForm


def AddPost(request):
    if request.POST:
        save_post(request)
        return HttpResponseRedirect(reverse('list_posts'))

def Posts(request):
    postform = PostForm()


    posts = Post.objects.all().order_by('-datetime_created')

    posts.doctype = lambda: None
    audio = Post.objects.filter(docfile__iendswith='mp3')
    images = Post.objects.filter(docfile__iendswith='jpg')

    for p in posts:
        string = str(p.docfile)
        if string.endswith("jpg"):
            p.doctype = "jpg"
        elif string.endswith("png"):
            p.doctype = "png"
        elif string.endswith("mp3"):
            p.doctype = "mp3"
        elif string.endswith("ogg"):
            p.doctype = "ogg"
        elif string.endswith("pdf"):
            p.doctype = "pdf"
        else:
            p.doctype = "none"


    return render_to_response('publication/posts.html', {
            'posts': posts,
            'postform': postform,
            'audio': audio,
            'images': images,
        }, context_instance=RequestContext(request))


def save_post(request):
    """
    Saves a comment to the stream
    """
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = Post(docfile = request.FILES["docfile"], body = request.POST['body'])
        newdoc.save()

    else:
        print form.errors

