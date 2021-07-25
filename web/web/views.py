from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import AudioForm, CreateUserForm
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
import speech_recognition as sr #for audio to text
from django.template import Context, Template
from .models import Text_convert

def register(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('login')


		context = {'form':form}
		return render(request, 'register.html', context)

def login_user(request):
    print("in login")
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'login.html', context)

def logout_user(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def index(request):
    print("in index")
    return render(request, 'index.html')

@login_required(login_url='login')
def upload_audio(request):
    if request.method == "POST":
        form = AudioForm(request.POST,request.FILES or None)
        if form.is_valid():
            form.save()

            return redirect('audiototext')
    else:
        form = AudioForm()
    return render(request, "audio.html", {"form":form})

@login_required(login_url='login')
def audio_to_text(request):
    HttpResponse("successfully uploaded")
    text=""
    file=""
    if request.method == "POST":
        PRIVATE_DIR = getattr(settings, "MEDIA_ROOT", None)
        path_join=join(PRIVATE_DIR,'documents')
        onlyfiles = [f for f in listdir(path_join) if isfile(join(path_join, f))]
        for file_name in onlyfiles:
            if ".wav" in file_name:
                file=file_name
                full_path=join(path_join,file_name)
                print("full_path",full_path)
                sound = full_path
                r = sr.Recognizer()
                with sr.AudioFile(sound) as source:
                    r.adjust_for_ambient_noise(source)
                    print("Converting Audio To Text ..... ")
                    audio = r.listen(source)
                text=r.recognize_google(audio)
                print("Converted Audio Is : \n" + text)
                remove_path=join(path_join, file_name)
                print("removing...",remove_path)
                os.remove(remove_path)
                # context = Context({"text":text})
                text_convert = Text_convert()
                text_convert.converted_text = text
                text_convert.save()
                render(request, 'convert_audio.html',{"text":text, "file":file})




    return render(request, 'convert_audio.html', {"text":text, "file":file})

@login_required(login_url='login')
def download_text(request):
	print(request)
	print("look here")
	field_name = 'converted_text'
	obj = Text_convert.objects.last()
	text = getattr(obj, field_name)
	response=HttpResponse(content_type='text/plain')
	response['Content-Disposition']='attachment; filename=voice.txt'
	response.writelines(text)
	return response
