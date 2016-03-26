from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
import apiclient
from apiclient.discovery import build
from django.core.mail import send_mail,EmailMessage
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# import classes
# from classes import *

DEVELOPER_KEY = "AIzaSyC4lxc1NfUV09y_vX9kTiRKvSbK6bc6rP0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)


class Video:
    def __init__(self):
        self.title = ""
        self.id = ""
        self.description = ""
        self.thumbnail_url = ""
        self.thumbnail_width = 0
        self.thumbnail_height = 0
        self.channelTitle = ""
        self.duration = ""
        self.caption = ""
        self.viewCount = 0
        self.likeCount = 0


class Channel:
    def __init__(self):
        self.title = ""
        self.id = ""
        self.description = ""
        self.thumbnail_url = ""
        self.thumbnail_width = 0
        self.thumbnail_height = 0


# Create your views here.
def home(request):
    return render(request, 'music/home.html', {})


def login(request):
    return render(request, 'music/login.html', {})


def register(request):
    return render(request, 'music/register.html', {})


def savedetails(request):
    firstname = request.POST["firstname"]
    lastname = request.POST["lastname"]
    email = request.POST["email"]
    mobile = request.POST["mobile"]
    username = request.POST["username"]
    password = request.POST["password"]
    try:
        o = Login.objects.get(username=username)
        return render(request, 'music/register.html', {'error_message': username + " already taken"})
    except (KeyError, Login.DoesNotExist):
        l = Login(username=username, password=password)
        l.save()
        l.detail_set.create(firstname=firstname, lastname=lastname, email=email, mobile=mobile)
        return render(request, 'music/login.html', {'error_message': "Account Successfully Registered.Login Here"})



def validate(request):
    uname = request.POST["username"]
    pwd = request.POST["password"]
    try:
        user = Login.objects.get(username=uname)
    except (KeyError, Login.DoesNotExist):
        return render(request, 'music/login.html', {'error_message': "Username is not found in database"})
    else:

        if pwd == user.password:

            # return HttpResponseRedirect('music:user', args=(user.id,))
            detail = Detail.objects.get(pk=user.id)
            send_mail("Conformation of DBMS Accout","PLease Click Below link to confirm your email you registered on DBMS",
                  'cs13b1037@iith.ac.in',['cs13b1042@iith.ac.in'],fail_silently=True)
            popular_videos = popular()
            context = {
                'id': user.id,
                'fullname': detail.firstname + detail.lastname,
                'email': detail.email,
                'popular_videos': popular_videos,
            }

            return render(request, 'music/user.html', context)
        else:
            return render(request, 'music/login.html', {'error_message': "Incorrect Username,Password Combination"})


def user(request, id):
    return render(request, "music/user.html", {'id': id})


def search(request):
    query = request.POST["search"]
    search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=5
    ).execute()

    videos = []
    channels = []
    # playlists = []

    for search_result in search_response.get("items", []):
        # print search_result
        # if "snippet" in search_result and "thumbnails" in search_result["snippet"] and "default" in search_result["snippet"]["thumbnails"]:
        #     print search_result["snippet"]["thumbnails"]["default"]
        if search_result["id"]["kind"] == "youtube#video":
            v = Video()
            if "id" in search_result and "videoId" in search_result["id"]:
                v.id = search_result["id"]["videoId"]
            get_info(v, search_result)
            videos.append(v)
        elif search_result["id"]["kind"] == "youtube#channel":
            ch = Channel()
            get_channel_info(ch, search_result)
            channels.append(ch)
    return render(request, 'music/search.html', {'query': query, 'videos': videos, 'channels': channels})


def watch(request, id):
    related_videos = related(id)
    return render(request, 'music/watch.html', {'id': id, 'related_videos': related_videos})


def popular():
    # youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    #                 developerKey=DEVELOPER_KEY)

    video_response = youtube.videos().list(
            chart="mostPopular",
            part='id,snippet,statistics,contentDetails',
            maxResults=5,
            videoCategoryId="10",
    ).execute()

    videos = []

    # print(video_response)
    # Add each result to the list, and then display the list of matching videos.
    for video_result in video_response.get("items", []):
        v = Video()
        if "id" in video_result:
            v.id = video_result["id"]
        get_info(v, video_result)
        videos.append(v)
    # print("Videos:\n", "\n".join(videos), "\n")
    return videos


def related(id):
    search_response = youtube.search().list(
            type="video",
            relatedToVideoId=id,
            part="id,snippet",
            maxResults=5,
    ).execute()
    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            v = Video()
            if "id" in search_result and "videoId" in search_result["id"]:
                v.id = search_result["id"]["videoId"]
            get_info(v, search_result)
            videos.append(v)
    return videos


def get_info(v, video_result):
    # if "id" in video_result:
    #     v.id = video_result["id"]
    if "snippet" in video_result:
        if "title" in video_result["snippet"]:
            v.title = video_result["snippet"]["title"]
        if "description" in video_result["snippet"]:
            v.description = video_result["snippet"]["description"]
        if "thumbnails" in video_result["snippet"]:
            if "default" in video_result["snippet"]["thumbnails"]:
                if "url" in video_result["snippet"]["thumbnails"]["default"]:
                    v.thumbnail_url = video_result["snippet"]["thumbnails"]["default"]["url"]
                    #  print(v.thumbnail_url)
                if "width" in video_result["snippet"]["thumbnails"]["default"]:
                    v.thumbnail_width = video_result["snippet"]["thumbnails"]["default"]["width"]
                if "height" in video_result["snippet"]["thumbnails"]["default"]:
                    v.thumbnail_height = video_result["snippet"]["thumbnails"]["default"]["height"]
        if "channelTitle" in video_result["snippet"]:
            v.channelTitle = video_result["snippet"]["channelTitle"]
    if "contentDetails" in video_result:
        if "duration" in video_result["contentDetails"]:
            v.duration = video_result["contentDetails"]["duration"]
        if "caption" in video_result["contentDetails"]:
            v.caption = video_result["contentDetails"]["caption"]
    if "statistics" in video_result:
        if "viewCount" in video_result["statistics"]:
            v.viewCount = video_result["statistics"]["viewCount"]
        if "likeCount" in video_result["statistics"]:
            v.likeCount = video_result["statistics"]["likeCount"]


def get_channel_info(ch, search_result):
    if "id" in search_result:
        ch.id = search_result["id"]["channelId"]
    if "snippet" in search_result:
        if "channelTitle" in search_result["snippet"]:
            ch.channelTitle = search_result["snippet"]["channelTitle"]
        if "descritption" in search_result["snippet"]:
            ch.description = search_result["snippet"]["description"]
        if "thumbnails" in search_result["snippet"]:
            if "default" in search_result["snippet"]["thumbnails"]:
                if "url" in search_result["snippet"]["thumbnails"]["default"]:
                    ch.thumbnail_url = search_result["snippet"]["thumbnails"]["default"]["url"]
                if "width" in search_result["snippet"]["thumbnails"]["default"]:
                    ch.thumbnail_width = search_result["snippet"]["thumbnails"]["default"]["width"]
                if "height" in search_result["snippet"]["thumbnails"]["default"]:
                    ch.thumbnail_height = search_result["snippet"]["thumbnails"]["default"]["height"]
