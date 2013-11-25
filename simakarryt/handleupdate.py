from __future__ import with_statement
from google.appengine.api import files

import webapp2
import os
import json
from google.appengine.ext import db
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import handlecommon
import handlecomment
import datatables

def get_long_lat_from_post(self):
   prov_lat_string = self.request.get('lat')
   prov_lon_string = self.request.get('long')
   
   if prov_lat_string != "" and prov_lon_string != "" :
      try:
         prov_lat = float( prov_lat_string )
         prov_lon = float( prov_lon_string )
         return (True, db.GeoPt( lat = prov_lat, lon=prov_lon ) )
      except ValueError:
         # This is not ok, bad update
         handlecommon.print_error( self, 400, "Invalid update param (float)");
         return (False, None)
      except db.BadValueError:
         handlecommon.print_error( self, 400, "Invalid update param (lonlat)");
         return (False, None)
         
         return (False, None)
   return (True, None)



#####################################################################################################
class HandleUpdate( webapp2.RequestHandler ):
   
   def get(self):
      (provider_key, provider)  = handlecommon.check_and_get_provider(self, 'id', None );
      
      if provider_key == None:
         return
      
      update_query = datatables.TableProviderUpdates.all().ancestor(
                           provider_key ).order('-date')
      
      update_list = update_query.fetch(100)
        
      if ( self.request.get('json') ):
         json_list = []
         for update in update_list:
            json_list.append( handlecommon.to_dict(update) )
         self.response.write( json.dumps( json_list ) )
      else:
         template        = JINJA_ENVIRONMENT.get_template('html/update.html')
         template_values = { 'id'    : str(provider_key), 
                             'update_list'  : update_list,
                             'provider' : provider }
         self.response.write(template.render( template_values ) )
                                               
   def post(self):
      (provider_key, provider)  = handlecommon.check_and_get_provider(self, 'id', None );
      
      if provider_key == None:
         return
      
      ( everything_ok, new_location ) = get_long_lat_from_post( self )
      
      if everything_ok == False:
         return
      
      if new_location != None:
         try:
            update          = datatables.TableProviderUpdates( parent = provider_key )
            update.location = new_location
            update.put()
         except BadValueError:
            handlecommon.print_error( self, 500, "Update write failed")

      # Anyway we need to update provider updated issue
      status = self.request.get('status')
     
      if status != "" :
        provider.status = status
      
      # Update anyway, to get the last_update field proper
      try:
         provider.put()
      except BadValueError:
        handlecommon.print_error( self, 500, "Update provider write failed");
        return
      
      if  self.request.get('json'):
          self.redirect("/comment?json=1&thread_id=" + str(provider_key) 
                         + "&comments="+self.request.get('comments')
                         + "&comments_offset=" + self.request.get('comments_offset') )
          return
      else:
          self.get()

#####################################################################################################



class HandleUploadImage( webapp2.RequestHandler ):
   def get(self):
     (provider_key, provider)  = handlecommon.check_and_get_provider(self, 'id', None );
     if provider_key == None:
        return
      
     if ( self.request.get('json') ):
         self.response.write( json.dumps( { 'status' : 'OK' } ) )
     else:
         template        = JINJA_ENVIRONMENT.get_template('html/upload_image.html')
         template_values = { 'id'    : str(provider_key) }
         self.response.write(template.render( template_values ) )
         
   def post(self):
      
     (provider_key, provider)  = handlecommon.check_and_get_provider(self, 'id', None )
     
     if provider_key == None:
        return
     
     ( everything_ok, image_location ) = get_long_lat_from_post( self )
     
     if everything_ok == False:
         return
 
     image_data =  self.request.get('file') 
     
     if len ( image_data ) < 1024 :
        handlecommon.print_error( self, 400, "Invalid image");
        return
      
     
     file_name = files.blobstore.create(mime_type='application/octet-stream')
     with files.open(file_name, 'a') as f:
       f.write(image_data)
     files.finalize(file_name)
     
     
     blob_key  = files.blobstore.get_blob_key(file_name)
     
     new_image    = datatables.TableImagesInfo( author   = provider ,
                                                blob_key = blob_key,
                                                location = image_location )
     new_image.put()
     
     if self.request.get('json'):
        self.response.write( json.dumps( { 'image_id' : "%s" % new_image.key() } ) )
     else:
        self.redirect("/")
   




