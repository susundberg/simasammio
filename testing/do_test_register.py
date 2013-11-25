
import requests
import json
import time
import inspect
import string
import random
import sys
import datetime

def print_usage():
   print "USAGE: ./python test_server <host to test> <number of updates> <open status>"


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
     return ''.join(random.choice(chars) for x in range(size))


def generate_random_lat():
   return "%f" % (60.45239 + -0.01 + 0.02*random.random())

def generate_random_lon():
   return "%f" % (22.2782 + -0.01 + 0.02*random.random())

def PrintTestOk():
  callerframerecord = inspect.stack()[1] 
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  print "Test:" + str( info.filename ) + ":" + str( info.lineno ) + " OK!"
  
  
def PrintFrame():
  callerframerecord = inspect.stack()[1]    # 0 represents this line
                                            # 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  print "FILE:" + str( info.filename ) + ":" + str( info.lineno )
  # print "FUNC:"info.function                       # __FUNCTION__ -> Main
 
def PrintRequest(r):
   print "-------------HEADERS------------------"
   print r.headers
   print "-------------CONTENT------------------"
   print r.text
   

if len(sys.argv) != 4:
   print_usage()
   exit(0)
   
host_base         = sys.argv[1];
number_of_updates = int( sys.argv[2] )
open_status_str   = ( sys.argv[3] ).lower();

open_status = False
if ( open_status_str == 'true'):
   open_status = True
   

print "TESTING SERVER " + host_base + " with %d updates " % number_of_updates;

TEST_ID=0

r = requests.get(host_base)

#######################################################

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   exit(0);
   
PrintTestOk()



#############################################generate_random_lon##########
print "Test for register"
#######################################################



      
payload = {
   'name'        : "Karry " + id_generator(16),
   'description' : "Automatic test script ",
   'valid_from'  : "",
   'valid_to'    : "",
   'secret'      : 'INVALID',
   'json'        : '1'
   }

r = requests.post(host_base+"/register" , data=payload)

# Invalid secret
if (r.status_code == requests.codes.ok ):
   PrintFrame()
   exit(0);
   
payload['secret'] = "kisumirri"
PrintTestOk()

r = requests.post(host_base+"/register" , data=payload)

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

resp_object = json.loads( r.text )

try:
   id_cart = resp_object["id"]   
except:
   PrintRequest(r)
   PrintFrame()
   exit(0);
print "ID FOUND: " + id_cart


PrintTestOk()

# Then try to re register with same name

time.sleep(0.1) # delays 

r = requests.post(host_base+"/register" , data=payload)
# Should reject re-registration
if (r.status_code == requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);
   
PrintTestOk()


#######################################################
print "Test for Updating cart info"
#######################################################
url = host_base+"/register_update" 
test_keys=["description"];

if open_status == True:
   
   date_delta = datetime.timedelta(days=1)
   date_open  = datetime.datetime.now() - date_delta 
   date_close = datetime.datetime.now() + date_delta 
   
   valid_from_str =  date_open.strftime("%Y-%m-%d %H%M")   
   valid_to_str   = date_close.strftime("%Y-%m-%d %H%M")   
   print "Point is set to be open : " + valid_from_str + " -> " + valid_to_str
   test_keys.push("valid_from");
   test_keys.push("valid_to");
   
else:
   if  ( random.random() > 0.5 ):
      valid_from_str = '2014-04-30 1400'
   else:
      valid_from_str = ''
      
   if  ( random.random() > 0.5 ):
      valid_to_str = '2015-04-30 1400'
   else:
      valid_to_str = ''
   
payload = {
      'id'          : id_cart,
      'description' : "Automatic test script updated description! Overtime please! ",
      'valid_from'  : valid_from_str,
      'valid_to'    : valid_to_str,
      'json'        : '1'
      }

r = requests.post( url, data=payload)

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);
   
PrintTestOk()


url2 = url + "?id=" + id_cart + "&" + "json=1";
r = requests.get( url2 );

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

cart_info = json.loads( r.text )



for key in test_keys:
   if cart_info.has_key(key) == False:
      print "KEY CHECK FAILED NO KEY '" + key + "'"
      PrintFrame()
      PrintRequest(r)
      exit(0);
   
   if ( cart_info[key] != payload[key] ):
      print "KEY CHECK FAILED: " + key
      print "CART " + cart_info[key]
      print "PAYL " + payload[key]
      PrintFrame()
      PrintRequest(r)
      exit(0);
      
PrintTestOk()



#######################################################
print "Test for commenting"
#######################################################

url = host_base+"/comment" 
payload = {
   'comment'   : """Multiline \n comment \n testing <b> WITH HTML </b> \n
                  <script type=\"text/javascript\"> document.write(\"JAVASCRIPT Hello World!\") </script>""",
   'commenter' : "Testing scripts " ,
   'thread_id' : str( id_cart ) ,
   'json'            : "1"
   }

r = requests.post( url, data=payload)
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);
   
PrintTestOk()

payload['comment'] = "TEST PASSED OK"
r = requests.post( url, data=payload)
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

# Get comment
payload = {
      'comments'        : "2",
      'comments_offset' : "0",
      'json'            : "1",
      'thread_id'       : str( id_cart ) 
      }

r = requests.get( url, params=payload)
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);
   

try:
   comments_dict = json.loads( r.text );
   comments = comments_dict['comments']
except:
   PrintFrame()
   PrintRequest(r)
   exit(0);
   
if ( len(comments) != 2 ) :
   PrintFrame()
   PrintRequest(r)
   exit(0);
   

PrintTestOk()


#######################################################
print "Test for Updating "
#######################################################
url = host_base+"/update" 

# test without ID
r = requests.get( url )
if (r.status_code == requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

PrintTestOk()

for loop in range(0,number_of_updates):
   payload = {
         'id'              : id_cart,
         'lat'             : generate_random_lat(),
         'long'            : generate_random_lon(),
         'comments'        : "1",
         'comments_offset' : "0",
         'json'            : "1"
         }
   r = requests.post( url, data=payload)

   if (r.status_code != requests.codes.ok ):
      PrintFrame()
      PrintRequest(r)
      exit(0);
      
   try:
      comments_dict = json.loads(r.text);
      comments = comments_dict['comments'];
   except:
      PrintFrame()
      PrintRequest(r)
      exit(0);

   if len (comments) != 1:
      PrintFrame()
      PrintRequest(r)
      exit(0);

   if ( comments[0]['message'] != "TEST PASSED OK" or comments[0]['author'] != "Testing scripts "):
      PrintFrame()
      PrintRequest(r)
      exit(0);
   
PrintTestOk()



# Then test for get update 
url2 = url + "?id=" + id_cart + "&json=1"

time.sleep(0.1) # delays 

r = requests.get( url2 )
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

updates = json.loads( r.text );

if len ( updates ) != number_of_updates:
   PrintFrame()
   PrintRequest(r)
   exit(0);

PrintTestOk()

#######################################################
print "Test for uploading image"
#######################################################

url = host_base+"/upload_image" 

files = {'file': open('test.png', 'rb')}

payload = {
      'id'              : id_cart,
      'lat'             : generate_random_lat(), 
      'long'            : generate_random_lon(),
      'json'            : "1"
      }

r = requests.post(url, files=files, data=payload )

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

image_hash = json.loads( r.text );

if image_hash.has_key("image_id") == False:
   PrintFrame()
   PrintRequest(r)
   exit(0);

image_id = image_hash["image_id"];

PrintTestOk()

#######################################################
print "Try to post comment to that image_hash"
#######################################################

url = host_base+"/comment" 
payload = {
   'comment'   : "Hello pretty picture!",
   'commenter' : "Testing scripts " ,
   'image_id'  :  image_id ,
   'json'      : "1"
   }

r = requests.post( url, data=payload )
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

#then confirm that it got posted
time.sleep(0.1) # delays    
   
r = requests.get( url + "?image_id=" + image_id + "&json=1")
if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

image_comment_hash = json.loads( r.text );

if len (image_comment_hash) != 1:
   PrintFrame()
   PrintRequest(r)
   exit(0);
   

PrintTestOk()



time.sleep(0.1) # delays 


#######################################################
print "Test tp get main (images)"
#######################################################

r = requests.get( host_base )

if (r.status_code != requests.codes.ok ):
   PrintFrame()
   PrintRequest(r)
   exit(0);

PrintTestOk()


print "----------------ALL TEST OK----------------\n"









