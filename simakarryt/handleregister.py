


import webapp2
import os
import jinja2
import json
from google.appengine.ext import db

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import datatables
import handlecommon
import datetime

def get_datetime_from_post(self, string ):
   try:
      if ( string == "" ):
         return None
      return datetime.datetime.strptime(string,"%Y-%m-%d %H%M")
   except ValueError:
      # Fixme error exit?
      return None

class HandleRegister( webapp2.RequestHandler ):
   def get(self):
      template = JINJA_ENVIRONMENT.get_template('html/register.html')
      self.response.write(template.render())
   
   def post(self):
      secret     = self.request.get('secret')
      if ( secret != 'kisumirri' ):
         handlecommon.print_error( self, 400, "Bad request")
         return
      
      requested_name = self.request.get('name')
      
      name_query = db.Query( datatables.TableProvider,  keys_only=True )
      name_query.filter('name =', requested_name )
      result = name_query.get()
      
      if ( result != None ):
         handlecommon.print_error( self, 403, "Bad name request")
         return
       
      provider = datatables.TableProvider( )
      
      provider.name       = requested_name
      provider.desc       = self.request.get('description')
      provider.valid_from = get_datetime_from_post( self, self.request.get('valid_from') )
      provider.valid_to   = get_datetime_from_post( self, self.request.get('valid_to') )
      
      try:
         provider.put()
         if  self.request.get('json') :
            json_out = { 'id' : "%s" % provider.key() }
            self.response.write( json.dumps( json_out ) )
         else:
            self.redirect("/")
      except:
         handlecommon.print_error( self, 500, "Write failed")


class HandleRegisterUpdate( webapp2.RequestHandler ):
   def get(self):
      
      ( provider_key, provider ) = handlecommon.check_and_get_provider( self, 'id', None );
      if provider_key == None: 
         return
      if self.request.get('json') :
        dict_object = handlecommon.to_dict( provider );
        dict_object["description"] = dict_object["desc"] ;
        dict_object["desc"] = None;
        self.response.write( json.dumps ( dict_object ) )
      else: 
         template = JINJA_ENVIRONMENT.get_template('html/register_update.html')
         self.response.write(template.render({ 'id' : str(provider_key) ,
                                            'provider' : provider } ) )
      
      
      
   def post(self):
      ( provider_key, provider ) = handlecommon.check_and_get_provider( self, 'id', None );
      if provider_key == None: 
         return
      
      if ( self.request.get('description') ):
         provider.desc       = self.request.get('description')

      if ( self.request.get('valid_from') ):         
         provider.valid_from = get_datetime_from_post( self, self.request.get('valid_from') )
      
      if ( self.request.get('valid_to') ):
         provider.valid_to   = get_datetime_from_post( self, self.request.get('valid_to') )
      
      try:
         provider.put()
         if  self.request.get('json') :
            json_out = { 'id' : "%s" % provider.key() }
            self.response.write( json.dumps( json_out ) )
         else:
            self.redirect("/")
      except:
         handlecommon.print_error( self, 500, "Write failed")













