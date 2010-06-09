"""Views for emencia.django.newsletter Mailing List"""
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import ContactMailingStatus


def view_mailinglist_unsubscribe(request, slug, uidb36, token):
    """Unsubscribe a contact to a mailing list"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    
    unsubscribers = Contact.objects.none()
    for mailing_list in newsletter.mailing_lists.all():
        unsubscribers |= mailing_list.unsubscribers.all()
    
    already_unsubscribed = contact in unsubscribers

    if request.POST.get('email') and not already_unsubscribed:
        for mailing_list in newsletter.mailing_lists.all():
            if contact in mailing_list.subscribers.all():
                mailing_list.unsubscribers.add(contact)
                mailing_list.save()

        already_unsubscribed = True
        log = ContactMailingStatus.objects.create(newsletter=newsletter, contact=contact,
                                                  status=ContactMailingStatus.UNSUBSCRIPTION)

    return render_to_response('newsletter/mailing_list_unsubscribe.html',
                              {'email': contact.email,
                               'already_unsubscribed': already_unsubscribed},
                              context_instance=RequestContext(request))

