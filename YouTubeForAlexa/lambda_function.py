# -*- coding: utf-8 -*-
from __future__ import print_function
from os import environ
try:
    from urllib.error import HTTPError  # python3
except:
    from urllib2 import HTTPError  # python2
import logging
from random import shuffle, randrange
import requests
import re
import json
from datetime import datetime
from dateutil import tz
from fuzzywuzzy import fuzz
from strings import *
strings = strings_en
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --------------- Helpers that build all of the responses ----------------------
#Variables:
video_url = None
playlist_favo_url = None
playlist_favo_name = None
#Get Latest GitHub Version
update = requests.get('https://api.github.com/repos/wes1993/YouTubeForAlexa/releases/latest')
githubversion = update.json()["tag_name"]
version = "09.02.2023"

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_cardless_speechlet_response(output, reprompt_text, should_end_session, speech_type='PlainText'):
    text_or_ssml = 'text'
    if speech_type == 'SSML':
        text_or_ssml = 'ssml'
    return {
        'outputSpeech': {
            'type': speech_type,
            text_or_ssml: output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_audio_or_video_response(title, output, should_end_session, url, token, offsetInMilliseconds=0):
    if video_or_audio == [True, 'video']:
        return build_video_response(title, output, url)
    else:
        return build_audio_speechlet_response(title, output, should_end_session, url, token, offsetInMilliseconds=0)


def build_audio_speechlet_response(title, output, should_end_session, url, token, offsetInMilliseconds=0):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'directives': [{
            'type': 'AudioPlayer.Play',
            'playBehavior': 'REPLACE_ALL',
            'audioItem': {
                'stream': {
                    'token': str(token),
                    'url': url,
                    'offsetInMilliseconds': offsetInMilliseconds
                }
            }
        }],
        'shouldEndSession': should_end_session
    }


def build_cardless_audio_speechlet_response(output, should_end_session, url, token, offsetInMilliseconds=0):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'directives': [{
            'type': 'AudioPlayer.Play',
            'playBehavior': 'REPLACE_ALL',
            'audioItem': {
                'stream': {
                    'token': str(token),
                    'url': url,
                    'offsetInMilliseconds': offsetInMilliseconds
                }
            }
        }],
        'shouldEndSession': should_end_session
    }


def build_audio_enqueue_response(should_end_session, url, previous_token, next_token, playBehavior='ENQUEUE'):
    to_return = {
        'directives': [{
            'type': 'AudioPlayer.Play',
            'playBehavior': playBehavior,
            'audioItem': {
                'stream': {
                    'token': str(next_token),
                    'url': url,
                    'offsetInMilliseconds': 0
                }
            }
        }],
        'shouldEndSession': should_end_session
    }
    if playBehavior == 'ENQUEUE':
        to_return['directives'][0]['audioItem']['stream']['expectedPreviousToken'] = str(previous_token)
    return to_return


def build_cancel_speechlet_response(title, output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'directives': [{
            'type': 'AudioPlayer.ClearQueue',
            'clearBehavior': "CLEAR_ALL"
        }],
        'shouldEndSession': should_end_session
    }


def build_stop_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'directives': [{
            'type': 'AudioPlayer.Stop'
        }],
        'shouldEndSession': should_end_session
    }


def build_short_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': should_end_session
    }


def build_response(speechlet_response, sessionAttributes={}):
    return {
        'version': '1.0',
        'sessionAttributes': sessionAttributes,
        'response': speechlet_response
    }


def build_video_response(title, output, url):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'directives': [{
            'type': 'VideoApp.Launch',
            'videoItem': {
                'source': url,
                'metadata': {
                    'title': title,
                }
            }
        }]
    }

# --------------- Main handler ------------------


def lambda_handler(event, context):
    if 'expires' in environ and int(datetime.strftime(datetime.now(), '%Y%m%d')) > int(environ['expires']):
        return skill_expired()
#    elif 'TESTYT' in environ:
#        return test_yt_limit()
    global strings
    if event['request']['locale'][0:2] == 'fr':
        strings = strings_fr
    elif event['request']['locale'][0:2] == 'it':
        strings = strings_it
    elif event['request']['locale'][0:2] == 'de':
        strings = strings_de
    elif event['request']['locale'][0:2] == 'es':
        strings = strings_es
    elif event['request']['locale'][0:2] == 'ja':
        strings = strings_ja
    elif event['request']['locale'][0:2] == 'pt':
        strings = strings_pt
    else:
        strings = strings_en
    for key in strings_en:
        if key not in strings:
            strings[key] = strings_en[key]
    global video_or_audio
    video_or_audio = [False, 'audio']
    if 'VideoApp' in event['context']['System']['device']['supportedInterfaces']:
        video_or_audio[0] = True
        if event['request']['type'] == "IntentRequest":
            if event['request']['intent']['name'] == 'PlayOneIntent':
                video_or_audio[1] = 'video'
    if event['request']['type'] == "LaunchRequest":
        return get_welcome_response(event)
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event)
    elif event['request']['type'] == "SessionEndedRequest":
        logger.info("on_session_ended")
    elif event['request']['type'].startswith('AudioPlayer'):
        return handle_playback(event)

# --------------- Events ------------------


def on_intent(event):
    logger.info(event)
    intent_name = event['request']['intent']['name']
    # Dispatch to your skill's intent handlers
    search_intents = ["SearchIntent", "PlayOneIntent", "PlaylistIntent", "SearchMyPlaylistsIntent", "ShuffleMyPlaylistsIntent", "ChannelIntent", "ShuffleIntent", "ShufflePlaylistIntent", "ShuffleChannelIntent", "PlayMyLatestVideoIntent"]
    add_to_fav = ["AddVideoToFavoritesIntent", "AddChannelToFavoritesIntent"]
    if intent_name in search_intents:
        return search(event)
#        return progressive_response(event)
    elif intent_name in add_to_fav:
        return add_to_favo(event)
    elif intent_name in 'AddPlaylistToFavoritesIntent':
        return add_to_favo_playlist(event)
    elif intent_name == 'NextPlaylistIntent':
        return next_playlist(event)
    elif intent_name == 'SkipForwardIntent':
        return skip_by(event, 1)
    elif intent_name == 'SkipBackwardIntent':
        return skip_by(event, -1)
    elif intent_name == 'SkipToIntent':
        return skip_to(event)
    elif intent_name == 'SayTimestampIntent':
        return say_timestamp(event)
    elif intent_name == 'AutoplayOffIntent':
        return change_mode(event, 'a', 0)
    elif intent_name == 'AutoplayOnIntent':
        return change_mode(event, 'a', 1)
    elif intent_name == "AMAZON.YesIntent":
        return yes_intent(event)
    elif intent_name == "AMAZON.NoIntent":
        return do_nothing()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help()
    elif intent_name == "AMAZON.CancelIntent":
        return do_nothing()
    elif intent_name == "AMAZON.PreviousIntent":
        return skip_action(event, -1)
    elif intent_name == "AMAZON.NextIntent":
        return skip_action(event, 1)
    elif intent_name == "AMAZON.ShuffleOnIntent":
        return change_mode(event, 's', 1)
    elif intent_name == "AMAZON.ShuffleOffIntent":
        return change_mode(event, 's', 0)
    elif intent_name == "AMAZON.ResumeIntent":
        return resume(event)
    elif intent_name == "AMAZON.RepeatIntent" or intent_name == "NowPlayingIntent":
        return say_video_title(event)
    elif intent_name == "AMAZON.LoopOnIntent":
        return change_mode(event, 'l', 1)
    elif intent_name == "AMAZON.LoopOffIntent":
        return change_mode(event, 'l', 0)
    elif intent_name == "AMAZON.StartOverIntent":
        return start_over(event)
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.PauseIntent":
        return stop()
    elif intent_name == "PlayMoreLikeThisIntent":
        return play_more_like_this(event)
    else:
        raise ValueError("Invalid intent")



def progressive_response(event):
    logger.info("progressive Reponse")
    headers = get_headers(event)
    reqid = event['request']['requestId']
    logger.info(headers)
    logger.info(reqid)
    data = { 
        "header":{ 
            "requestId": reqid,
        },
        "directive":{ 
            "type":"VoicePlayer.Speak",
            "speech":"<speak>" + strings['waitloading1'] + "<break time='10s'/>" + strings['waitloading2'] + "<break time='10s'/>" + strings['waitloading3'] + "</speak>"
            #"speech":"<speak>Test Progressive. <audio src='https://file-examples.com/storage/fe6a5406fa63112369b75a2/2017/11/file_example_MP3_700KB.mp3' /></speak>"
        }
        }
#   data = {
#        "value": text,
#        "status": "active"
#    }
    url = event['context']['System']['apiEndpoint'] + '/v1/directives'
    r = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info('progressive_response Executed')
#    speech_output = strings['addedplaylistfavo']
#    return build_response(build_short_speechlet_response(speech_output, should_end_session))
    return search(event)





def handle_playback(event):
    request = event['request']
    if request['type'] == 'AudioPlayer.PlaybackStarted':
        return started(event)
    elif request['type'] == 'AudioPlayer.PlaybackFinished':
        return finished(event)
    elif request['type'] == 'AudioPlayer.PlaybackStopped':
        return stopped(event)
    elif request['type'] == 'AudioPlayer.PlaybackNearlyFinished':
        return nearly_finished(event)
    elif request['type'] == 'AudioPlayer.PlaybackFailed':
        return failed(event)

# --------------- Functions that control the skill's behavior ------------------

def get_headers(event):
    if 'apiAccessToken' in event['context']['System']:
        apiAccessToken = event['context']['System']['apiAccessToken']
        headers = {
            'Authorization': 'Bearer '+apiAccessToken,
            'Content-Type': 'application/json'
        }
        return headers
    else:
        logger.info('apiAccessToken not found')
        return False

#OLD FIX FOR apiAccessToken
#def get_headerslist(event):
#    if 'consentToken' in event['context']['System']['user']['permissions']:
#        consentToken = event['context']['System']['user']['permissions']['consentToken']
#        headers = {
#            'Authorization': 'Bearer '+consentToken,
#            'Content-Type': 'application/json'
#        }
#        return headers
#    else:
#        logger.info('consentToken not found')
#        return False


def get_welcome_response(event):
    list_created = create_list(event, 'YouTube')
    list_created = create_list(event, 'YouTube Favorites', ['Add shortcuts to your favorite videos or playlists like this:', 'that song I like | https://youtu.be/gJLIiF15wjQ', 'super awesome playlist | https://www.youtube.com/playlist?list=PL1EQjK4xc6hsirkCQq-MHfmUqGMkSgUTn'])
    if 'welcome' in environ and (environ['welcome'].lower() == 'short'):
        speech_output = strings['welcome3']
        reprompt_text = strings['welcome4']
    else:
        speech_output = strings['welcome1']
        reprompt_text = strings['welcome2']
    should_end_session = False
    speech_output = '<speak>' + speech_output + '</speak>'
    return build_response(build_cardless_speechlet_response(speech_output, reprompt_text, should_end_session, 'SSML'))


def create_list(event, list_title, list_items=[]):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if not headers:
        return False
    data = {
        "name": list_title,
        "state": "active"
    }
    url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code == 201:
        logger.info('List created')
        listId = r.json()['listId']
        for list_item in reversed(list_items):
            post_list_item(event, listId, headers, list_item)
        return True
    elif r.status_code == 409:
        logger.info('List already exists')
        return True
    elif r.status_code == 403:
        logger.info('List permissions not granted')
        logger.info(r)
        logger.info(r.json())
        return False
    else:
        logger.info(r.status_code)
        logger.info(r.json())
        return True


def get_list_id(event, list_title):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if headers:
        url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'
        r = requests.get(url, headers=headers)
        try:
            lists = r.json()['lists']
        except:
            return None
        for list in lists:
            if list['name'] == list_title and list['state'] == 'active':
                return list['listId']
    return None


def read_list_item(event, listId):
    items = get_list(event, listId)
    if items is not None and len(items) > 0:
        return items[0]['id'], items[0]['value'], items[0]['version']
    return None, None, None


def update_list_item(event, listId, itemId, itemValue, itemVersion, itemStatus='completed'):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if headers:
        data = {
            "value": itemValue,
            "status": itemStatus,
            "version": itemVersion
        }
        url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/items/'+itemId
        r = requests.put(url, headers=headers, data=json.dumps(data))
        logger.info(r.json())


def create_list_item(event, listId, title):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if headers:
        timestamp = event['request']['timestamp']
        utc = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        from_zone = tz.tzutc()
        timezone = get_time_zone(event)
        if type(timezone) == list:
            timezone = 'Europe/London'
            if event['request']['locale'] in locales:
                timezone = locales[event['request']['locale']]
        to_zone = tz.gettz(timezone)
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        the_date = local.strftime('%d%t%m%t%Y %H:%M:%S')
        text = the_date+' '+title
        post_list_item(event, listId, headers, text)



def post_list_item(event, listId, headers, text):
    data = {
        "value": text,
        "status": "active"
    }
    url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/items/'
    r = requests.post(url, headers=headers, data=json.dumps(data))


def get_list(event, listId):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if headers:
        url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/active/'
        r = requests.get(url, headers=headers)
        if 'items' in r.json():
            return r.json()['items']
    return None


def trim_list(event, listId):
    items = get_list(event, listId)
    if items is not None:
        maxLength = 90
        for item in items[maxLength:]:
            itemId = item['id']
            delete_list_item(event, listId, itemId)


def delete_list_item(event, listId, itemId):
#    headers = get_headerslist(event) //OLDFIX
    headers = get_headers(event)
    if headers:
        url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/items/'+itemId
        r = requests.delete(url, headers=headers)


def add_to_list(event, title):
    listId = get_list_id(event, 'YouTube')
    logger.info(listId)
    if listId is not None:
        create_list_item(event, listId, title)
        logger.info('Created item')
        trim_list(event, listId)

def add_to_favo(event):
    should_end_session = True
    listId = get_list_id(event, 'YouTube Favorites')
    logger.info(listId)
    if listId is not None:
        global favo_title
        if favo_title is not None:
            global video_url
            headers = get_headerslist(event)
            text = favo_title+" | "+video_url
            data = {
                "value": text,
                "status": "active"
            }
            url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/items/'
            r = requests.post(url, headers=headers, data=json.dumps(data))
            logger.info('Video Added to Favorites')
            speech_output = strings['addedfavo']
            return build_response(build_short_speechlet_response(speech_output, should_end_session))
        else:
            speech_output = strings['nothingplaying']
            return build_response(build_short_speechlet_response(speech_output, should_end_session))
    else:
        speech_output = strings['listerror']
        return build_response(build_short_speechlet_response(speech_output, should_end_session))

def add_to_favo_playlist(event):
    should_end_session = True
    listId = get_list_id(event, 'YouTube Favorites')
    logger.info(listId)
    if listId is not None:
        global playlist_favo_name
        global playlist_favo_url
        if playlist_favo_name is not None:
#            headers = get_headerslist(event) //OLDFIX
            headers = get_headers(event)
            text = playlist_favo_name+" | "+playlist_favo_url
            data = {
                "value": text,
                "status": "active"
            }
            url = event['context']['System']['apiEndpoint'] + '/v2/householdlists/'+listId+'/items/'
            r = requests.post(url, headers=headers, data=json.dumps(data))
            logger.info('Playlist Added to Favorites')
            speech_output = strings['addedplaylistfavo']
            return build_response(build_short_speechlet_response(speech_output, should_end_session))
        else:
            speech_output = strings['noplaylistplaying']
            return build_response(build_short_speechlet_response(speech_output, should_end_session))
    else:
        speech_output = strings['listerror']
        return build_response(build_short_speechlet_response(speech_output, should_end_session))


def check_favorite_videos(event, query, do_shuffle='0'):
    logger.info('checking for faves')
    listId = get_list_id(event, 'YouTube Favorites')
    if listId is None:
        logger.info('No Youtube Favorites list found')
        return [], strings['video'], None
    items = get_list(event, listId)
    for item in items:
        val = item['value']
        logger.info('checking '+val)
        try:
            name, url = val.split('|')
        except:
            continue
        if query.lower() == name.lower().strip():
            logger.info('match found')
            videos, string_to_return, playlist_title = get_videos_from_url(url.strip())
            if do_shuffle == '1':
                shuffle(videos)
            return videos[0:50], string_to_return, playlist_title
    return [], strings['video'], None


def get_videos_from_url(url):
    t = re.search('youtube.com\/watch\?v=.*&list=([^&]+)', url, re.I)
    if t:
        logger.info('match on t1')
        playlist_id = t.groups()[0]
        videos = get_videos_from_playlist(playlist_id)
        return videos, strings['playlist'], get_title(playlist_id, 'playlists')
    t = re.search('youtube.com\/playlist\?list=([^&]+)', url, re.I)
    if t:
        logger.info('match on t2')
        playlist_id = t.groups()[0]
        videos = get_videos_from_playlist(playlist_id)
        return videos, strings['playlist'], get_title(playlist_id, 'playlists')
    t = re.search('youtube.com\/watch\?v=([^&]+)', url, re.I)
    if t:
        logger.info('match on t3')
        video_id = t.groups()[0]
        return [video_id], strings['video'], None
    t = re.search('youtu.be\/([^&]+)', url, re.I)
    if t:
        logger.info('match on t4')
        video_id = t.groups()[0]
        return [video_id], strings['video'], None
    t = re.search('youtube.com\/channel\/([^&]+)', url, re.I)
    if t:
        logger.info('match on t5')
        channel_id = t.groups()[0]
        videos, errorMessage = video_search(channelId=channel_id)
        return videos, strings['channel'], get_title(channel_id, 'channels')
    t = re.search('youtube.com\/user\/([^&]+)', url, re.I)
    if t:
        logger.info('match on t6')
        username = t.groups()[0]
        channel_info = youtube_channel_search(username)
        if 'items' in channel_info and len(channel_info['items']) > 0 and 'id' in channel_info['items'][0]:
            channel_id = channel_info['items'][0]['id']
            videos, errorMessage = video_search(channelId=channel_id)
            return videos, strings['channel'], get_title(channel_id, 'channels')
    return [], strings['video'], None

def get_help():
    speech_output = strings['help']
    card_title = 'Youtube Help'
    should_end_session = False
    return build_response(build_speechlet_response(card_title, speech_output, None, should_end_session))


def illegal_action():
    speech_output = strings['illegal']
    should_end_session = True
    return build_response(build_short_speechlet_response(speech_output, should_end_session))


def do_nothing():
    return build_response({})


def youtube_search(query, search_type, maxResults, relatedToVideoId=None, channel_id=None, order=None, pageToken=None):
    if 'DEVELOPER_KEY' not in environ:
        return {'error': {'code': 400}}
    params = {}
    for kv in ([['q', query], ['type', search_type], ['maxResults', maxResults],
                ['relatedToVideoId', relatedToVideoId], ['channelId', channel_id], ['order', order], ['pageToken', pageToken],
                ['part', 'id,snippet'], ['key', environ['DEVELOPER_KEY']]]):
        k = kv[0]
        v = kv[1]
        params[k] = v
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/search'
    if 'youtube_search_url' in environ:
        youtube_search_url = environ['youtube_search_url']
    r = requests.get(youtube_search_url, params=params)
    return r.json()


def youtube_playlist_search(channel_id, pageToken=None):
    params = {}
    for kv in ([['maxResults', 50], ['channelId', channel_id], ['pageToken', pageToken],
                ['part', 'snippet'], ['key', environ['DEVELOPER_KEY']]]):
        k = kv[0]
        v = kv[1]
        params[k] = v
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/playlists'
    if 'youtube_playlist_search_url' in environ:
        youtube_search_url = environ['youtube_playlist_search_url']
    r = requests.get(youtube_search_url, params=params)
    return r.json()


def youtube_playlist_items_search(playlist_id, pageToken=None):
    params = {}
    for kv in ([['maxResults', 50], ['playlistId', playlist_id], ['pageToken', pageToken],
                ['part', 'snippet'], ['key', environ['DEVELOPER_KEY']]]):
        k = kv[0]
        v = kv[1]
        params[k] = v
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    if 'youtube_playlist_items_search_url' in environ:
        youtube_search_url = environ['youtube_playlist_items_search_url']
    r = requests.get(youtube_search_url, params=params)
    return r.json()


def youtube_channel_search(username):
    params = {}
    for kv in ([['maxResults', 50], ['forUsername', username], ['part', 'id'], ['key', environ['DEVELOPER_KEY']]]):
        k = kv[0]
        v = kv[1]
        params[k] = v
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/channels'
    if 'youtube_channel_search_url' in environ:
        youtube_search_url = environ['youtube_channel_search_url']
    r = requests.get(youtube_search_url, params=params)
    return r.json()


def video_search(query=None, relatedToVideoId=None, channelId=None):
    try:
        search_response = youtube_search(query, 'video', 50, relatedToVideoId, channelId)
    except:
        return False, strings['youtubeerror']
    if 'error' in search_response:
        if search_response['error']['code'] == 403:
            return False, strings['error403']
        else:
            return False, strings['apikeyerror']
    videos = []
    for search_result in search_response.get('items', []):
        if 'videoId' in search_result['id']:
            videos.append(search_result['id']['videoId'])
    return videos, ""


def playlist_search(query, sr, do_shuffle='0'):
    playlist_id = ''
    errorMessage = ''
    try:
        search_response = youtube_search(query, 'playlist', 10)
    except:
        return False, strings['youtubeerror']
    if 'error' in search_response:
        if search_response['error']['code'] == 403:
            return False, strings['error403']
        else:
            return False, strings['apikeyerror']
    if sr > len(search_response.get('items')):
        return False, '', sr, strings['nomoreplaylists']
    if len(search_response.get('items')) == 0:
        return False, '', sr, strings['noplaylistresults']
    for playlist in range(sr, len(search_response.get('items'))):
        if 'playlistId' in search_response.get('items')[playlist]['id']:
            playlist_id = search_response.get('items')[playlist]['id']['playlistId']
            break
    sr = playlist
    logger.info('Playlist info: https://www.youtube.com/playlist?list='+playlist_id)
    playlist_title = search_response.get('items')[sr]['snippet']['title']
    global playlist_favo_name
    global playlist_favo_url
    playlist_favo_name = playlist_title
    playlist_favo_url = "https://www.youtube.com/playlist?list="+playlist_id
    videos = get_videos_from_playlist(playlist_id)
    if do_shuffle == '1':
        shuffle(videos)
    return videos[0:50], playlist_title, sr, errorMessage


def get_videos_from_playlist(playlist_id):
    videos = []
    data = {'nextPageToken': ''}
    while 'nextPageToken' in data and len(videos) < 100:
        next_page_token = data['nextPageToken']
        data = youtube_playlist_items_search(playlist_id, next_page_token)
        for item in data['items']:
            try:
                videos.append(item['snippet']['resourceId']['videoId'])
            except:
                pass
    return videos


def my_playlists_search(query, sr, do_shuffle='0'):
    channel_id = None
    playlist_id = None
    if 'MY_CHANNEL_ID' in environ:
        channel_id = environ['MY_CHANNEL_ID']
    search_response = youtube_search(query, 'playlist', 10, channel_id=channel_id)
    if len(search_response.get('items')) == 0:
        search_response = youtube_playlist_search(channel_id)
        for playlist in search_response.get('items'):
            title = playlist['snippet']['title']
            playlist['ratio'] = fuzz.ratio(query.lower(), title.lower())
            playlist['id'] = {'playlistId': playlist['id']}
        search_response['items'] = sorted(search_response['items'], key=lambda k: k['ratio'], reverse=True)
    for playlist in range(sr, len(search_response.get('items'))):
        if 'playlistId' in search_response.get('items')[playlist]['id']:
            playlist_id = search_response.get('items')[playlist]['id']['playlistId']
            break
    if playlist_id is None:
        return [], None, 0
    sr = playlist
    logger.info('Playlist info: https://www.youtube.com/playlist?list='+playlist_id)
    playlist_title = search_response.get('items')[sr]['snippet']['title']
    videos = []
    data = {'nextPageToken': ''}
    while 'nextPageToken' in data and len(videos) < 200:
        next_page_token = data['nextPageToken']
        data = youtube_playlist_items_search(playlist_id, next_page_token)
        for item in data['items']:
            try:
                videos.append(item['snippet']['resourceId']['videoId'])
            except:
                pass
    if do_shuffle == '1':
        shuffle(videos)
    return videos[0:50], playlist_title, sr


def my_latest_video():
    channel_id = None
    if 'MY_CHANNEL_ID' in environ:
        channel_id = environ['MY_CHANNEL_ID']
    if channel_id is None:
        return build_response(build_short_speechlet_response(strings['nochannelid'], True))
    search_response = youtube_search(None, 'video', 50, channel_id=channel_id, order='date')
    videos = []
    for search_result in search_response.get('items', []):
        if 'videoId' in search_result['id']:
            videos.append(search_result['id']['videoId'])
    return videos


def channel_search(query, sr, do_shuffle='0'):
    try:
        search_response = youtube_search(query, 'channel', 10)
    except:
        return False, strings['youtubeerror']
    if 'error' in search_response:
        if search_response['error']['code'] == 403:
            return False, strings['error403']
        else:
            return False, strings['apikeyerror']
    channel_id = search_response.get('items')[sr]['id']['channelId']
    playlist_title = search_response.get('items')[sr]['snippet']['title']
    data = {'nextPageToken': ''}
    videos = []
    while 'nextPageToken' in data and len(videos) < 200:
        next_page_token = data['nextPageToken']
        search_response = youtube_search(query, 'video', 50, channel_id=channel_id, pageToken=next_page_token)
        for item in search_response.get('items'):
            try:
                videos.append(item['id']['videoId'])
            except:
                pass
    if do_shuffle == '1':
        shuffle(videos)
    return videos[0:50], playlist_title

def get_url_and_title(id):
    if 'get_url_service' in environ and (environ['get_url_service'].lower() == 'pytube'):
        return get_url_and_title_pytube(id)
    elif 'get_url_service' in environ and (environ['get_url_service'].lower() == 'rapidapi'):
        return get_url_and_title_rapidapi(id)
    elif 'get_url_service' in environ and (environ['get_url_service'].lower() == 'youtubestream'):
        return get_url_and_title_youtubestream(id)
    else:
        return get_url_and_title_youtube_dl(id)


def get_url_and_title_youtube_dl(id, retry=True):
    import youtube_dl
    logger.info('Getting youtube-dl url for https://www.youtube.com/watch?v='+id)
    youtube_dl_properties = { 'quiet' : True, 'cachedir' : '/tmp/' }
    if 'proxy_enabled' in environ and 'proxy' in environ and environ['proxy_enabled'].lower() == 'true':
        youtube_dl_properties['proxy'] = environ['proxy']
    try:
        with youtube_dl.YoutubeDL(youtube_dl_properties) as ydl:
            yt_url = 'http://www.youtube.com/watch?v='+id
            info = ydl.extract_info(yt_url, download=False)
    except Exception as e:
        if 'unavailable' in e.__str__() or 'not available' in e.__str__():
            logger.info(id+' is unavailable')
            return None, None
        logger.info('youtube_dl error')
        if 'youtube_dl_error_mirror' in environ and 'http' in environ['youtube_dl_error_mirror']:
            logger.info('Trying mirror: '+environ['youtube_dl_error_mirror'])
            params = {'id': id, 'function_name': environ['AWS_LAMBDA_FUNCTION_NAME']}
            r = requests.get(environ['youtube_dl_error_mirror'], params=params)
            info = r.json()
        elif retry:
            logger.info('trying pytube')
            return get_url_and_title_pytube(id, False)
        else:
            return False, False
    if info['is_live'] is True:
        video_or_audio[1] = 'video'
        return info['url'], info['title']
    for f in info['formats']:
        if video_or_audio[1] == 'audio' and f['vcodec'] == 'none' and f['ext'] == 'm4a':
            logger.info(f)
            logger.info(info)
            return f['url'], info['title']
        if video_or_audio[1] == 'video' and f['vcodec'] != 'none' and f['acodec'] != 'none':
            logger.info(f)
            logger.info(info)
            return f['url'], info['title']
    logger.info('Unable to get URL for '+id)
    return None, None

def get_url_and_title_pytube(id, retry=True):
    from pytube import YouTube
    from pytube.exceptions import LiveStreamError, VideoUnavailable
    proxy_list = {}
    if 'proxy_enabled' in environ and 'proxy' in environ and environ['proxy_enabled'] == 'true':
        logger.info('Using PyTube Proxy')
        proxy_list = {'https': environ['proxy']}
    logger.info('Getting pytube url for https://www.youtube.com/watch?v='+id)
    global video_url
    video_url = "https://www.youtube.com/watch?v="+id
    try:
        yt = YouTube('https://www.youtube.com/watch?v='+id, proxies=proxy_list)
    except LiveStreamError:
        logger.info(id+' is a live video')
        return get_live_video_url_and_title(id)
    except VideoUnavailable:
        logger.info(id+' is unavailable')
        return None, None
    except HTTPError as e:
        logger.info('HTTPError code '+str(e.code))
        if retry:
            return get_url_and_title_youtube_dl(id, False)
        return False, False
    except:
        logger.info('Unable to get URL for '+id)
        return None, None
    if video_or_audio[1] == 'video':
        first_stream = yt.streams.filter(progressive=True).first()
    else:
        first_stream = yt.streams.filter(only_audio=True, subtype='mp4').first()
    logger.info(first_stream.url)
    return first_stream.url, first_stream.title

####RAPIDAPI --> DOWNLOAD VIDEO YOUTUBE Link --> https://rapidapi.com/convertisseur.mp3.video/api/download-video-youtube1####
#def get_url_and_title_rapidapi(id, retry=True):
#    apikey = environ['apikey']
#    if 'pytube' in environ and 'http' in environ['pytube']:
#        return get_url_and_title_pytube_server(id)
#    from pytube import YouTube
#    from pytube.exceptions import LiveStreamError, VideoUnavailable
#    proxy_list = {}
#    if 'proxy_enabled' in environ and 'proxy' in environ and environ['proxy_enabled'] == 'true':
#        proxy_list = {'https': environ['proxy']}
#    logger.info('Getting RapidAPi url for https://www.youtube.com/watch?v='+id)
#    global video_url
#    video_url = "https://www.youtube.com/watch?v="+id
#    try:
#        yt = YouTube('https://www.youtube.com/watch?v='+id, proxies=proxy_list)
#    except LiveStreamError:
#        logger.info(id+' is a live video')
#        return get_live_video_url_and_title(id)
#    except VideoUnavailable:
#        logger.info(id+' is unavailable')
#        return None, None
#    except HTTPError as e:
#        logger.info('HTTPError code '+str(e.code))
#        if retry:
#            return get_url_and_title_youtube_dl(id, False)
#        return False, False
#    except:
#        logger.info('Unable to get URL for '+id)
#        return None, None
#    if video_or_audio[1] == 'video':
#        first_stream = yt.streams.filter(progressive=True).first()
#    else:
#        first_stream = yt.streams.filter(only_audio=True, subtype='mp4').first()
#        logger.info('Getting url for https://www.youtube.com/watch?v='+id)
#        url = "https://download-video-youtube1.p.rapidapi.com/mp3/"+id
#        logger.info(url)
#        headers = {
#            'x-rapidapi-key': apikey,
#            'x-rapidapi-host': "download-video-youtube1.p.rapidapi.com"
#            }
#        response = requests.request("GET", url, headers=headers)
#        json_decode = response.json()
#        for value in json_decode['vidInfo'].values():
#           stream_ext = value['dloadUrl']
#           print(stream_ext)
#           break
#    return stream_ext, first_stream.title
####FINE YOUTUBE Video DOwnload####

#def get_url_and_title_rapidapi(id, retry=True):
#    apikey = environ['apikey']
#    if 'pytube' in environ and 'http' in environ['pytube']:
#        return get_url_and_title_pytube_server(id)
#    from pytube import YouTube
#    from pytube.exceptions import LiveStreamError, VideoUnavailable
#    proxy_list = {}
#    if 'proxy_enabled' in environ and 'proxy' in environ and environ['proxy_enabled'] == 'true':
#        proxy_list = {'https': environ['proxy']}
#    logger.info('Getting RapidAPi url for https://www.youtube.com/watch?v='+id)
#    global video_url
#    video_url = "https://www.youtube.com/watch?v="+id
#    try:
#        yt = YouTube('https://www.youtube.com/watch?v='+id, proxies=proxy_list)
#    except LiveStreamError:
#        logger.info(id+' is a live video')
#        return get_live_video_url_and_title(id)
#    except VideoUnavailable:
#        logger.info(id+' is unavailable')
#        return None, None
#    except HTTPError as e:
#        logger.info('HTTPError code '+str(e.code))
#        if retry:
#            return get_url_and_title_youtube_dl(id, False)
#        return False, False
#    except:
#        logger.info('Unable to get URL for '+id)
#        return None, None
#    if video_or_audio[1] == 'video':
#        first_stream = yt.streams.filter(progressive=True).first()
#    else:
#        first_stream = yt.streams.filter(only_audio=True, subtype='mp4').first()
#        logger.info('Getting url for https://www.youtube.com/watch?v='+id)
#        url = "https://youtube-mp3-download1.p.rapidapi.com/dl"
#        querystring = {"id":id}
#        logger.info(url)
#        headers = {
#            'x-rapidapi-key': apikey,
#            'x-rapidapi-host': "youtube-mp3-download1.p.rapidapi.com"
#            }
#        response = requests.request("GET", url, headers=headers, params=querystring)
#        json_decode = response.json()
#        stream_ext = json_decode['link']
#        logger.info(stream_ext)
#    return stream_ext, first_stream.title
#### Il formato del file MP3 che viene estratto non sembra essere Supportato da Alexa #####

def get_url_and_title_rapidapi(id, retry=True):
    apikey = environ['apikey']
    proxy_list = {}
    logger.info('Getting RapidAPi url for https://www.youtube.com/watch?v='+id)
#    logger.info('Getting url for https://www.youtube.com/watch?v='+id)
    url = "https://youtube-mp3-download1.p.rapidapi.com/dl"
    querystring = {"id":id}
    headers = {
        'x-rapidapi-key': apikey,
        'x-rapidapi-host': "youtube-mp3-download1.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    json_decode = response.json()
    stream_ext = json_decode['link']
    first_stream = json_decode['title']
    return stream_ext, first_stream
#### Il formato non sembra essere Supportato #####


def get_url_and_title_youtubestream(id, retry=True):
    logger.info('Getting YouTubeStream url for https://www.youtube.com/watch?v='+id)
    if 'ytstreamurl' in environ:
        url = "https://" + environ['ytstreamurl'] + "/api/meta/" + id
        response = requests.request("GET", url)
        json_decode = response.json()
        try:
            first_stream = json_decode['title']
        except KeyError:
            print("Wrong Video ID Check")
            return None, None
        if video_or_audio[1] == 'video':
            stream_ext = "https://" + environ['ytstreamurl'] + "/api/dl/" + id + "?f=bestvideo"
        else:
            stream_ext = "https://" + environ['ytstreamurl'] + "/api/dl/" + id + "?f=bestaudio"
        logger.info("Sending song: " + first_stream + " to Alexa")
        return stream_ext, first_stream
    else:
        logger.info("Please add URL for YouTubeStream Server in Environ (ytstreamurl)")
        return False, False


def get_live_video_url_and_title(id):
    logger.info('Live video?')
    title = 'live video'
    try:
        u = 'https://www.youtube.com/watch?v='+id
        r = requests.get(u)
        a = re.search('https:[%\_\-\\\/\.a-z0-9]+m3u8', r.text, re.I)
        url = a.group().replace('\\/', '/')
        logger.info(url)
        t = re.search('<title>(.+) - youtube</title>', r.text, re.I)
        if t:
            title = t.groups()[0]
        video_or_audio[1] = 'video'
        return url, title
    except:
        logger.info('Unable to get m3u8')
        return None, None


def yes_intent(event):
    session = event['session']
    sessionAttributes = session.get('attributes')
    if not sessionAttributes or 'intent' not in sessionAttributes or 'sr' not in sessionAttributes:
        return build_response(build_cardless_speechlet_response(strings['gonewrong'], None, True))
    intent = sessionAttributes['intent']
    session['attributes']['sr'] = sessionAttributes['sr'] + 1
    return search(event)


def next_playlist(event):
    intent = event['request']['intent']
    session = event['session']
    logger.info(intent)
    if 'token' not in event['context']['AudioPlayer']:
        speech_output = strings['nothingplaying']
        return build_response(build_short_speechlet_response(speech_output, True))
    current_token = event['context']['AudioPlayer']['token']
    playlist = convert_token_to_dict(current_token)
    if 'sr' not in playlist or 'query' not in playlist:
        return build_response(build_cardless_speechlet_response(strings['gonewrong'], None, True))
    if 'attributes' not in session:
        session['attributes'] = {}
    session['attributes']['sr'] = int(playlist['sr']) + 1
    session['attributes']['query'] = playlist['query']
    return search(event)

def search(event):
    session = event['session']
    intent = event['request']['intent']
    startTime = datetime.now()
    query = ''
    if 'slots' in intent and 'query' in intent['slots']:
        query = intent['slots']['query']['value']
    if environ['AWS_LAMBDA_FUNCTION_NAME'] == 'YouTubeTest':
        query = 'gangnam style'
    logger.info('Looking for: ' + query)
    should_end_session = True
    intent_name = intent['name']
    playlist_title = None
    sessionAttributes = session.get('attributes')
    if not sessionAttributes:
        sessionAttributes = {'sr': 0, 'intent': intent}
    if 'query' in sessionAttributes:
        query = sessionAttributes['query'].replace('_', ' ')
    sr = sessionAttributes['sr']
    playlist = {}
    playlist['s'] = '0'
    playlist['sr'] = sr
    playlist['a'] = '1'
    playlist['i'] = intent_name.replace('Intent', '')
    if intent_name == "PlayOneIntent":
        playlist['a'] = '0'
    playlist['query'] = query.replace(' ', '_')
    if intent_name == "ShuffleIntent" or intent_name == "ShufflePlaylistIntent" or intent_name == "ShuffleChannelIntent" or intent_name == "ShuffleMyPlaylistsIntent":
        playlist['s'] = '1'
    playlist['l'] = '0'
    videos, playlist_channel_video, playlist_title = check_favorite_videos(event, query, playlist['s'])
    if videos == []:
        if intent_name == "PlaylistIntent" or intent_name == "ShufflePlaylistIntent" or intent_name == "NextPlaylistIntent":
            videos, playlist_title, playlist['sr'], errorMessage = playlist_search(query, sr, playlist['s'])
            playlist_channel_video = strings['playlist']
        elif intent_name == "SearchMyPlaylistsIntent" or intent_name == "ShuffleMyPlaylistsIntent":
            videos, playlist_title, playlist['sr'] = my_playlists_search(query, sr, playlist['s'])
            playlist_channel_video = strings['playlist']
        elif intent_name == "ChannelIntent" or intent_name == "ShuffleChannelIntent":
            videos, playlist_title = channel_search(query, sr, playlist['s'])
            playlist_channel_video = strings['channel']
        elif intent_name == "PlayMyLatestVideoIntent":
            videos = my_latest_video()
            playlist_channel_video = strings['video']
        else:
            videos, errorMessage = video_search(query)
            playlist_channel_video = strings['video']
        if videos is False:
            return build_response(build_cardless_speechlet_response(errorMessage, None, True))
    if videos == []:
        return build_response(build_cardless_speechlet_response(strings['novideo'], None, True))
    if len(videos) == 1:
        video_or_audio[1] = 'video'
    next_url = None
    for i, id in enumerate(videos):
        if playlist_channel_video != strings['video'] and (datetime.now() - startTime).total_seconds() > 8:
            return build_response(build_cardless_speechlet_response(playlist_channel_video+" "+playlist_title+" " + strings['notworked'], None, False), sessionAttributes)
        playlist['v'+str(i)] = id
        if next_url is None:
            playlist['p'] = i
            next_url, title = get_url_and_title(id)
    if next_url is False:
        if 'get_url_service' in environ and (environ['get_url_service'].lower() == 'youtubestream'):
            return build_response(build_short_speechlet_response(strings['no_url_youtubestream'], True))
        else:
            return build_response(build_short_speechlet_response(strings['throttled'], True))
    next_token = convert_dict_to_token(playlist)
    if version != githubversion:
        logger.info('Update Available')
        if playlist_title is None:
            speech_output = strings['updateavailable']
            speech_output += strings['playing'] + ' ' + title
        else:
            speech_output = strings['updateavailable']
            speech_output += strings['playing'] + ' ' + playlist_title
        card_title = "Youtube"
        return build_response(build_audio_or_video_response(card_title, speech_output, should_end_session, next_url, next_token))
    elif playlist_title is None:
        speech_output = strings['playing'] + ' ' + title
    else:
        speech_output = strings['playing'] + ' ' + playlist_title
    card_title = "Youtube"
    return build_response(build_audio_or_video_response(card_title, speech_output, should_end_session, next_url, next_token))


def stop():
    should_end_session = True
    speech_output = strings['pausing']
    return build_response(build_stop_speechlet_response(speech_output, should_end_session))


def nearly_finished(event):
    should_end_session = True
    current_token = event['request']['token']
    skip = 1
    next_url, next_token, title = get_next_url_and_token(current_token, skip)
    if title is None:
        playlist = convert_token_to_dict(next_token)
        if playlist['i'] != 'ShuffleMyPlaylists':
            return do_nothing()
        videos, playlist_title, playlist['sr'] = my_playlists_search(playlist['query'], int(playlist['sr']), playlist['s'])
        for i, id in enumerate(videos):
            playlist['v'+str(i)] = id
            if next_url is None:
                playlist['p'] = i
                next_url, title = get_url_and_title(id)
        next_token = convert_dict_to_token(playlist)
    if next_url is False:
        return do_nothing()
    return build_response(build_audio_enqueue_response(should_end_session, next_url, current_token, next_token))


def play_more_like_this(event):
    should_end_session = True
    if 'AudioPlayer' not in event['context'] or 'token' not in event['context']['AudioPlayer']:
        speech_output = strings['nothingplaying']
        return build_response(build_short_speechlet_response(speech_output, True))
    current_token = event['context']['AudioPlayer']['token']
    playlist = convert_token_to_dict(current_token)
    now_playing = playlist['p']
    now_playing_id = playlist['v'+now_playing]
    videos, errorMessage = video_search(None, now_playing_id)
    if videos is False:
        return build_response(build_short_speechlet_response(errorMessage, True))
    next_url = None
    for i, id in enumerate(videos):
        playlist['v'+str(i)] = id
        if next_url is None:
            playlist['p'] = i
            next_url, title = get_url_and_title(id)
    if next_url is False:
        return build_response(build_short_speechlet_response(strings['throttled'], True))
    next_token = convert_dict_to_token(playlist)
    speech_output = strings['playing']+' '+title
    return build_response(build_cardless_audio_speechlet_response(speech_output, should_end_session, next_url, next_token))


def skip_action(event, skip):
    logger.info("event:")
    logger.info(event)
    logger.info("context:")
    logger.info(event['context'])
    should_end_session = True
    current_token = event['context']['AudioPlayer']['token']
    next_url, next_token, title = get_next_url_and_token(current_token, skip)
    if title is None:
        playlist = convert_token_to_dict(next_token)
        if playlist['i'] != 'ShuffleMyPlaylists':
            speech_output = strings['nomoreitems']
            return build_response(build_short_speechlet_response(speech_output, should_end_session))
        videos, playlist_title, playlist['sr'] = my_playlists_search(playlist['query'], int(playlist['sr']), playlist['s'])
        for i, id in enumerate(videos):
            playlist['v'+str(i)] = id
            if next_url is None:
                playlist['p'] = i
                next_url, title = get_url_and_title(id)
        next_token = convert_dict_to_token(playlist)
    if next_url is False:
        return build_response(build_short_speechlet_response(strings['throttled'], True))
    speech_output = strings['playing']+' '+title
    return build_response(build_cardless_audio_speechlet_response(speech_output, should_end_session, next_url, next_token))


def skip_by(event, direction):
    intent = event['request']['intent']
    logger.info(intent)
    if 'token' not in event['context']['AudioPlayer']:
        speech_output = strings['nothingplaying']
        return build_response(build_short_speechlet_response(speech_output, True))
    if 'slots' not in intent:
        speech_output = strings['sorryskipby']
        return build_response(build_short_speechlet_response(speech_output, True))
    if 'hours' in intent['slots'] and 'value' in intent['slots']['hours']:
        try:
            hours = int(intent['slots']['hours']['value'])
        except:
            hours = 0
    else:
        hours = 0
    if 'minutes' in intent['slots'] and 'value' in intent['slots']['minutes']:
        try:
            minutes = int(intent['slots']['minutes']['value'])
        except:
            minutes = 0
    else:
        minutes = 0
    if 'seconds' in intent['slots'] and 'value' in intent['slots']['seconds']:
        try:
            seconds = int(intent['slots']['seconds']['value'])
        except:
            seconds = 0
    else:
        seconds = 0
    if hours == 0 and minutes == 0 and seconds == 0:
        speech_output = strings['sorryskipby']
        return build_response(build_short_speechlet_response(speech_output, True))
    current_offsetInMilliseconds = event['context']['AudioPlayer']['offsetInMilliseconds']
    skip_by_offsetInMilliseconds = direction * (hours * 3600000 + minutes * 60000 + seconds * 1000)
    return resume(event, current_offsetInMilliseconds+skip_by_offsetInMilliseconds)


def skip_to(event):
    intent = event['request']['intent']
    logger.info(intent)
    if 'token' not in event['context']['AudioPlayer']:
        speech_output = strings['nothingplaying']
        return build_response(build_short_speechlet_response(speech_output, True))
    if 'slots' not in intent:
        speech_output = strings['sorryskipto']
        return build_response(build_short_speechlet_response(speech_output, True))
    if 'hours' in intent['slots'] and 'value' in intent['slots']['hours']:
        try:
            hours = int(intent['slots']['hours']['value'])
        except:
            hours = 0
    else:
        hours = 0
    if 'minutes' in intent['slots'] and 'value' in intent['slots']['minutes']:
        try:
            minutes = int(intent['slots']['minutes']['value'])
        except:
            minutes = 0
    else:
        minutes = 0
    if 'seconds' in intent['slots'] and 'value' in intent['slots']['seconds']:
        try:
            seconds = int(intent['slots']['seconds']['value'])
        except:
            seconds = 0
    else:
        seconds = 0
    if hours == 0 and minutes == 0 and seconds == 0:
        speech_output = strings['sorryskipto']
        return build_response(build_short_speechlet_response(speech_output, True))
    offsetInMilliseconds = hours * 3600000 + minutes * 60000 + seconds * 1000
    return resume(event, offsetInMilliseconds)


def resume(event, offsetInMilliseconds=None):
    if 'token' not in event['context']['AudioPlayer']:
        return get_welcome_response(event)
    current_token = event['context']['AudioPlayer']['token']
    should_end_session = True
    speech_output = strings['ok']
    if offsetInMilliseconds is None:
        speech_output = strings['resuming']
        offsetInMilliseconds = event['context']['AudioPlayer']['offsetInMilliseconds']
    next_url, next_token, title = get_next_url_and_token(current_token, 0)
    if title is None:
        speech_output = strings['noresume']
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    return build_response(build_cardless_audio_speechlet_response(speech_output, should_end_session, next_url, current_token, offsetInMilliseconds))


def change_mode(event, mode, value):
    if 'token' not in event['context']['AudioPlayer']:
        speech_output = strings['nothingplaying']
        return build_response(build_short_speechlet_response(speech_output, True))
    current_token = event['context']['AudioPlayer']['token']
    should_end_session = True
    playlist = convert_token_to_dict(current_token)
    playlist[mode] = str(value)
    current_token = convert_dict_to_token(playlist)
    speech_output = strings['ok']
    offsetInMilliseconds = event['context']['AudioPlayer']['offsetInMilliseconds']
    next_url, next_token, title = get_next_url_and_token(current_token, 0)
    return build_response(build_cardless_audio_speechlet_response(speech_output, should_end_session, next_url, current_token, offsetInMilliseconds))


def start_over(event):
    current_token = event['context']['AudioPlayer']['token']
    should_end_session = True
    next_url, next_token, title = get_next_url_and_token(current_token, 0)
    if title is None:
        speech_output = strings['novideo']
        return build_response(build_short_speechlet_response(speech_output, should_end_session))
    speech_output = strings['playing']+" " + title
    return build_response(build_cardless_audio_speechlet_response(speech_output, should_end_session, next_url, next_token))


def say_video_title(event):
    should_end_session = True
    if 'token' in event['context']['AudioPlayer']:
        current_token = event['context']['AudioPlayer']['token']
        next_url, next_token, title = get_next_url_and_token(current_token, 0)
        if title is None:
            speech_output = strings['notitle']
        else:
            speech_output = strings['nowplaying']+" "+title
    else:
        speech_output = strings['nothingplaying']
    return build_response(build_short_speechlet_response(speech_output, should_end_session))


def say_timestamp(event):
    should_end_session = True
    if 'offsetInMilliseconds' in event['context']['AudioPlayer']:
        current_offsetInMilliseconds = int(event['context']['AudioPlayer']['offsetInMilliseconds'])
        hours = current_offsetInMilliseconds / 3600000
        minutes = (current_offsetInMilliseconds - hours*3600000) / 60000
        seconds = (current_offsetInMilliseconds - hours*3600000 - minutes*60000) / 1000
        speech_output = strings['currentposition']
        if hours >= 2:
            speech_output += ' ' + str(hours) + ' ' + strings['hours'] + ', '
        elif hours == 1:
            speech_output += ' ' + str(hours) + ' ' + strings['hour'] + ', '
        if minutes == 1:
            speech_output += ' ' + str(minutes) + ' ' + strings['minute'] + ', '
        else:
            speech_output += ' ' + str(minutes) + ' ' + strings['minutes'] + ', '
        if seconds == 1:
            speech_output += ' ' + str(seconds) + ' ' + strings['second'] + ', '
        else:
            speech_output += ' ' + str(seconds) + ' ' + strings['seconds'] + ', '
    else:
        speech_output = strings['nothingplaying']
    return build_response(build_short_speechlet_response(speech_output, should_end_session))


def convert_token_to_dict(token):
    pi = token.split('&')
    playlist = {}
    for i in pi:
        key = i.split('=')[0]
        val = i.split('=')[1]
        playlist[key] = val
    return playlist


def convert_dict_to_token(playlist):
    token = "&".join(["=".join([key, str(val)]) for key, val in playlist.items()])
    return token


def get_next_url_and_token(current_token, skip):
    should_end_session = True
    speech_output = ''
    playlist = convert_token_to_dict(current_token)
    next_url = None
    title = None
    shuffle_mode = int(playlist['s'])
    loop_mode = int(playlist['l'])
    next_playing = int(playlist['p'])
    autoplay = int(playlist['a'])
    if not autoplay and skip != 0:
        return None, convert_dict_to_token(playlist), None
    number_of_videos = sum('v' in i for i in playlist.keys())
    if shuffle_mode and skip != 0:
        for i in range(int(next_playing), number_of_videos-1):
            playlist['v'+str(i)] = playlist['v'+str(i+1)]
        del(playlist['v'+str(number_of_videos-1)])
        number_of_videos = sum('v' in i for i in playlist.keys())
        if number_of_videos == 0:
            return None, convert_dict_to_token(playlist), None
    while next_url is None:
        next_playing = next_playing + skip
        if shuffle_mode and skip != 0:
            next_playing = randrange(number_of_videos)
        if next_playing < 0:
            if loop_mode:
                next_playing = number_of_videos - 1
            else:
                next_playing = 0
        if next_playing >= number_of_videos and loop_mode:
            next_playing = 0
        next_key = 'v'+str(next_playing)
        if next_key not in playlist:
            break
        next_id = playlist[next_key]
        next_url, title = get_url_and_title(next_id)
        if skip == 0:
            break
    playlist['p'] = str(next_playing)
    next_token = convert_dict_to_token(playlist)
    return next_url, next_token, title


def get_time_zone(event):
    try:
        deviceId = event['context']['System']['device']['deviceId']
        apiAccessToken = event['context']['System']['apiAccessToken']
        apiEndpoint = event['context']['System']['apiEndpoint']
        headers = {'Authorization': 'Bearer '+apiAccessToken}
        url = apiEndpoint + '/v2/devices/'+deviceId+'/settings/System.timeZone'
        r = requests.get(url, headers=headers)
        return r.json()
    except:
        return []


def stopped(event):
    offsetInMilliseconds = event['request']['offsetInMilliseconds']
    logger.info("Stopped at %s" % offsetInMilliseconds)


def started(event):
    logger.info("Started")
    logger.info(event)
    current_token = event['context']['AudioPlayer']['token']
    playlist = convert_token_to_dict(current_token)
    now_playing = playlist['p']
    id = playlist['v'+now_playing]
    title = get_title(id)
    global favo_title
    if title:
        favo_title = title
        add_to_list(event, title)


def get_title(id, type_='videos'):
    try:
        params = {'part': 'snippet', 'id': id, 'key': environ['DEVELOPER_KEY']}
        youtube_search_url = 'https://www.googleapis.com/youtube/v3/'+type_
        r = requests.get(youtube_search_url, params=params)
        return r.json()['items'][0]['snippet']['title']
    except:
        return None


def finished(event):
    logger.info('finished')
    token = event['request']['token']


def failed(event):
    logger.info("Playback failed")
    logger.info(event)
    if 'error' in event['request']:
        logger.info(event['request']['error'])
    should_end_session = True
    playBehavior = 'REPLACE_ALL'
    current_token = event['request']['token']
    skip = 1
    next_url, next_token, title = get_next_url_and_token(current_token, skip)
    if title is None:
        return do_nothing()
    return build_response(build_audio_enqueue_response(should_end_session, next_url, current_token, next_token, playBehavior))


def skill_expired():
    speech_output = '<speak><voice name="Brian"><prosody rate="medium">'
    speech_output += 'Hi there, this is the developer. '
    speech_output += 'If you would like to continue using this skill, please go to https://www.paypal.com/paypalme/wes93 and do an offer. '
    speech_output += '</prosody></voice></speak> '
    return build_response(build_cardless_speechlet_response(speech_output, '', True, 'SSML'))

def test_yt_limit(query=None, relatedToVideoId=None, channelId=None):
    logger.info('video_search_test')
    try:
        search_response = youtube_search_test(query, 'video', 50, relatedToVideoId, channelId)
    except:
        return False, strings['youtubeerror']
    if 'error' in search_response:
        if search_response['error']['code'] == 403:
            return False, strings['error403']
        else:
            return False, strings['apikeyerror']

def youtube_search_test(query="Queen", search_type="video", maxResults="2", relatedToVideoId=None, channel_id=None, order=None, pageToken=None):
    logger.info('youtube_search_test')
    if 'DEVELOPER_KEY' not in environ:
        return {'error': {'code': 400}}
    params = {}
    for kv in ([['q', query], ['type', search_type], ['maxResults', maxResults],
                ['relatedToVideoId', relatedToVideoId], ['channelId', channel_id], ['order', order], ['pageToken', pageToken],
                ['part', 'id,snippet'], ['key', environ['DEVELOPER_KEY']]]):
        k = kv[0]
        v = kv[1]
        params[k] = v
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/search'
    if 'youtube_search_url' in environ:
        youtube_search_url = environ['youtube_search_url']
    r = requests.get(youtube_search_url, params=params)
    return r.json()
