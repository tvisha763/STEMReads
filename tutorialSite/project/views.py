from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Post, Comment, Staff, Request
import bcrypt
import requests
import urllib
import os
from datetime import datetime

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.

def home(request):
    if request.session.get('logged_in') == True:
        return redirect('/project/dashboard')
    else:
        return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password').encode("utf8")
        confirmPass = request.POST.get('confirmPass').encode("utf8")
        inputs = [email, username, password, confirmPass, phone]

        # checking if confirm password matches password   
        if (password != confirmPass):
            messages.error(request, "The passwords do not match.")
            return redirect('signup')

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please fill all the boxes.")
                return redirect('signup')

        if password != '' and len(password) < 6:
            messages.error(request, "Your password must be at least 6 charecters.")
            return redirect('signup')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. If this is you, please log in.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this username already exists. Please pick another one.")
            return redirect('signup')

        else:
            salt = bcrypt.gensalt()
            user = User()
            user.email = email
            user.username = username
            user.phone = phone
            user.password = bcrypt.hashpw(password, salt)
            user.salt = salt
            user.save()
            return redirect('login')
    else:
        if request.session.get('logged_in'):
            return redirect('dashboard')

    return render(request, 'auth/signup.html')

def login(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password').encode("utf8")
            inputs = [username, password]

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('login')

            

            if User.objects.filter(username=username).exists():
                saved_hashed_pass = User.objects.filter(username=username).get().password.encode("utf8")[2:-1]
                saved_salt = User.objects.filter(username=username).get().salt.encode("utf8")[2:-1]
                user  = User.objects.filter(username=username).get()
                request.session["username"] = user.username
                request.session['logged_in'] = True
            
                salted_password = bcrypt.hashpw(password, saved_salt)
                if salted_password != saved_hashed_pass:
                    messages.error(request, "Your password is incorrect.")
                    return render(request, 'auth/login.html')
                if salted_password == saved_hashed_pass:
                    return redirect('dashboard')
                

            else:
                messages.error(request, "An account with this username does not exist. Please sign up.")
                return redirect('login')

    else:
        if request.session.get('logged_in'):
            return redirect('dashboard')

    return render(request, 'auth/login.html')


    
def logout(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        return redirect('/project/login')
    else:
        request.session["username"] = None
        request.session['logged_in'] = False
        return redirect('/project/')



def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    else:
        posts = Post.objects.all()
        user = User.objects.get(username=request.session["username"])
        
        class PostClass:
            def __init__(self, post, blurb):
                self.post = post
                self.blurb = blurb
        postList = []

        for post in posts:
            blurb = post.text.split()[:100]
            blurb2 = ' '.join(blurb) + '...'
            postList.append(PostClass(post, blurb2))

        postList.reverse()
        context = {
            "posts": postList,
            "status" : user.status,
        }

        return render(request, 'dashboard.html', context)
    

def writePost(request):
    if not request.session.get('logged_in'):
        return redirect('/project/')

    else:
        user = User.objects.get(username=request.session["username"])
        if user.status != 2:
            return redirect('dashboard')
        if request.method == "POST":
            title = request.POST.get("title")
            author = request.POST.get("author")
            image = request.FILES.get('image')
            video = request.POST.get("video")
            text = request.POST.get("text")

            post = Post(title=title, author=author, image=image, video_embed=video, text=text)
            post.save()
            id = post.id
            return redirect('/project/view-post/'+str(id)+'/')
        else:
            return render(request, 'writePost.html')
        
def viewPost(request, post_id):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    else:
        post = Post.objects.get(id=post_id)
        user = User.objects.get(username=request.session["username"])
        Context = {
            "comments" : Comment.objects.filter(post_id=post_id),
            "post" : post,
            "status" : user.status,
        }
        return render(request, 'viewPost.html', Context) 


def search(request):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    else:
        if request.method == "POST":
            search = request.POST.get("search")
            results = []
            posts = Post.objects.all()
            
            for post in posts:
                if search in post.title:
                    results.append(post)
                elif search in post.author:
                    results.append(post)
                elif search in post.text:
                    results.append(post)
            
            class PostClass:
                def __init__(self, post, blurb):
                    self.post = post
                    self.blurb = blurb

            postList = []

            for result in results:
                blurb = result.text.split()[:100]
                blurb2 = ' '.join(blurb) + '...'
                postList.append(PostClass(result, blurb2))

            postList.reverse()

            user = User.objects.get(username=request.session["username"])
            context = {
                "posts" : postList,
                "status" : user.status,
            }

            return render(request, 'search.html', context)
        else:
            return render(request, 'search.html')

def comment(request, post_id):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    else:
        user = User.objects.get(username=request.session["username"])
        post = Post.objects.get(id=post_id)
        if request.method == "POST":
            message = request.POST.get("message")
            text = Comment()
            text.post_id = post.id
            text.user = user
            text.message = message
            text.save()
        class Id():
            def __init__(self, id):
                self.id = id
  
        context = {
            "comments" : Comment.objects.filter(post_id=post.id),
            "post" : post,
        
        }
        return render(request, 'viewPost.html', context)


def staff(request):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    
    else:
        staff = Staff.objects.all()
        user = User.objects.get(username=request.session["username"])
        context = {
            "staff" : staff,
            "padding" : len(staff)*250,
            "status" : user.status,
        }
        return render(request, 'staff.html', context)
    

def request(request):
    if not request.session.get('logged_in'):
        return redirect('/project/')
    else:
        if request.method == "POST":
            user = User.objects.get(username=request.session["username"])
            title = request.POST.get("title")
            text = request.POST.get("request")
            req = Request()
            req.user = user
            req.title = title
            req.request = text
            req.save()
            return redirect('/project/dashboard')
        else:
            return render(request, 'request.html')
