import json
from ctypes.wintypes import DOUBLE

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from crowdsourcing.models import Rectangle,Document
from .models import *
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
# importing messages
from django.contrib import messages

# Model Forms.
from .forms import UserPostForm, AnswerForm
# String module
from django.template.loader import render_to_string

# Create your views here.

def home(request):
    user_posts = UserPost.objects.all()
    
    # Display latest posts.
    latest_blogs = BlogPost.objects.order_by('-timestamp')[0:3]

    latest_topics = UserPost.objects.order_by('-date_created')[0:3]
    
    context = {
        'user_posts':user_posts,
        'latest_blogs':latest_blogs,
        'latest_topics':latest_topics
    }
    return render(request, 'forum-main.html', context)

@login_required(login_url='login')
def userPost(request,type,id):
    # User Post form.
    form = UserPostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            title = request.POST.get('title')
            description = request.POST.get('description')
            topic = UserPost.objects.create(title=title, author=request.user, description=description)
            if(type =="d"):
                topic.related_document= Document.objects.get(id=id)
            elif(type =="r"):
                topic.related_rectangle = Rectangle.objects.get(id=id)

            topic.save()
            return redirect('home')
    else:
        if(type == 'd'):
            document = Document.objects.get(id=id)
            user_post = UserPost.objects.filter(related_document=document)
        elif(type == 'r'):
            rect = Rectangle.objects.get(id=id)
            user_post = UserPost.objects.filter(related_rectangle=rect)
        if(len(user_post)>0):
            return redirect('topic-detail',pk=user_post[0].id)

        form = UserPostForm()

    context = {'form':form}
    return render(request, 'user-post.html', context)

@login_required(login_url='login')
def postTopic(request, pk):
    # Get specific user post by id.
    post_topic = get_object_or_404(UserPost, pk=pk)

    # Count Post View only for authenticated users
    if request.user.is_authenticated:
        TopicView.objects.get_or_create(user=request.user, user_post=post_topic)

    # Get all answers of a specific post.
    answers = Answer.objects.filter(user_post = post_topic)

    # Answer form.
    answer_form = AnswerForm(request.POST or None)
    if request.method == "POST":
        if answer_form.is_valid():
            content = request.POST.get('content')
            # passing User Id & User Post Id to DB
            ans = Answer.objects.create(user_post=post_topic, user=request.user, content=content)
            ans.save()
            return HttpResponseRedirect(post_topic.get_absolute_url())
    else:
        answer_form = AnswerForm()
    image=None
    rectangles_data =[]
    if(post_topic.related_rectangle != None):
        document = Document.objects.get(pk=post_topic.related_rectangle.document.id)
        image = document.image

        rect = Rectangle.objects.get(id=post_topic.related_rectangle.id)

        rectangles_data ={
                "x": rect.x,
                "y": rect.y,
                "width": rect.width,
                "height": rect.height,
                "angle": rect.angle,
                "id": rect.id
            }
        rectangles_data = json.dumps([rectangles_data])
    else:
        if(post_topic.related_document != None):
            image = post_topic.related_document.image

    context = {
        'image':image,
        'rectangles_data':rectangles_data,
        'topic':post_topic,
        'answers':answers,
        'answer_form':answer_form,
        
    }
    return render(request, 'topic-detail.html', context)

@login_required(login_url='login')
def userDashboard(request):
    topic_posted = request.user.userpost_set.all()
    topic_count = topic_posted.count()


    ans = Answer.objects.filter(user=request.user)
    topic_ans=[]
    for i in ans:
        if(i.user_post.author != request.user):
            topic_ans.append(i.user_post)

    context = {
        'topic_posted':topic_posted,
        'ans_posted':topic_ans,
        'topic_count':topic_count,
        'ans_count':len(topic_ans),
    }
    return render(request, 'user-dashboard.html', context)

def searchView(request):
    queryset = UserPost.objects.all()
    search_query = request.GET.get('q')

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query) 
        ).distinct()
        
        q_count = queryset.count()
    else:
        messages.error(request, f"Oops! Looks like you didn't put any keyword. Please try again.")
        return redirect('home')

    
    context = {
        'queryset':queryset,
        'search_query':search_query,
        'q_count':q_count
    }

    return render(request, 'search-result.html', context)


def upvote(request):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    
    has_upvoted = False

    if answer.upvotes.filter(id = request.user.id).exists():
        answer.upvotes.remove(request.user)
        has_upvoted = False        
    else:
        answer.upvotes.add(request.user)
        answer.downvotes.remove(request.user)
        has_upvoted = True

    return HttpResponseRedirect(answer.user_post.get_absolute_url())
    

def downvote(request):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    
    has_downvoted = False
    
    if answer.downvotes.filter(id = request.user.id).exists():
        answer.downvotes.remove(request.user)
        has_downvoted = False
    else:
        answer.downvotes.add(request.user)
        answer.upvotes.remove(request.user)
        has_downvoted = True
    
    return HttpResponseRedirect(answer.user_post.get_absolute_url())

# Blog listing page view.
def blogListView(request):
    
    # Display all blog posts.
    all_posts = BlogPost.objects.all()
    
    context = {
        'all_posts':all_posts
    }
    return render(request, 'blog-listing.html', context)

    
# Blog single post detail view.
def blogDetailView(request, slug):
    # Get specific post by slug.
    post_detail = get_object_or_404(BlogPost, slug=slug)

    context = {
        'post_detail':post_detail,
    }

    return render(request, 'blog-detail.html', context)  

