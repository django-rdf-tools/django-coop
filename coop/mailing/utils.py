# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc
from django.core.mail import get_connection, EmailMultiAlternatives
from coop_cms.html2text import html2text
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()


# copied from http://stackoverflow.com/a/3987802/117092
def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        print_exc(file=stderr)
        return text
    
def make_links_absolute(html_content):
    """replace all local url with absolute url"""
    import re
    #regex = """<.*(?P<tag>href|src)\s*=\s*["'](?P<url>.+?)["'].*>"""
    #regex = """<.*href|src\s*=\s*["'](?P<url>.+?)["'].*>"""
    
    def make_abs(match):
        #Thank you : http://www.gawel.org/howtos/python-re-sub
        start = match.group('start')
        url = match.group('url')
        if url.startswith('..'):
            url = url[2:]
        while url.startswith('/..'):
            url = url[3:]
        if url.startswith('/'):
            url = '%s%s' % (settings.COOP_CMS_SITE_PREFIX, url)
        end = match.group('end')
        return start + url + end
    
    a_pattern = re.compile(r'(?P<start>.*?href=")(?P<url>\S+)(?P<end>".*?)')
    html_content = a_pattern.sub(make_abs, html_content)
    
    img_pattern = re.compile(r'(?P<start>.*?src=")(?P<url>\S+)(?P<end>".*?)')
    html_content = img_pattern.sub(make_abs, html_content)

    return html_content
    
def send_newsletter(newsletter, dests):

    t = get_template(newsletter.get_template_name())
    context_dict = {
        'title': newsletter.subject, 'newsletter': newsletter, 'by_email': True,
        'SITE_PREFIX': settings.COOP_CMS_SITE_PREFIX,
        'MEDIA_URL': settings.MEDIA_URL, 'STATIC_URL': settings.STATIC_URL,
    }
    html_text = t.render(Context(context_dict))
    html_text = make_links_absolute(html_text)

    emails = []
    connection = get_connection()
    from_email = settings.COOP_CMS_FROM_EMAIL
    reply_to = getattr(settings, 'COOP_CMS_REPLY_TO', None)
    headers = {'Reply-To': reply_to} if reply_to else None

    for addr in dests:
        text = html2text(html_text)
        email = EmailMultiAlternatives(newsletter.subject, text, from_email, [addr], headers=headers)
        email.attach_alternative(html_text, "text/html")
        emails.append(email)
    return connection.send_messages(emails)

    