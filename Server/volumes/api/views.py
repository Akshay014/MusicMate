from api.token import getToken
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .serializers import SongSeriallizer
from rest_framework.parsers import JSONParser
from .serializers import UserSeriallizer
from .aescipher import AESCipher

# Create your views here.
@csrf_exempt
def idCheck(request):
    if request.method == 'GET':
        id = request.GET['id']
        try:
            query_set = User.objects.get(name=id)
            result = dict()
            result['statusCode'] = 200
            result['status'] = 'Already Exist'
            return JsonResponse(result, status = 200)
        except User.DoesNotExist as e:
            result = dict()
            result['statusCode'] = 200
            result['status'] = 'Allow'
            return JsonResponse(result, status = 200)
        except Exception as e:
            result['statusCode'] = 404
            result['status'] = 'Error'
            return JsonResponse(result, status = 404)

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        cipher = AESCipher()
        
        q = User(name=data['name'], password = cipher.encrypt(data['password']), nickName = data['nickName'], encryptKey=cipher.key)
        q.save()
        token = getToken(q.id)
        result = dict()
        result['statusCode'] = 200
        result['status'] = 'allow'
        result['key'] = q.encryptKey
        result['token'] = token
        return JsonResponse(result, status = 404)

# @csrf_exempt
import base64
import json
import requests

client_id = 'ee7b63f166a142a3b29f5f6c8095eb1d'
client_secret = 'e83335f20e2e47e89d230ad1b7efe7bc'

# SPOTIFY API TOKEN 받기
def get_headers(client_id, client_secret):
    endpoint = 'https://accounts.spotify.com/api/token'

    encoded = base64.b64encode('{}:{}'.format(client_id,client_secret).encode('utf-8')).decode('ascii')
    headers = {'Authorization' : 'Basic {}'.format(encoded)}
    grant_type = {'grant_type' : 'client_credentials'}

    res = requests.post(endpoint, headers=headers, data=grant_type)
    raw = json.loads(res.text)
    access_token = raw['access_token']

    headers = {'Authorization' : 'Bearer {}'.format(access_token)}
    return headers

# 테스트 페이지
def test(request):
    return render(request, 'api/test.html')

def searchMusic(request):
    # Spotify API 에서 검색 결과 받아오기
    endpoint = 'https://api.spotify.com/v1/search'
    spotify_token = get_headers(client_id, client_secret)
    params = {
        'q': request.GET['search'],
        'type': 'track',
        'limit': '1'
    }

    r = requests.get(endpoint,params=params,headers=spotify_token)
    raw = json.loads(r.text)

    # Json Filtering
    items = []
    for i in range(0,len(raw['tracks']['items'])):
        item = {
            'musicName': raw['tracks']['items'][i]['name'],
            'artist': raw['tracks']['items'][i]['artists'][0]['name'],
            'musicPreview': raw['tracks']['items'][i]['preview_url'],
            'albumArt': raw['tracks']['items'][i]['album']['images'][0]['url'],
            'albumName': raw['tracks']['items'][i]['album']['name']
        }
        items.append(item)

    # Result
    result = {
        'statusCode' : 200,
        'status': 'success',
        'items': items
    }

    #return JsonResponse(result,status=200)
    return render(request,'api/result.html',{'result': result})