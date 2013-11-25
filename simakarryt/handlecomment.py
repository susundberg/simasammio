
import webapp2
import os

from google.appengine.ext import db
from google.appengine.api.images import get_serving_url

import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import datatables
import handlecommon


import json

def get_mainpage_comment_key():
   return db.Key.from_path('TableComments', 'mainpage_comments')

class HandleComment( webapp2.RequestHandler ):

   def get_thread_id(self):
      self.provider  = None;
      self.image     = None;
      self.thread_id = None;
      
      if self.request.get("thread_id") :
         ( self.thread_id, self.provider ) = handlecommon.check_and_get_provider( self, 'thread_id', 
                                                                           get_mainpage_comment_key() );
         if self.thread_id == None: 
            return False
         
      elif  self.request.get("image_id") :
         image    = datatables.TableImagesInfo.get( self.request.get("image_id") )
         
         if image == None:
            handlecommon.print_error( self, 400, "Invalid message (image id)" ) 
            return False
         
         self.image = image;
         self.thread_id = image.key() ;
         
      else :
         handlecommon.print_error( self, 400, "Invalid message (id)" ) 
         return False
      
      return True;
  


   def get(self):
      if self.get_thread_id() == False:
          return ;

      comments_query = datatables.TableComments.all().ancestor( self.thread_id ).order('-date')
      
      comment_offset = 0
      comment_amount = 100
      
      ## Check if we have offset & len provided
      try:
         comment_str = self.request.get('comments') 
         if comment_str != "":
            comment_amount = int( comment_str )
      except:
         handlecommon.print_error( self, 400, "Invalid message (comment amount)" ) 
         return
      
      try:
         comment_str = self.request.get('comments_offset') 
         if comment_str != "":
            comment_offset = int( comment_str )
      except:
         handlecommon.print_error( self, 400, "Invalid message (comment offset)" ) 
         return
      
      comment_list = comments_query.fetch( limit = comment_amount, offset = comment_offset )
        
      if ( self.request.get('json') ):
         # We need to make list for JSON to serialize
         json_list = []
         for comment in comment_list:
            json_list.append( handlecommon.to_dict(comment) )
         
         self.response.write( json.dumps( { "comments" : json_list } ) )
      else:
         template = JINJA_ENVIRONMENT.get_template('html/comment.html')
         image_url = None;
         
         if self.image:
            image_url = get_serving_url( self.image.blob_key )
            post_var  = "image_id"   
         else:
            post_var  = "thread_id"
         
         template_values = { 
                              'provider'     : self.provider, 
                              'image_url'    : image_url,
                              'thread_id'    : str( self.thread_id )  ,
                              'post_var'     : post_var , 
                              'comment_list' : comment_list 
                           }
         self.response.write(template.render( template_values ))
                                               
   def post(self):
      
      if self.get_thread_id() == False:
          return ;
       
      author  = self.request.get('commenter')
      message = self.request.get('comment')
      
      if message == None or len ( message ) < 2 :
         handlecommon.print_error( self, 400, "Invalid message" )
         return 
      
      if author != None and len ( author ) < 3 : 
         author = None
      # FIXME: Here check for reserved names   
      
      #try:
      if True:
         comment = datatables.TableComments( parent = self.thread_id )
         comment.author   = author
         comment.message = message
         comment.put()
      #except:
      #   handlecommon.print_error( self, 500, "Write failed" )
      #   return 
      
      if ( self.request.get('json')):
          self.response.write( json.dumps( { 'comment_id' : "%s" % comment.key() } ) )
      else:
          self.get()

