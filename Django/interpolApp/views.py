from django.shortcuts import render, get_object_or_404
from .models import Notice
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import requests
from datetime import datetime
from django.db.models.functions import TruncSecond

def interpol(request):
    all_notices = Notice.objects.all()

    latest_time = Notice.objects.latest('updated_at').updated_at
    recent_notices = Notice.objects.filter(updated_at=latest_time)

    # Format the datetime to a string format for comparison in the template
    latest_time_str = latest_time.strftime('%Y-%m-%d %H:%M:%S')

    context = {
        "notices": all_notices,
        "latest_time": latest_time_str,  # Pass the formatted datetime string
    }
    
    return render(request, "interpolApp/interpolWeb.html", context=context)



def notice_detail(request , notice_id):

    notice = get_object_or_404(Notice, entity_id=notice_id)
    url = notice.self_url

    
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://google.com'
    }


    
    response = requests.get(url, headers=headers)

    print(response.status_code)
   
    if response.status_code == 200:
        data = response.json()
        print(data)
        date_of_birth_str = data.get('date_of_birth')
        if date_of_birth_str:
            try:
               
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            except ValueError:
                date_of_birth = None
        else:
            date_of_birth = None
        
       
        notice.entity_id = data.get('entity_id', notice.entity_id)
        notice.date_of_birth = date_of_birth
        notice.distinguishing_marks = data.get('distinguishing_marks', notice.distinguishing_marks)
        notice.weight = data.get('weight', notice.weight)
        notice.nationalities = data.get('nationalities', notice.nationalities)
        notice.eyes_colors_id = data.get('eyes_colors_id', notice.eyes_colors_id)
        notice.sex_id = data.get('sex_id', notice.sex_id)
        notice.place_of_birth = data.get('place_of_birth', notice.place_of_birth)
        notice.forename = data.get('forename', notice.forename)
        notice.arrest_warrants = data.get('arrest_warrants', notice.arrest_warrants)
        notice.country_of_birth_id = data.get('country_of_birth_id', notice.country_of_birth_id)
        notice.hairs_id = data.get('hairs_id', notice.hairs_id)
        notice.name = data.get('name', notice.name)
        notice.languages_spoken_ids = data.get('languages_spoken_ids', notice.languages_spoken_ids)
        notice.height = data.get('height', notice.height)
        notice.self_url = data.get('self_url', notice.self_url)
        notice.images_url = data.get('images_url', notice.images_url)
        notice.thumbnail_url = data.get('thumbnail_url', notice.thumbnail_url)
   
        notice.save()


    
    return render(request, 'interpolApp/notice_detail.html', {'noti': notice})

