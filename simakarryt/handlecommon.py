
import datetime
import time
import webapp2
from google.appengine.ext import db

import datatables

#############################################################################
#
#############################################################################

def print_error(self, code, message ):
   self.response.set_status( code=code, message=message ) 
   self.response.write("Error code %d: " % code + message )
   
#############################################################################
#
#############################################################################
def check_and_get_provider( self, id_name, accept_extra_key ):
   provider_id  = self.request.get(id_name)

   if len( provider_id ) < 3:
      print_error(self, 400, "No id provided" )
      return (None, None)

   provider     = None
   
   try:
      provider     = datatables.TableProvider.get(provider_id)
   except:
      print_error(self, 400, "No valid id found" )
      return (None, None)

   if provider == None:
      if accept_extra_key  != None:
         parent_key = accept_extra_key
         
         if provider_id == str(parent_key):
            return ( parent_key, provider )
         
      print_error(self, 500, "No valid id provided" )
      return (None, None)

   return ( provider.key() , provider)


SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            
            
            output[key] = value.strftime("%Y-%m-%d %H%M")
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    return output
 
 
 