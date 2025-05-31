import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# importing messages
from django.contrib import messages

# Model Forms.
from .forms import UserPostForm, AnswerForm


def home(request):
    user_posts = Topic.objects.all()

    context = {'user_posts':user_posts}
    return render(request, 'forum-main.html', context)

@login_required(login_url='login')
def userPost(request,type,id):
    # User Post form.
    form = UserPostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            title = request.POST.get('title')
            description = request.POST.get('description')
            topic = Topic.objects.create(title=title, author=request.user, description=description)
            if(type =="d"):
                topic.related_document= Document.objects.get(id=id)
            elif(type =="r"):
                topic.related_rectangle = Rectangle.objects.get(id=id)

            topic.save()
            return redirect("/forum")
    else:
        if(type == 'd'):
            document = Document.objects.get(id=id)
            user_post = Topic.objects.filter(related_document=document)
        elif(type == 'r'):
            rect = Rectangle.objects.get(id=id)
            user_post = Topic.objects.filter(related_rectangle=rect)
        if(len(user_post)>0):
            return redirect('topic-detail',id=user_post[0].id)

        form = UserPostForm()

    context = {'form':form}
    return render(request, 'user-post.html', context)


@login_required(login_url='login')
def postTopic(request, id):
    # Get specific user post by id.
    post_topic = get_object_or_404(Topic, id=id)

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
    topic_posted = Topic.objects.filter(author=request.user)
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
    search_query = request.GET.get('q')#check secu TODO
    queryset = Topic.objects.all()

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query) 
        ).distinct()
        
        q_count = queryset.count()
    else:
        messages.error(request, f"Looks like you didn't put any keyword. Please try again.")
        return redirect('forum')

    context = {
        'queryset':queryset,
        'search_query':search_query,
        'q_count':q_count
    }

    return render(request, 'search-result.html', context)


def upvote(request):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    
    # has_upvoted = False

    if answer.upvotes.filter(id = request.user.id).exists():
        answer.upvotes.remove(request.user)
        # has_upvoted = False
    else:
        answer.upvotes.add(request.user)
        answer.downvotes.remove(request.user)
        # has_upvoted = True

    return redirect(f"/topic/{answer.user_post.id}")
    

def downvote(request):
    answer = get_object_or_404(Answer, id=request.POST.get('answer_id'))
    
    # has_downvoted = False
    
    if answer.downvotes.filter(id = request.user.id).exists():
        answer.downvotes.remove(request.user)
        # has_downvoted = False
    else:
        answer.downvotes.add(request.user)
        answer.upvotes.remove(request.user)
        # has_downvoted = True
    
    return redirect(f"/topic/{answer.user_post.id}")


# Blog listing page view.
def announcementsList(request):
    all_posts = Announcement.objects.all()
    context = {'all_posts':all_posts}
    return render(request, 'announcements.html', context)

# Blog single post detail view.
def announcementView(request, id):
    post_detail = get_object_or_404(Announcement, id=id)
    context = {'post_detail':post_detail}
    return render(request, 'announcement-detail.html', context)