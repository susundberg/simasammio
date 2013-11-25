
from google.appengine.ext import db
from google.appengine.ext import blobstore

#####################################################################
#
#####################################################################
class TableComments(db.Model):
   date      = db.DateTimeProperty(auto_now_add=True)
   author    = db.StringProperty()
   message   = db.TextProperty()
   
class TableProvider(db.Model):
   name        = db.StringProperty()
   desc        = db.TextProperty()
   blob_key    = blobstore.BlobReferenceProperty()
   valid_from  = db.DateTimeProperty(auto_now_add=False)
   valid_to    = db.DateTimeProperty(auto_now_add=False)
   status      = db.StringProperty()
   last_update = db.DateTimeProperty(auto_now=True)

class TableImagesInfo(db.Model):
   date      = db.DateTimeProperty(auto_now_add=True)
   blob_key  = blobstore.BlobReferenceProperty()
   location  = db.GeoPtProperty()
   author    = db.ReferenceProperty(TableProvider)

class TableProviderUpdates(db.Model):
   location  = db.GeoPtProperty()
   date      = db.DateTimeProperty(auto_now_add=True)
  



