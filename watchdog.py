from models import sqlalchemy_
from pprintpp import pprint as pp
import time
import datetime
import json
from bson import json_util
#time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
alchemy = sqlalchemy_()
now = time.time()

def poplulate_attachment(board, color):

    tmp = {
               "fallback": "Required plain-text summary of the attachment.",
               "color": color,
               # "pretext": "Optional text that appears above the attachment block",
               "author_name": "",
               "author_link": "http://flickr.com/bobby/",
               "author_icon": "http://www.ebcbuzz.com/images/logo.png",
               "title": board["board"],
               "title_link": board["link"],
               "text": "board crawler seems not working",
               # "image_url": "http://my-website.com/path/to/image.jpg",
               "fields": [
                   {"title": "last board check time", "value": board["board_crawler_last_check_time"] ,  "short": True},
                   {"title": "last article check time", "value": board["article_crawler_last_check_time"], "short": True},
                   {"title": "last article time", "value": board["last_article_time"], "short": True},
                   {"title": "error count", "value": board["error_count"], "short": True}
               ]
           }
    return tmp

def make_order(board, msg):
    url = "https://hooks.slack.com/services/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"
    color = "warning"
    attachments = []
    attachments.append(poplulate_attachment(board, color))
    data = {"channel": "#crawler",
            "attachments": attachments}
    data["username"] = "Crawler Watch Dog "
    data["text"] = msg
    data["markdwn"] = True
    data["icon_emoji"] = ":chart_with_upwards_trend:"

    data2 = json.dumps(data, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=False, separators=None, encoding="utf-8", sort_keys=False, default=json_util.default)
    import subprocess
    cmd = "curl  -X POST --data-urlencode 'payload=%s' %s" % (str(data2), url)
    pingPopen = subprocess.Popen(args=cmd, shell=True)


if __name__ == '__main__':

    board_threshold = 1200
    article_threshold = 1.3
    boards = alchemy.get_boards_statistics("")
    for board in boards:
        try:
            #if board['error'] > 0:
            # sent notify and clear record 
            for _k in ['board_crawler_last_check_time', 
                       'article_crawler_last_check_time', 
                       'last_article_time']:
                _ = time.mktime(datetime.datetime.strptime(board[_k], "%Y-%m-%d %H:%M:%S").timetuple())

                if _k == "board_crawler_last_check_time":
                    if now - _ > board_threshold: 
                        print "send warning to slack"
                        msg = "[WARN] Board Crawler Check Timeout(%s s)" % board_threshold
                        board[_k] = board[_k] + "( +" + str(int(now - _ - board_threshold)) + "s)"
                        make_order(board, msg)
                        send = True
                """
                if _k == "article_crawler_last_check_time":
                TO-DO: Compare w/ avg duration of posts, and issue alert if exceed expected time
                avg_duration = xxx
                if (now - _) > avg_duration*1.3:
                    send warning

                if _k == 'article_crawler_last_check_time':
                """
                # print now, _k,  _, (_ - now)
        except Exception as e:
            print e
            print "!!!!!!", board["board"].encode("utf-8")
            pass

