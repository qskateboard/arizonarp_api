#
# Created by pSkateboard (Lee_Dohyeon)
#

import re
import requests
import bs4


headers = {}
session = requests.session()


def setup(user_agent, cookie):
    global headers
    headers = {
        "user-agent": user_agent,
        "cookie": cookie
    }
    session.headers = headers

def get_categories(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    result = []
    for category in soup.find_all('div', re.compile('.*node--depth2 node--forum.*')):
        result.append({
            "name": category.find("a").text,
            "link": "https://forum.arizona-rp.com" + category.find("a")['href'],
        })
    return result


def get_category(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    return soup.find("h1", re.compile("p-title-value")).text


def get_threads(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    result = []
    for thread in soup.find_all('div', re.compile('structItem structItem--thread.*')):
        link = object
        unread = False
        closed = False
        pinned = False
        title_element = thread.find_all('div', "structItem-title")[0]
        for el in title_element.find_all("a"):
            if "threads" in el['href']:
                link = el

        if "structItem-status structItem-status--locked" in str(thread):
            closed = True
        if "structItem-status structItem-status--sticky" in str(thread):
            pinned = True
        if "unread" in link['href']:
            unread = True

        creator = thread.find('a').text
        try:
            creator = thread.find('img')['alt']
        except:
            pass

        result.append({
            "title": link.text,
            "link": "https://forum.arizona-rp.com" + link['href'].replace("unread", ""),
            "creator": creator,
            "latest": thread.find('div', re.compile('structItem-cell structItem-cell--latest')).find_all("a")[1].text,
            "closed_date": thread.find('time', re.compile('structItem-latestDate u-dt'))['data-time'],
            "unread": unread,
            "pinned": pinned,
            "closed": closed,
        })
    return result


def get_post(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    post_id = str(int(url.split("post-")[1]))

    message = soup.find_all("article", {"id": "js-post-" + post_id})[0]

    q = session.get(f"https://forum.arizona-rp.com/posts/{post_id}/edit")
    soup2 = bs4.BeautifulSoup(q.text, "lxml")
    result = {
        "post_id": post_id,
        "author": message['data-author'],
        "timestamp": message.find("time", "u-dt")['data-time'],
        "content": soup2.find("textarea", {"name": "message"}).text,
        "content_html": soup2.find("textarea", {"name": "message_html"}).text,
    }
    return result


def edit_post(uid, html):
    r = session.get(f"https://forum.arizona-rp.com/posts/{uid}/edit")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[6]
    body = {
        "message_html": html,
        "message": html,
        "_xfToken": token,
    }
    session.post(f"https://forum.arizona-rp.com/posts/{uid}/edit", body)


def set_unread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[6]
    session.post(url, data={"_xfToken": token})


def send_message(url, message):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    form = soup.find_all("form")[6]

    action = "https://forum.arizona-rp.com" + form['action']
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[6]
    json = {
        "message": message,
        "_xfToken": token,
        "last_date": form.find_all("input", {"name": "last_date"})[0]['value'],
        "last_known_date": form.find_all("input", {"name": "last_known_date"})[0]['value'],
    }
    session.post(action, data=json)


def get_thread(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")

    title = soup.find("h1", re.compile("p-title-value")).text
    post = soup.find_all('article', re.compile('message-threadStarterPost'))[0]
    return [title, post.find("div", "bbWrapper").text]


def close_thread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[1]
    query = {
        "_xfRequestUri": str(url).replace("https://forum.arizona-rp.com", ""),
        "_xfWithData": 1,
        "_xfToken": token,
        "_xfResponseType": "json",
    }
    r = session.post(url + "quick-close", data=query)


def pin_thread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[1]
    query = {
        "_xfRequestUri": str(url).replace("https://forum.arizona-rp.com", ""),
        "_xfWithData": 1,
        "_xfToken": token,
        "_xfResponseType": "json",
    }
    r = session.post(url + "quick-stick", data=query)


def make_reaction(link, uid):
    reacted = False
    if "post-" in link:
        link = link.split("post-")[1].replace("/", "")
        try:
            uri = "https://forum.arizona-rp.com/posts/{}/react".format(link)
            q = session.get("https://forum.arizona-rp.com/posts/" + link + "/react?reaction_id=" + str(uid))
            if "Вы действительно хотите оставить эту реакцию?" in q.text:
                token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(q.text)[6]
                session.post(uri, data={"reaction_id": uid, "_xfToken": token})
                reacted = True
        except:
            print("[-] Произошла ошибка при установке реакции")
    else:
        if "https://forum.arizona-rp.com/threads/" in link:
            try:
                q = session.get(link)
                soup = bs4.BeautifulSoup(q.text, "lxml")
                for post in soup.findAll('article', {'class': 'message'}):
                    hrefs = post.findAll('a')
                    for a in hrefs:
                        if "/post-" in a['href']:
                            number = a['href'].split("post-")[1].replace("/", "")
                            uri = "https://forum.arizona-rp.com/posts/{}/react".format(str(number))
                            q = session.get("https://forum.arizona-rp.com/posts/" + number + "/react?reaction_id=" + str(uid))
                            if "Вы действительно хотите оставить эту реакцию?" in q.text:
                                token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(q.text)[6]
                                session.post(uri, data={"reaction_id": uid, "_xfToken": token})
                                reacted = True
                            break
                        if reacted:
                            break
                    if reacted:
                        break
            except:
                print("[-] Произошла ошибка при установке реакции")
    return reacted
