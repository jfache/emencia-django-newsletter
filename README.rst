=========================
Emencia Django Newsletter
=========================

The problematic was :

 *How to couple a contact base to a mailing list and sending newsletters throught Django ?*

Imagine that we have an application containing some kind of profiles or something like the **django.contrib.auth** and you want to send newsletters to them and tracking the activity.

.. contents::

Features
========

More than a long speech, here the list of the main features :

  * Coupling capacities with another django model.
  * Variables can be used in the newsletter's templates.
  * Mailing list managements (merging, importing...).
  * Import/Export of the contact in VCard 3.0.
  * Configurable SMTP servers with flow limit management.
  * Working groups.
  * Can send newsletter previews.
  * Unsubscriptions to mailing list.
  * Unique urls for an user.
  * Tracking statistics.


Architecture
============

At the level of the application architecture, we can see 2 originalities who need to be explained.

Content types
-------------

The **content types** application is used to link any *Contact* model instance to another model instance. 
This allow you to create different kinds of contact linked to differents application, and retrieve the association at anytime.

This is particulary usefull with the templates variables if certain informations are located in the model instance linked.

Cronjob/Command
---------------

The emencia.django.newsletter application will never send the newsletters registered in the site until you launch the **send_newsletter** command. ::

  $> python manage.py send_newsletter

This command will launch the newsletters who need to be launched accordingly to the credits of the SMTP server of the newsletter. 
That's mean that not all newsletters will be expedied at the end of the command because if you use a public SMTP server you can be banished temporarly if you reach the sending limit.
To avoid banishment all the newsletters are not sended in the same time and immediately.

So it is recommanded to create a **cronjob** for launching this command every hours for example.

Installation
============

You could retrieve the last sources from http://github.com/Fantomas42/emencia-django-newsletter and running the installation script ::
    
  $> python setup.py install

or use pip ::

  $> pip install -e git://github.com/Fantomas42/emencia-django-newsletter.git#egg=emencia.django.newsletter

For the latest stable version use easy_install ::

  $> easy_install emencia.django.newsletter

Applications
------------

Then register **emencia.django.newsletter**, **admin**, **contenttypes** and **tagging** in the INSTALLED_APPS section of your project's settings. ::

  >>> INSTALLED_APPS = (
  ...   # Your favorites apps
  ...   'django.contrib.contenttypes',
  ...   'django.contrib.admin',
  ...   'tagging',
  ...   'emencia.django.newsletter',)


Template Context Processors
---------------------------

Add these following template context processors if not already present. ::

  >>> TEMPLATE_CONTEXT_PROCESSORS = (
  ...      'django.core.context_processors.auth',
  ...      'django.core.context_processors.i18n',
  ...      'django.core.context_processors.request',
  ...      'django.core.context_processors.media',
  ...      'emencia.django.newsletter.context_processors.media',
  ...	)

Urls
----

In your project urls.py adding this following line to include the newsletter's urls for serving the newsletters in HTML. ::

  >>> url(r'^newsletters/', include('emencia.django.newsletter.urls')),

Note this urlset is provided for convenient usage, but you can do something like that if you want to customize your urls : ::

  >>> url(r'^newsletters/', include('emencia.django.newsletter.urls.newsletter')),
  >>> url(r'^mailing/', include('emencia.django.newsletter.urls.mailing_list')),
  >>> url(r'^tracking/', include('emencia.django.newsletter.urls.tracking')),
  >>> url(r'^statistics/', include('emencia.django.newsletter.urls.statistics')),

Media Files
-----------

You have to make a symbolic link from emencia/django/newsletter/media/ directory to your media directory or make a copy named **edn**,
but if want to change this value, define NEWSLETTER_MEDIA_URL in the settings.py as appropriate.

Don't forget to serve this url.

Synchronization
---------------

Now you can run a *syncdb* for installing the models into your database.


DBMS considerations
===================

It's not recommended to use SQLite for production use. Because is limited to 999
variables into a SQL query, you can not create a Mailing List greater than this limitations
in the Django's admin modules. Prefer MySQL ou PgSQL.


HOWTO couple your profile application with emencia.django.newsletter
====================================================================

If you wan to quickly import your contacts into a mailing list for example, 
you can write an admin's action for your model.

We suppose that we have the fields *email*, *first_name* and *last_name* in a models name **Profile**.

In his AdminModel definition add this method and register it into the *actions* property. ::

  >>> class ProfileAdmin(admin.ModelAdmin):
  ...
  ...   def make_mailing_list(self, request, queryset):
  ...     from emencia.django.newsletter.models import Contact
  ...     from emencia.django.newsletter.models import MailingList
  ...
  ...     subscribers = []
  ...     for profile in queryset:
  ...       contact, created = Contact.objects.get_or_create(email=profile.mail,
  ...                                                        defaults={'first_name': profile.first_name,
  ...                                                                  'last_name': profile.last_name,
  ...                                                                  'content_object': profile})
  ...     subscribers.append(contact)
  ...     new_mailing = MailingList(name='New mailing list',
  ...                               description='New mailing list created from admin/profile')
  ...     new_mailing.save()
  ...     new_mailing.subscribers.add(*subscribers)
  ...     new_mailing.save()
  ...     self.message_user(request, '%s succesfully created.' % new_mailing)
  ...   make_mailing_list.short_description = 'Create a mailing list'
  ...
  ...   actions = ['make_mailing_list',]

This action will create or retrieve all the **Contact** instances needed for the mailing list creation.

After this you can send a newsletter to this mailing list.

Database Representation
=======================

.. image:: http://github.com/Fantomas42/emencia-django-newsletter/raw/master/docs/graph_model.png
  

