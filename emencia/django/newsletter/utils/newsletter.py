"""Utils for newsletter"""
import urllib2

from BeautifulSoup import BeautifulSoup, Tag
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from emencia.django.newsletter.models import Link
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import MailingList

def get_webpage_content(url):
    """Return the content of the website
    located in the body markup"""
    request = urllib2.Request(url)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)

    return soup.body.prettify()

def body_insertion(content, insertion, end=False):
    """Insert an HTML content into the body HTML node"""
    if not content.startswith('<body'):
        content = '<body>%s</body>' % content
    soup = BeautifulSoup(content)

    if end:
        soup.body.append(insertion)
    else:
        soup.body.insert(0, insertion)
    return soup.prettify()

def track_links(content, context):
    """Convert all links in the template for the user
    to track his navigation"""
    if not context.get('uidb36'):
        return content

    soup = BeautifulSoup(content)
    for link_markup in soup('a'):
        if link_markup.get('href'):
            link_href = link_markup['href']
            link_title = link_markup.get('title', link_href)
            link, created = Link.objects.get_or_create(url=link_href,
                                                       defaults={'title': link_title})
            link_markup['href'] = 'http://%s%s' % (context['domain'], reverse('newsletter_newsletter_tracking_link',
                                                                              args=[context['newsletter'].slug,
                                                                                    context['uidb36'], context['token'],
                                                                                    link.pk]))
    return soup.prettify()
    
def get_recipients_list(newsletter, mailing_list_pk=None):
    """Returns the recipient list of a newsletter
    depending on the mailing list"""
    if mailing_list_pk:
        mailing_list = get_object_or_404(MailingList, pk=mailing_list_pk)
        recipients_list = mailing_list.recipients()
    else:
        recipients_list = newsletter.recipients()
        
    return recipients_list

