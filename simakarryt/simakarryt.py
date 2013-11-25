# directly write blobs
from __future__ import with_statement
from google.appengine.api import files

import cgi
import datetime
import urllib
import webapp2

import os
import urllib
import json


from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from google.appengine.api import urlfetch


from datetime import datetime

# Local files
import datatables
import handlecomment
import handleupdate
import handleregister

import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


###############################################################################################
# Main page
###############################################################################################
class MainPage(webapp2.RequestHandler):
   def get(self):

      provider_query = datatables.TableProvider.all().order('-last_update')
      provider_list = provider_query.fetch(100)
      
      comments_parent = handlecomment.get_mainpage_comment_key()
      comments_query = datatables.TableComments.all().ancestor( comments_parent ).order('-date')
      comment_list = comments_query.fetch(100)

      
      images_query = datatables.TableImagesInfo.all().order('-date')
      images_list = images_query.fetch(100)
      
      image_show_list = []
      
      
      for image in images_list:
         try:
            blob_info = image.blob_key
            image_info = { 
               'date'      : image.date,
               'url'       : get_serving_url( blob_info ),
               'author'    : str( image.author.key() ) ,
               'thread_id' : str( image.key() ),
               'location'  : image.location
               }
            image_show_list.append( image_info )
         except :
            print "Invalid image file found: " + str( blob_info.key() )
      
      date_now = datetime.now()
      
      for provider in provider_list:
         updates_query          = datatables.TableProviderUpdates.all().ancestor( provider.key() ).order('-date')
         provider.updates_list  = updates_query.fetch(32);
         provider.updates_last  = None
         if len( provider.updates_list ) >= 1 :
            provider.updates_last  = provider.updates_list.pop(0);
         provider.open_now  = True
         
         if ( provider.valid_from and provider.valid_from > date_now ):
            provider.open_now  = False  
            
         if ( provider.valid_to and provider.valid_to < date_now ):
            provider.open_now  = False
 
      template_values = {
         'provider_list'       : provider_list   ,
         'comment_list'        : comment_list    ,
         'image_list'          : image_show_list , 
         'comment_thread_id'   : comments_parent 
         }
      
      if self.request.get('debug'):
         template = JINJA_ENVIRONMENT.get_template('html/debug.html')
      else:
         template = JINJA_ENVIRONMENT.get_template('html/index.html')
         
      self.response.write(template.render(template_values))

########################################################################################
#
########################################################################################

###############################################################################################
# MAIN PROVIDER
###############################################################################################

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/register',handleregister.HandleRegister ),
                               ('/register_update',handleregister.HandleRegisterUpdate ),
                               ('/comment', handlecomment.HandleComment ),
                               ('/update', handleupdate.HandleUpdate ) , 
                               ('/upload_image', handleupdate.HandleUploadImage ),
                               ],
                                  debug=True)

