import datetime
import json
import logging
import re
import traceback
from urllib.request import urlopen

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from github import Github
from google_play_scraper.scraper import PlayStoreScraper
from google_play_scraper.util import PlayStoreException

from landing.constants import *

VIDEOS_INFO = None
APPS_INFO = None
OPEN_SOURCE_INFO = None
PROJECTS_INFO = None
NEXT_UPDATE = None


def home(request):
    check_if_project_info_update_required()
    return render(request, 'landing/home.html', {'landing_page': True,
                                                 'videos_info': VIDEOS_INFO,
                                                 'apps_info': APPS_INFO,
                                                 'open_source_info': OPEN_SOURCE_INFO,
                                                 'projects_info': PROJECTS_INFO})


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        all_contact_info = f'Name: {name}. Email: {email}. Subject: {subject}. Message: {message}'
        log(all_contact_info)
        if send_mail(f'New Contact from {name}', all_contact_info, EMAIL, [EMAIL]):
            return HttpResponse()
        else:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=404)


def video_detail(request, video_id):
    video_info_url = \
        f'''https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}'''
    video_info = json.loads(urlopen(video_info_url).read())['items'][0]
    video_description = video_info['snippet']['description']
    video_description = replace_url_to_link(video_description)
    video_base = 'https://www.youtube.com/embed/'
    video_url = video_base + video_id
    title = video_info['snippet']['title']

    return render(request, 'landing/video_detail.html', {'additional_navbar_style': 'display: flex !important;',
                                                         'block_content_div_style': 'padding-top: 3rem;',
                                                         'video_description': video_description,
                                                         'video_url': video_url,
                                                         'title': title})


def check_if_project_info_update_required():
    global VIDEOS_INFO, APPS_INFO, OPEN_SOURCE_INFO, PROJECTS_INFO, NEXT_UPDATE
    first_call = VIDEOS_INFO is None or APPS_INFO is None or OPEN_SOURCE_INFO is None or PROJECTS_INFO is None
    update_needed = NEXT_UPDATE is None or NEXT_UPDATE < datetime.datetime.now()
    if first_call or update_needed:
        log("updating project info")
        VIDEOS_INFO = get_videos_info()
        APPS_INFO = get_apps_info()
        OPEN_SOURCE_INFO = get_open_source_info()
        PROJECTS_INFO = get_projects_info()
        NEXT_UPDATE = datetime.datetime.now() + datetime.timedelta(days=1)


def replace_url_to_link(value):
    urls = re.compile(URL_REGEX, re.MULTILINE | re.UNICODE)
    value = urls.sub(r'<a href="\1" target="_blank">\1</a>', value)
    return value


def get_videos_info():
    videos_info = dict()
    url = f'https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={YOUTUBE_CHANNEL_ID}&part=snippet,id&order=date'
    data_json = json.loads(urlopen(url).read())
    for video_data in data_json['items']:
        if video_data['id']['kind'] == 'youtube#video':
            video_id = video_data['id']['videoId']
            video_img = video_data['snippet']['thumbnails']['high']['url']
            video_title = video_data['snippet']['title']
            videos_info[video_title] = {'img': video_img, 'id': video_id, 'type': 'Video'}
    return videos_info


def get_apps_info():
    # for some reason, API not working properly. Using static data below for now
    return {
        'PhotoAI - Mobile Image Classification': {
            'img': 'https://play-lh.googleusercontent.com/ugR4F_fhjPHPIa3I0FMcYuEHFQv_mix3c1I6pRJ40KIbIPmN0Od24_sPYKBCs9cZiXqI=w480-h960-rw',
            'link': 'https://play.google.com/store/apps/details?id=com.soumio.mikes.photoai&hl=en&gl=us',
            'type': 'App'
        },
        'Mismatch Run': {
            'img': 'https://play-lh.googleusercontent.com/D-BtCfsciNOmO5VXXe_VJnuKJhCuWQAwA-P-xK_OJWR_17R5YB13dUrdYTy4e6WhhGjP=w480-h960-rw',
            'link': 'https://play.google.com/store/apps/details?id=com.SoumIO.Mismatch_Run&hl=en&gl=us',
            'type': 'App'
        }
    }
    # apps_info = dict()
    # try:
    #     google_play_store_scraper = PlayStoreScraper()
    #     app_ids = google_play_store_scraper.get_app_ids_for_developer("Soumio", country="us", lang="en")
    #     for app_id in app_ids:
    #         app_info = google_play_store_scraper.get_app_details(app_id, country="us", lang="en")
    #         log(app_info)
    #         if 'link' in app_info and 'title' in app_info and 'icon_link' in app_info:
    #             apps_info[app_info['title']] = {'link': app_info['link'], 'img': app_info['icon_link'], 'type': 'App'}
    # except PlayStoreException as e:
    #     log(f"Can't get app details: {e}. Details: {traceback.print_exc()}")
    # return apps_info


def get_open_source_info():
    return get_repo_infos(OPEN_SOURCE_REPO_IDS, 'Open Source')


def get_projects_info():
    return get_repo_infos(PROJECT_REPO_IDS, 'Personal Project')


def get_repo_infos(repo_ids, type):
    open_source_info = dict()
    github_scraper = Github(GITHUB_API_TOKEN)
    for open_source_id in repo_ids:
        repo_info = github_scraper.get_repo(open_source_id)
        open_source_info[repo_info.name] = {'link': repo_info.html_url, 'img': GITHUB_LOGO, 'type': type}
    return open_source_info


def log(msg):
    logging.warning(msg)
