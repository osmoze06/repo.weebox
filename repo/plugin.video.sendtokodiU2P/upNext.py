import xbmc

def upnext_signal(sender, next_info):
    """Send a signal to Kodi using JSON RPC"""
    from base64 import b64encode
    from json import dumps
    from upNext import notify, to_unicode
    data = [to_unicode(b64encode(dumps(next_info).encode()))]
    return notify(sender=sender + '.SIGNAL', message='upnext_data', data=data)

def notify(sender, message, data):
    """Send a notification to Kodi using JSON RPC"""
    result = jsonrpc(method='JSONRPC.NotifyAll', params=dict(
        sender=sender,
        message=message,
        data=data,
    ))
    if result.get('result') != 'OK':
        xbmc.log('Failed to send notification: ' + result.get('error').get('message'), 4)
        return False
    return True

def jsonrpc(**kwargs):
    """Perform JSONRPC calls"""
    from json import dumps, loads
    if kwargs.get('id') is None:
        kwargs.update(id=0)
    if kwargs.get('jsonrpc') is None:
        kwargs.update(jsonrpc='2.0')
    return loads(xbmc.executeJSONRPC(dumps(kwargs)))

def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text










"""
next_info = dict(
    current_episode=dict(
        episodeid=item_details.id,
        tvshowid=item_details.series_id,
        title=item_details.name,
        art={
            'thumb': item_details.art.get('thumb', ''),
            'tvshow.clearart': item_details.art.get('tvshow.clearart', ''),
            'tvshow.clearlogo': item_details.art.get('tvshow.clearlogo', ''),
            'tvshow.fanart': item_details.art.get('tvshow.fanart', ''),
            'tvshow.landscape': item_details.art.get('tvshow.landscape', ''),
            'tvshow.poster': item_details.art.get('tvshow.poster', ''),
        },
        season=item_details.season_number,
        episode=item_details.episode_number,
        showtitle=item_details.series_name,
        plot=item_details.plot,
        playcount=item_details.play_count,
        rating=item_details.critic_rating,
        firstaired=item_details.year,
        runtime=item_details.runtime,  # NOTE: This is optional
    ),
    next_episode=dict(
        episodeid=next_item_details.id,
        tvshowid=next_item_details.series_name,
        title=next_item_details.name,
        art={
            'thumb': next_item_details.art.get('thumb', ''),
            'tvshow.clearart': next_item_details.art.get('tvshow.clearart', ''),
            'tvshow.clearlogo': next_item_details.art.get('tvshow.clearlogo', ''),
            'tvshow.fanart': next_item_details.art.get('tvshow.fanart', ''),
            'tvshow.landscape:': next_item_details.art.get('tvshow.landscape', ''),
            'tvshow.poster': next_item_details.art.get('tvshow.poster', ''),
        },
        season=next_item_details.season_number,
        episode=next_item_details.episode_number,
        showtitle=next_item_details.series_name,
        plot=next_item_details.plot,
        playcount=next_item_details.play_count,
        rating=next_item_details.critic_rating,
        firstaired=next_item_details.year,
        runtime=next_item_details.runtime,  # NOTE: This is optional
    ),
    # NOTE: You need to provide either `play_info` or `play_url`
    play_url='plugin://plugin.video.foobar/play_item/' + item_id,
#    play_info=dict(
#        item_id=next_item_details.id,
#    ),
    notification_time=notification_time,  # NOTE: This is optional
#    notification_offset=notification_offset,
)
"""