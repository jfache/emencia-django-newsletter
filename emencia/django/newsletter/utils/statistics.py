"""Statistics for emencia.django.newsletter"""
from django.db.models import Q

from emencia.django.newsletter.utils.newsletter import get_recipients_list

from emencia.django.newsletter.models import ContactMailingStatus as Status
from emencia.django.newsletter.models import MailingList

def get_newsletter_opening_statistics(status, recipients):
    """Return opening statistics of a newsletter based on status"""
    openings = status.filter(Q(status=Status.OPENED) | Q(status=Status.OPENED_ON_SITE))

    openings_by_links_opened = len(set(status.filter(status=Status.LINK_OPENED).exclude(
        contact__in=openings.values_list('contact', flat=True)).values_list('contact', flat=True)))
    
    total_openings = openings.count() + openings_by_links_opened
    if total_openings:
        unique_openings = len(set(openings.values_list('contact', flat=True))) + openings_by_links_opened
        unique_openings_percent = float(unique_openings) / float(recipients) * 100
        unknow_openings = recipients - unique_openings
        unknow_openings_percent = float(unknow_openings) / float(recipients) * 100
        opening_average = float(total_openings) / float(unique_openings)
    else:
        unique_openings = unique_openings_percent = unknow_openings = \
                          unknow_openings_percent = opening_average = 0

    return {'total_openings': total_openings,
            'double_openings': total_openings - unique_openings,
            'unique_openings': unique_openings,
            'unique_openings_percent': unique_openings_percent,
            'unknow_openings': unknow_openings,
            'unknow_openings_percent': unknow_openings_percent,
            'opening_average': opening_average,
            'opening_deducted': openings_by_links_opened}

def get_newsletter_on_site_opening_statistics(status):
    """Return on site opening statistics of a newsletter based on status"""
    on_site_openings = status.filter(status=Status.OPENED_ON_SITE)
    total_on_site_openings = on_site_openings.count()
    unique_on_site_openings = len(set(on_site_openings.values_list('contact', flat=True)))

    return {'total_on_site_openings': total_on_site_openings,
            'unique_on_site_openings': unique_on_site_openings}


def get_newsletter_clicked_link_statistics(status, recipients, openings):
    """Return clicked link statistics of a newsletter based on status"""
    clicked_links = status.filter(status=Status.LINK_OPENED)

    total_clicked_links = clicked_links.count()
    total_clicked_links_percent = float(total_clicked_links) / float(recipients) * 100

    unique_clicked_links = len(set(clicked_links.values_list('contact', flat=True)))
    unique_clicked_links_percent = float(unique_clicked_links) / float(recipients) * 100

    double_clicked_links = total_clicked_links - unique_clicked_links
    double_clicked_links_percent = float(double_clicked_links) / float(recipients) * 100

    clicked_links_by_openings = openings and float(total_clicked_links) / float(openings) * 100 or 0.0

    clicked_links_average = total_clicked_links and float(total_clicked_links) / float(unique_clicked_links) or 0.0

    return {'total_clicked_links': total_clicked_links,
            'total_clicked_links_percent': total_clicked_links_percent,
            'double_clicked_links': double_clicked_links,
            'double_clicked_links_percent': double_clicked_links_percent,
            'unique_clicked_links': unique_clicked_links,
            'unique_clicked_links_percent': unique_clicked_links_percent,
            'clicked_links_by_openings': clicked_links_by_openings,
            'clicked_links_average': clicked_links_average}

def get_newsletter_unsubscription_statistics(status, recipients):
    unsubscriptions = status.filter(status=Status.UNSUBSCRIPTION)

    #Patch: multiple unsubsriptions logs could exist before a typo bug was corrected, a 'set' is needed
    total_unsubscriptions = len(set(unsubscriptions.values_list('contact', flat=True)))
    total_unsubscriptions_percent = float(total_unsubscriptions) / float(recipients) * 100

    return {'total_unsubscriptions': total_unsubscriptions,
            'total_unsubscriptions_percent': total_unsubscriptions_percent}

def get_newsletter_top_links(status):
    """Return the most clicked links"""
    links = {}
    clicked_links = status.filter(status=Status.LINK_OPENED)
    
    for cl in clicked_links:
        links.setdefault(cl.link, 0)
        links[cl.link] += 1

    top_links = []
    for link, score in sorted(links.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        unique_clicks = len(set(clicked_links.filter(link=link).values_list('contact', flat=True)))
        top_links.append({'link': link,
                          'total_clicks': score,
                          'unique_clicks': unique_clicks})
        
    return {'top_links': top_links}

def get_newsletter_statistics(newsletter, mailing_list_pk=None):
    """Return the statistics of a newsletter"""
    recipients_list = get_recipients_list(newsletter, mailing_list_pk)
    recipients = recipients_list.count()
    
    newsletter_status = Status.objects.filter(newsletter=newsletter)
    recipients_status = newsletter_status.filter(creation_date__gte=newsletter.sending_date, contact__in=recipients_list)    
    mails_sent = recipients_status.filter(status=Status.SENT).count()
    if mails_sent > recipients:
        recipients = mails_sent
    remaining_mails = recipients - mails_sent

    statistics = {'tests_sent': newsletter_status.filter(status=Status.SENT_TEST).count(),
                  'mails_sent': mails_sent,
                  'mails_to_send': recipients,
                  'remaining_mails': recipients - mails_sent}

    statistics.update(get_newsletter_opening_statistics(recipients_status, recipients))
    statistics.update(get_newsletter_on_site_opening_statistics(recipients_status))
    statistics.update(get_newsletter_unsubscription_statistics(recipients_status, recipients))
    statistics.update(get_newsletter_clicked_link_statistics(recipients_status, recipients,
                                                             statistics['total_openings']))
    statistics.update(get_newsletter_top_links(recipients_status))

    return statistics


