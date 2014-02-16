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
    """
    Handles posts
    """
    postform = PostForm()


    posts = Post.objects.all().order_by('-datetime_created')
    posts.doctype = lambda: None

    for p in posts:
        string = str(p.document)
        if string.endswith("mp3"):
            p.doctype = "mp3"
        else:
            p.doctype = "pdf"


    return render_to_response('publication/posts.html', {
            'posts': posts,
            'postform': postform,
        }, context_instance=RequestContext(request))


def save_post(request):
    """
    Saves a comment to the stream
    """
    form = PostForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
    else:
        print form.errors