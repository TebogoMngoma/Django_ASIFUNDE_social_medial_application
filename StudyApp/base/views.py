from django.shortcuts import render , redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate ,login ,logout
# Create your views here.
from .models import Room , Topic , Message
from .forms import RoomForm

# rooms = [
#     {'id':1,
#      'name':'lets learn python'},
#       {'id':2,
#      'name':'im familiar with the basics, lets learn the intermediate stuff'},
#       {'id':3,
#      'name':'i want to learn Javascript,am i in the wrong platform?'}
# ]
# the loginPage function is where a user will be redirected when logging in the site 
def loginPage(request):
    page ='login'
    #if the user is registered , redirect them to home page
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User Not Found')
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or Password does not exist')

    context = {'page':page}
    return render(request,'base/login_register.html',context)

# this function is when a user wants to log out of the website
def logoutUser(request):
    logout(request)
    return redirect('home')

# this function is when a user wants to register to the website to have an access to many features that guests do not have
def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    return render(request,'base/login_register.html',{"form":form})

# this function is the view of the home page
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))  
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms':rooms,'topics':topics , 'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)


# this is a room function , this are the features of the room pages
def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)

# this function is for every registered user on the platform
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_message':room_message,'topic':topics}
    return render(request,'base/profile.html',context)


# all the functions below createRoom , updateRoom , deleteRoom , deleteMessage have a fuunction named @login_required above them which give control of the functions of the app
# for example , if a user is registered they can create , update and delete rooms and also delete messages  

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        if form.is_valid:
            form.save()
            return redirect('home')
    context = {"form":form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{"obj":room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{"obj":message})