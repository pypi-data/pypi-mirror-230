#!/usr/bin/env python

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2016-2023 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016-2023 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: pywwwget.py - Last Update: 9/13/2023 Ver. 0.8.2 RC 1 - Author: cooldude2k $
'''

from __future__ import division, absolute_import, print_function;
import re, os, sys, hashlib, shutil, platform, tempfile, urllib, gzip, time, argparse, cgi, subprocess;
import logging as log;
from ftplib import FTP, FTP_TLS;
from base64 import b64encode;
haverequests = False;
try:
 import requests;
 haverequests = True;
except ImportError:
 haverequests = False;
havemechanize = False;
try:
 import mechanize;
 havemechanize = True;
except ImportError:
 havemechanize = False;
haveparamiko = False;
try:
 import paramiko;
 haveparamiko = True;
except ImportError:
 haveparamiko = False;
haveurllib3 = False;
try:
 import urllib3;
 haveurllib3 = True;
except ImportError:
 haveurllib3 = False;
havehttplib2 = False;
try:
 from httplib2 import HTTPConnectionWithTimeout, HTTPSConnectionWithTimeout;
 havehttplib2 = True;
except ImportError:
 havehttplib2 = False;
if(sys.version[0]=="2"):
 try:
  from cStringIO import StringIO;
 except ImportError:
  from StringIO import StringIO;
 # From http://python-future.org/compatible_idioms.html
 from urlparse import urlparse, urlunparse, urlsplit, urlunsplit, urljoin;
 from urllib import urlencode;
 from urllib import urlopen as urlopenalt;
 from urllib2 import urlopen, Request, install_opener, HTTPError;
 import urllib2, urlparse, cookielib;
 from httplib import HTTPConnection, HTTPSConnection;
if(sys.version[0]>="3"):
 from io import StringIO, BytesIO;
 # From http://python-future.org/compatible_idioms.html
 from urllib.parse import urlparse, urlunparse, urlsplit, urlunsplit, urljoin, urlencode;
 from urllib.request import urlopen, Request, install_opener;
 from urllib.error import HTTPError;
 import urllib.request as urllib2;
 import urllib.parse as urlparse;
 import http.cookiejar as cookielib;
 from http.client import HTTPConnection, HTTPSConnection;

__program_name__ = "PyWWW-Get";
__program_alt_name__ = "PyWWWGet";
__program_small_name__ = "wwwget";
__project__ = __program_name__;
__project_url__ = "https://github.com/GameMaker2k/PyWWW-Get";
__version_info__ = (0, 8, 2, "RC 1", 1);
__version_date_info__ = (2023, 9, 13, "RC 1", 1);
__version_date__ = str(__version_date_info__[0])+"."+str(__version_date_info__[1]).zfill(2)+"."+str(__version_date_info__[2]).zfill(2);
__revision__ = __version_info__[3];
__revision_id__ = "$Id: 92f4be686afeaf8b2a7f4518910d8a66e2d31c31 $";
if(__version_info__[4] is not None):
 __version_date_plusrc__ = __version_date__+"-"+str(__version_date_info__[4]);
if(__version_info__[4] is None):
 __version_date_plusrc__ = __version_date__;
if(__version_info__[3] is not None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2])+" "+str(__version_info__[3]);
if(__version_info__[3] is None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2]);

tmpfileprefix = "py"+str(sys.version_info[0])+__program_small_name__+str(__version_info__[0])+"-";
tmpfilesuffix = "-";
pytempdir = tempfile.gettempdir();

geturls_cj = cookielib.CookieJar();
geturls_ua_firefox_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0";
geturls_ua_seamonkey_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0 SeaMonkey/2.49.3";
geturls_ua_chrome_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36";
geturls_ua_chromium_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/67.0.3396.99 Chrome/67.0.3396.99 Safari/537.36";
geturls_ua_palemoon_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.9) Gecko/20100101 Goanna/3.4 Firefox/52.9 PaleMoon/27.9.3";
geturls_ua_opera_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.54";
geturls_ua_vivaldi_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.52";
geturls_ua_internet_explorer_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko";
geturls_ua_microsoft_edge_windows7 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134";
geturls_ua_pywwwget_python = "Mozilla/5.0 (compatible; {proname}/{prover}; +{prourl})".format(proname=__project__, prover=__version__, prourl=__project_url__);
if(platform.python_implementation()!=""):
 geturls_ua_pywwwget_python_alt = "Mozilla/5.0 ({osver}; {archtype}; +{prourl}) {pyimp}/{pyver} (KHTML, like Gecko) {proname}/{prover}".format(osver=platform.system()+" "+platform.release(), archtype=platform.machine(), prourl=__project_url__, pyimp=platform.python_implementation(), pyver=platform.python_version(), proname=__project__, prover=__version__);
if(platform.python_implementation()==""):
 geturls_ua_pywwwget_python_alt = "Mozilla/5.0 ({osver}; {archtype}; +{prourl}) {pyimp}/{pyver} (KHTML, like Gecko) {proname}/{prover}".format(osver=platform.system()+" "+platform.release(), archtype=platform.machine(), prourl=__project_url__, pyimp="Python", pyver=platform.python_version(), proname=__project__, prover=__version__);
geturls_ua_googlebot_google = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)";
geturls_ua_googlebot_google_old = "Googlebot/2.1 (+http://www.google.com/bot.html)";
geturls_ua = geturls_ua_firefox_windows7;
geturls_headers_firefox_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_firefox_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_seamonkey_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_seamonkey_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_chrome_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_chrome_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_chromium_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_chromium_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_palemoon_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_palemoon_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_opera_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_opera_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_vivaldi_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_vivaldi_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_internet_explorer_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_internet_explorer_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_microsoft_edge_windows7 = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_microsoft_edge_windows7, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_pywwwget_python = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_pywwwget_python, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_pywwwget_python_alt = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_pywwwget_python_alt, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_googlebot_google = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers_googlebot_google_old = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google_old, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"};
geturls_headers = geturls_headers_firefox_windows7;
geturls_download_sleep = 0;

def verbose_printout(dbgtxt, outtype="log", dbgenable=True, dgblevel=20):
 if(outtype=="print" and dbgenable):
  print(dbgtxt);
  return True;
 elif(outtype=="log" and dbgenable):
  logging.info(dbgtxt);
  return True;
 elif(outtype=="warning" and dbgenable):
  logging.warning(dbgtxt);
  return True;
 elif(outtype=="error" and dbgenable):
  logging.error(dbgtxt);
  return True;
 elif(outtype=="critical" and dbgenable):
  logging.critical(dbgtxt);
  return True;
 elif(outtype=="exception" and dbgenable):
  logging.exception(dbgtxt);
  return True;
 elif(outtype=="logalt" and dbgenable):
  logging.log(dgblevel, dbgtxt);
  return True;
 elif(outtype=="debug" and dbgenable):
  logging.debug(dbgtxt);
  return True;
 elif(not dbgenable):
  return True;
 else:
  return False;
 return False;

def verbose_printout_return(dbgtxt, outtype="log", dbgenable=True, dgblevel=20):
 verbose_printout(dbgtxt, outtype, dbgenable, dgblevel);
 return dbgtxt;

def add_url_param(url, **params):
 n=3;
 parts = list(urlparse.urlsplit(url));
 d = dict(cgi.parse_qsl(parts[n])); # use cgi.parse_qs for list values
 d.update(params);
 parts[n]=urlencode(d);
 return urlparse.urlunsplit(parts);

os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.path.dirname(os.path.realpath(__file__)) + os.pathsep + os.getcwd();
def which_exec(execfile):
 for path in os.environ["PATH"].split(":"):
  if os.path.exists(path + "/" + execfile):
   return path + "/" + execfile;

def listize(varlist):
 il = 0;
 ix = len(varlist);
 ilx = 1;
 newlistreg = {};
 newlistrev = {};
 newlistfull = {};
 while(il < ix):
  newlistreg.update({ilx: varlist[il]});
  newlistrev.update({varlist[il]: ilx});
  ilx = ilx + 1;
  il = il + 1;
 newlistfull = {1: newlistreg, 2: newlistrev, 'reg': newlistreg, 'rev': newlistrev};
 return newlistfull;

def twolistize(varlist):
 il = 0;
 ix = len(varlist);
 ilx = 1;
 newlistnamereg = {};
 newlistnamerev = {};
 newlistdescreg = {};
 newlistdescrev = {};
 newlistfull = {};
 while(il < ix):
  newlistnamereg.update({ilx: varlist[il][0].strip()});
  newlistnamerev.update({varlist[il][0].strip(): ilx});
  newlistdescreg.update({ilx: varlist[il][1].strip()});
  newlistdescrev.update({varlist[il][1].strip(): ilx});
  ilx = ilx + 1;
  il = il + 1;
 newlistnametmp = {1: newlistnamereg, 2: newlistnamerev, 'reg': newlistnamereg, 'rev': newlistnamerev};
 newlistdesctmp = {1: newlistdescreg, 2: newlistdescrev, 'reg': newlistdescreg, 'rev': newlistdescrev};
 newlistfull = {1: newlistnametmp, 2: newlistdesctmp, 'name': newlistnametmp, 'desc': newlistdesctmp}
 return newlistfull;

def arglistize(proexec, *varlist):
 il = 0;
 ix = len(varlist);
 ilx = 1;
 newarglist = [proexec];
 while(il < ix):
  if varlist[il][0] is not None:
   newarglist.append(varlist[il][0]);
  if varlist[il][1] is not None:
   newarglist.append(varlist[il][1]);
  il = il + 1;
 return newarglist;

# hms_string by ArcGIS Python Recipes
# https://arcpy.wordpress.com/2012/04/20/146/
def hms_string(sec_elapsed):
 h = int(sec_elapsed / (60 * 60));
 m = int((sec_elapsed % (60 * 60)) / 60);
 s = sec_elapsed % 60.0;
 return "{}:{:>02}:{:>05.2f}".format(h, m, s);

# get_readable_size by Lipis
# http://stackoverflow.com/posts/14998888/revisions
def get_readable_size(bytes, precision=1, unit="IEC"):
 unit = unit.upper();
 if(unit!="IEC" and unit!="SI"):
  unit = "IEC";
 if(unit=="IEC"):
  units = [" B"," KiB"," MiB"," GiB"," TiB"," PiB"," EiB"," ZiB"];
  unitswos = ["B","KiB","MiB","GiB","TiB","PiB","EiB","ZiB"];
  unitsize = 1024.0;
 if(unit=="SI"):
  units = [" B"," kB"," MB"," GB"," TB"," PB"," EB"," ZB"];
  unitswos = ["B","kB","MB","GB","TB","PB","EB","ZB"];
  unitsize = 1000.0;
 return_val = {};
 orgbytes = bytes;
 for unit in units:
  if abs(bytes) < unitsize:
   strformat = "%3."+str(precision)+"f%s";
   pre_return_val = (strformat % (bytes, unit));
   pre_return_val = re.sub(r"([0]+) ([A-Za-z]+)", r" \2", pre_return_val);
   pre_return_val = re.sub(r"\. ([A-Za-z]+)", r" \1", pre_return_val);
   alt_return_val = pre_return_val.split();
   return_val = {'Bytes': orgbytes, 'ReadableWithSuffix': pre_return_val, 'ReadableWithoutSuffix': alt_return_val[0], 'ReadableSuffix': alt_return_val[1]}
   return return_val;
  bytes /= unitsize;
 strformat = "%."+str(precision)+"f%s";
 pre_return_val = (strformat % (bytes, "YiB"));
 pre_return_val = re.sub(r"([0]+) ([A-Za-z]+)", r" \2", pre_return_val);
 pre_return_val = re.sub(r"\. ([A-Za-z]+)", r" \1", pre_return_val);
 alt_return_val = pre_return_val.split();
 return_val = {'Bytes': orgbytes, 'ReadableWithSuffix': pre_return_val, 'ReadableWithoutSuffix': alt_return_val[0], 'ReadableSuffix': alt_return_val[1]}
 return return_val;

def get_readable_size_from_file(infile, precision=1, unit="IEC", usehashes=False, usehashtypes="md5,sha1"):
 unit = unit.upper();
 usehashtypes = usehashtypes.lower();
 getfilesize = os.path.getsize(infile);
 return_val = get_readable_size(getfilesize, precision, unit);
 if(usehashes):
  hashtypelist = usehashtypes.split(",");
  openfile = open(infile, "rb");
  filecontents = openfile.read();
  openfile.close();
  listnumcount = 0;
  listnumend = len(hashtypelist);
  while(listnumcount < listnumend):
   hashtypelistlow = hashtypelist[listnumcount].strip();
   hashtypelistup = hashtypelistlow.upper();
   filehash = hashlib.new(hashtypelistup);
   filehash.update(filecontents);
   filegethash = filehash.hexdigest();
   return_val.update({hashtypelistup: filegethash});
   listnumcount += 1;
 return return_val;

def get_readable_size_from_string(instring, precision=1, unit="IEC", usehashes=False, usehashtypes="md5,sha1"):
 unit = unit.upper();
 usehashtypes = usehashtypes.lower();
 getfilesize = len(instring);
 return_val = get_readable_size(getfilesize, precision, unit);
 if(usehashes):
  hashtypelist = usehashtypes.split(",");
  listnumcount = 0;
  listnumend = len(hashtypelist);
  while(listnumcount < listnumend):
   hashtypelistlow = hashtypelist[listnumcount].strip();
   hashtypelistup = hashtypelistlow.upper();
   filehash = hashlib.new(hashtypelistup);
   if(sys.version[0]=="2"):
    filehash.update(instring);
   if(sys.version[0]>="3"):
    filehash.update(instring.encode('utf-8'));
   filegethash = filehash.hexdigest();
   return_val.update({hashtypelistup: filegethash});
   listnumcount += 1;
 return return_val;

def make_http_headers_from_dict_to_list(headers={'Referer': "http://google.com/", 'User-Agent': geturls_ua, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}):
 if isinstance(headers, dict):
  returnval = [];
  if(sys.version[0]=="2"):
   for headkey, headvalue in headers.iteritems():
    returnval.append((headkey, headvalue));
  if(sys.version[0]>="3"):
   for headkey, headvalue in headers.items():
    returnval.append((headkey, headvalue));
 elif isinstance(headers, list):
  returnval = headers;
 else:
  returnval = False;
 return returnval;

def make_http_headers_from_dict_to_pycurl(headers={'Referer': "http://google.com/", 'User-Agent': geturls_ua, 'Accept-Encoding': "gzip, deflate", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}):
 if isinstance(headers, dict):
  returnval = [];
  if(sys.version[0]=="2"):
   for headkey, headvalue in headers.iteritems():
    returnval.append(headkey+": "+headvalue);
  if(sys.version[0]>="3"):
   for headkey, headvalue in headers.items():
    returnval.append(headkey+": "+headvalue);
 elif isinstance(headers, list):
  returnval = headers;
 else:
  returnval = False;
 return returnval;

def make_http_headers_from_list_to_dict(headers=[("Referer", "http://google.com/"), ("User-Agent", geturls_ua), ("Accept-Encoding", "gzip, deflate"), ("Accept-Language", "en-US,en;q=0.8,en-CA,en-GB;q=0.6"), ("Accept-Charset", "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7"), ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"), ("Connection", "close")]):
 if isinstance(headers, list):
  returnval = {};
  mli = 0;
  mlil = len(headers);
  while(mli<mlil):
   returnval.update({headers[mli][0]: headers[mli][1]});
   mli = mli + 1;
 elif isinstance(headers, dict):
  returnval = headers;
 else:
  returnval = False;
 return returnval;

def get_httplib_support(checkvalue=None):
 global haverequests, havemechanize;
 returnval = [];
 returnval.append("httplib");
 returnval.append("urllib");
 returnval.append("request");
 if(haverequests):
  returnval.append("requests");
 if(havemechanize):
  returnval.append("mechanize");
 if(not checkvalue is None):
  if(checkvalue=="urllib1" or checkvalue=="urllib2"):
   checkvalue = "urllib";
  if(checkvalue=="httplib1"):
   checkvalue = "httplib";
  if(checkvalue in returnval):
   returnval = True;
  else:
   returnval = False;
 return returnval;

def check_httplib_support(checkvalue="urllib"):
 if(checkvalue=="urllib1" or checkvalue=="urllib2"):
  checkvalue = "urllib";
 if(checkvalue=="httplib1"):
  checkvalue = "httplib";
 returnval = get_httplib_support(checkvalue);
 return returnval;

def get_httplib_support_list():
 returnval = get_httplib_support(None);
 return returnval;

def download_from_url(httpurl, httpheaders, httpcookie, httplibuse="urllib", sleep=-1):
 global geturls_download_sleep, haverequests, havemechanize;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(httplibuse=="urllib1" or httplibuse=="urllib2"):
  httplibuse = "urllib";
 if(httplibuse=="httplib1"):
  httplibuse = "httplib";
 if(not haverequests and httplibuse=="requests"):
  httplibuse = "urllib";
 if(not havemechanize and httplibuse=="mechanize"):
  httplibuse = "urllib";
 if(not havehttplib2 and httplibuse=="httplib2"):
  httplibuse = "httplib";
 if(httplibuse=="urllib"):
  returnval = download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep);
 elif(httplibuse=="request"):
  returnval = download_from_url_with_request(httpurl, httpheaders, httpcookie, sleep);
 elif(httplibuse=="httplib"):
  returnval = download_from_url_with_httplib(httpurl, httpheaders, httpcookie, sleep);
 elif(httplibuse=="httplib2"):
  returnval = download_from_url_with_httplib2(httpurl, httpheaders, httpcookie, sleep);
 elif(httplibuse=="requests"):
  returnval = download_from_url_with_requests(httpurl, httpheaders, httpcookie, sleep);
 elif(httplibuse=="mechanize"):
  returnval = download_from_url_with_mechanize(httpurl, httpheaders, httpcookie, sleep);
 else:
  returnval = False;
 return returnval;

def download_from_url_file(httpurl, httpheaders, httpcookie, httplibuse="urllib", buffersize=524288, sleep=-1):
 global geturls_download_sleep, haverequests, havemechanize;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(httplibuse=="urllib1" or httplibuse=="urllib2"):
  httplibuse = "urllib";
 if(httplibuse=="httplib1"):
  httplibuse = "httplib";
 if(not haverequests and httplibuse=="requests"):
  httplibuse = "urllib";
 if(not havemechanize and httplibuse=="mechanize"):
  httplibuse = "urllib";
 if(not havehttplib2 and httplibuse=="httplib2"):
  httplibuse = "httplib";
 if(httplibuse=="urllib"):
  returnval = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, sleep);
 elif(httplibuse=="request"):
  returnval = download_from_url_file_with_request(httpurl, httpheaders, httpcookie, buffersize, sleep);
 elif(httplibuse=="httplib"):
  returnval = download_from_url_file_with_httplib(httpurl, httpheaders, httpcookie, buffersize, sleep);
 elif(httplibuse=="requests"):
  returnval = download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize, sleep);
 elif(httplibuse=="mechanize"):
  returnval = download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize, sleep);
 else:
  returnval = False;
 return returnval;

def download_from_url_to_file(httpurl, httpheaders, httpcookie, httplibuse="urllib", outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
 global geturls_download_sleep, haverequests, havemechanize;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(httplibuse=="urllib1" or httplibuse=="urllib2"):
  httplibuse = "urllib";
 if(httplibuse=="httplib1"):
  httplibuse = "httplib";
 if(not haverequests and httplibuse=="requests"):
  httplibuse = "urllib";
 if(not havemechanize and httplibuse=="mechanize"):
  httplibuse = "urllib";
 if(not havehttplib2 and httplibuse=="httplib2"):
  httplibuse = "httplib";
 if(httplibuse=="urllib"):
  returnval = download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, outfile, outpath, buffersize, sleep);
 elif(httplibuse=="request"):
  returnval = download_from_url_to_file_with_request(httpurl, httpheaders, httpcookie, outfile, outpath, buffersize, sleep);
 elif(httplibuse=="httplib"):
  returnval = download_from_url_to_file_with_httplib(httpurl, httpheaders, httpcookie, outfile, outpath, buffersize, sleep);
 elif(httplibuse=="requests"):
  returnval = download_from_url_to_file_with_requests(httpurl, httpheaders, httpcookie, outfile, outpath, buffersize, sleep);
 elif(httplibuse=="mechanize"):
  returnval = download_from_url_to_file_with_mechanize(httpurl, httpheaders, httpcookie, outfile, outpath, buffersize, sleep);
 else:
  returnval = False;
 return returnval;

def download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 if(isinstance(httpheaders, dict)):
  httpheaders = make_http_headers_from_dict_to_list(httpheaders);
 geturls_opener.addheaders = httpheaders;
 time.sleep(sleep);
 geturls_text = geturls_opener.open(httpurl);
 log.info("Downloading URL "+httpurl);
 if(geturls_text.info().get("Content-Encoding")=="gzip" or geturls_text.info().get("Content-Encoding")=="deflate"):
  if(sys.version[0]=="2"):
   strbuf = StringIO(geturls_text.read());
  if(sys.version[0]>="3"):
   strbuf = BytesIO(geturls_text.read());
  gzstrbuf = gzip.GzipFile(fileobj=strbuf);
  returnval_content = gzstrbuf.read()[:];
 if(geturls_text.info().get("Content-Encoding")!="gzip" and geturls_text.info().get("Content-Encoding")!="deflate"):
  returnval_content = geturls_text.read()[:];
 returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.getcode()};
 geturls_text.close();
 return returnval;

def download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
 global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
 exec_time_start = time.time();
 myhash = hashlib.new("sha1");
 if(sys.version[0]=="2"):
  myhash.update(httpurl);
  myhash.update(str(buffersize));
  myhash.update(str(exec_time_start));
 if(sys.version[0]>="3"):
  myhash.update(httpurl.encode('utf-8'));
  myhash.update(str(buffersize).encode('utf-8'));
  myhash.update(str(exec_time_start).encode('utf-8'));
 newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 if(isinstance(httpheaders, dict)):
  httpheaders = make_http_headers_from_dict_to_list(httpheaders);
 geturls_opener.addheaders = httpheaders;
 time.sleep(sleep);
 geturls_text = geturls_opener.open(httpurl);
 downloadsize = geturls_text.info().get('Content-Length');
 if(downloadsize is not None):
  downloadsize = int(downloadsize);
 if downloadsize is None: downloadsize = 0;
 fulldatasize = 0;
 prevdownsize = 0;
 log.info("Downloading URL "+httpurl);
 with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
  tmpfilename = f.name;
  returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.getcode()};
  while True:
   databytes = geturls_text.read(buffersize);
   if not databytes: break;
   datasize = len(databytes);
   fulldatasize = datasize + fulldatasize;
   percentage = "";
   if(downloadsize>0):
    percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
   downloaddiff = fulldatasize - prevdownsize;
   log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
   prevdownsize = fulldatasize;
   f.write(databytes);
  f.close();
 geturls_text.close();
 exec_time_end = time.time();
 log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
 returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
 return returnval;

def download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(not outfile=="-"):
  outpath = outpath.rstrip(os.path.sep);
  filepath = os.path.realpath(outpath+os.path.sep+outfile);
  if(not os.path.exists(outpath)):
   os.makedirs(outpath);
  if(os.path.exists(outpath) and os.path.isfile(outpath)):
   return False;
  if(os.path.exists(filepath) and os.path.isdir(filepath)):
   return False;
  pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  log.info("Moving file "+tmpfilename+" to "+filepath);
  exec_time_start = time.time();
  shutil.move(tmpfilename, filepath);
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
  if(os.path.exists(tmpfilename)):
   os.remove(tmpfilename);
  returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]=="2"):
  pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = StringIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]>="3"):
  pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = BytesIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 return returnval;

def download_from_url_with_httplib(httpurl, httpheaders, httpcookie, sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 geturls_opener.addheaders = httpheaders;
 time.sleep(sleep);
 if(urlparts[0]=="http"):
  httpconn = HTTPConnection(urlparts[1]);
 elif(urlparts[0]=="https"):
  httpconn = HTTPSConnection(urlparts[1]);
 else:
  return False;
 httpconn.request("GET", urlparts[2], headers=httpheaders);
 geturls_text = httpconn.getresponse();
 log.info("Downloading URL "+httpurl);
 if(dict(geturls_text.getheaders()).get("Content-Encoding")=="gzip" or dict(geturls_text.getheaders()).get("Content-Encoding")=="deflate"):
  if(sys.version[0]=="2"):
   strbuf = StringIO(geturls_text.read());
  if(sys.version[0]>="3"):
   strbuf = BytesIO(geturls_text.read());
  gzstrbuf = gzip.GzipFile(fileobj=strbuf);
  returnval_content = gzstrbuf.read()[:];
 if(dict(geturls_text.getheaders()).get("Content-Encoding")!="gzip" and dict(geturls_text.getheaders()).get("Content-Encoding")!="deflate"):
  returnval_content = geturls_text.read()[:];
 returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.getheaders()), 'URL': httpurl, 'Code': geturls_text.status};
 geturls_text.close();
 return returnval;

def download_from_url_file_with_httplib(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
 global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
 exec_time_start = time.time();
 myhash = hashlib.new("sha1");
 if(sys.version[0]=="2"):
  myhash.update(httpurl);
  myhash.update(str(buffersize));
  myhash.update(str(exec_time_start));
 if(sys.version[0]>="3"):
  myhash.update(httpurl.encode('utf-8'));
  myhash.update(str(buffersize).encode('utf-8'));
  myhash.update(str(exec_time_start).encode('utf-8'));
 newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 geturls_opener.addheaders = httpheaders;
 time.sleep(sleep);
 if(urlparts[0]=="http"):
  httpconn = HTTPConnection(urlparts[1]);
 elif(urlparts[0]=="https"):
  httpconn = HTTPSConnection(urlparts[1]);
 else:
  return False;
 httpconn.request("GET", urlparts[2], headers=httpheaders)
 geturls_text = httpconn.getresponse();
 downloadsize = dict(geturls_text.getheaders()).get('Content-Length');
 if(downloadsize is not None):
  downloadsize = int(downloadsize);
 if downloadsize is None: downloadsize = 0;
 fulldatasize = 0;
 prevdownsize = 0;
 log.info("Downloading URL "+httpurl);
 with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
  tmpfilename = f.name;
  returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(dict(geturls_text.getheaders())), 'URL': httpurl, 'Code': geturls_text.status};
  while True:
   databytes = geturls_text.read(buffersize);
   if not databytes: break;
   datasize = len(databytes);
   fulldatasize = datasize + fulldatasize;
   percentage = "";
   if(downloadsize>0):
    percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
   downloaddiff = fulldatasize - prevdownsize;
   log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
   prevdownsize = fulldatasize;
   f.write(databytes);
  f.close();
 geturls_text.close();
 exec_time_end = time.time();
 log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
 returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
 return returnval;

def download_from_url_to_file_with_httplib(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(not outfile=="-"):
  outpath = outpath.rstrip(os.path.sep);
  filepath = os.path.realpath(outpath+os.path.sep+outfile);
  if(not os.path.exists(outpath)):
   os.makedirs(outpath);
  if(os.path.exists(outpath) and os.path.isfile(outpath)):
   return False;
  if(os.path.exists(filepath) and os.path.isdir(filepath)):
   return False;
  pretmpfilename = download_from_url_file_with_httplib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  log.info("Moving file "+tmpfilename+" to "+filepath);
  exec_time_start = time.time();
  shutil.move(tmpfilename, filepath);
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
  if(os.path.exists(tmpfilename)):
   os.remove(tmpfilename);
  returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]=="2"):
  pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = StringIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]>="3"):
  pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = BytesIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 return returnval;

if(havehttplib2):
 def download_from_url_with_httplib2(httpurl, httpheaders, httpcookie, sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
  geturls_opener.addheaders = httpheaders;
  time.sleep(sleep);
  if(urlparts[0]=="http"):
   httpconn = HTTPConnectionWithTimeout(urlparts[1]);
  elif(urlparts[0]=="https"):
   httpconn = HTTPSConnectionWithTimeout(urlparts[1]);
  else:
   return False;
  httpconn.request("GET", urlparts[2], headers=httpheaders);
  geturls_text = httpconn.getresponse();
  log.info("Downloading URL "+httpurl);
  if(dict(geturls_text.getheaders()).get("Content-Encoding")=="gzip" or dict(geturls_text.getheaders()).get("Content-Encoding")=="deflate"):
   if(sys.version[0]=="2"):
    strbuf = StringIO(geturls_text.read());
   if(sys.version[0]>="3"):
    strbuf = BytesIO(geturls_text.read());
   gzstrbuf = gzip.GzipFile(fileobj=strbuf);
   returnval_content = gzstrbuf.read()[:];
  if(dict(geturls_text.getheaders()).get("Content-Encoding")!="gzip" and dict(geturls_text.getheaders()).get("Content-Encoding")!="deflate"):
   returnval_content = geturls_text.read()[:];
  returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.getheaders()), 'URL': httpurl, 'Code': geturls_text.status};
  geturls_text.close();
  return returnval;

if(not havehttplib2):
 def download_from_url_with_httplib2(httpurl, httpheaders, httpcookie, sleep=-1):
  returnval = download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep)
  return returnval;

if(havehttplib2):
 def download_from_url_file_with_httplib2(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
  exec_time_start = time.time();
  myhash = hashlib.new("sha1");
  if(sys.version[0]=="2"):
   myhash.update(httpurl);
   myhash.update(str(buffersize));
   myhash.update(str(exec_time_start));
  if(sys.version[0]>="3"):
   myhash.update(httpurl.encode('utf-8'));
   myhash.update(str(buffersize).encode('utf-8'));
   myhash.update(str(exec_time_start).encode('utf-8'));
  newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
  geturls_opener.addheaders = httpheaders;
  time.sleep(sleep);
  if(urlparts[0]=="http"):
   httpconn = HTTPConnectionWithTimeout(urlparts[1]);
  elif(urlparts[0]=="https"):
   httpconn = HTTPSConnectionWithTimeout(urlparts[1]);
  else:
   return False;
  httpconn.request("GET", urlparts[2], headers=httpheaders)
  geturls_text = httpconn.getresponse();
  downloadsize = dict(geturls_text.getheaders()).get('Content-Length');
  if(downloadsize is not None):
   downloadsize = int(downloadsize);
  if downloadsize is None: downloadsize = 0;
  fulldatasize = 0;
  prevdownsize = 0;
  log.info("Downloading URL "+httpurl);
  with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
   tmpfilename = f.name;
   returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(dict(geturls_text.getheaders())), 'URL': httpurl, 'Code': geturls_text.status};
   while True:
    databytes = geturls_text.read(buffersize);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.close();
  geturls_text.close();
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
  returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
  return returnval;

if(not havehttplib2):
 def download_from_url_file_with_httplib2(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  returnval = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, sleep)
  return returnval;

if(havehttplib2):
 def download_from_url_to_file_with_httplib2(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  if(not outfile=="-"):
   outpath = outpath.rstrip(os.path.sep);
   filepath = os.path.realpath(outpath+os.path.sep+outfile);
   if(not os.path.exists(outpath)):
    os.makedirs(outpath);
   if(os.path.exists(outpath) and os.path.isfile(outpath)):
    return False;
   if(os.path.exists(filepath) and os.path.isdir(filepath)):
    return False;
   pretmpfilename = download_from_url_file_with_httplib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   log.info("Moving file "+tmpfilename+" to "+filepath);
   exec_time_start = time.time();
   shutil.move(tmpfilename, filepath);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
   if(os.path.exists(tmpfilename)):
    os.remove(tmpfilename);
   returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]=="2"):
   pretmpfilename = download_from_url_file_with_urllib2(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = StringIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]>="3"):
   pretmpfilename = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = BytesIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  return returnval;

if(not havehttplib2):
 def download_from_url_to_file_with_httplib2(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  returnval = download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, outfile, outpath, sleep)
  return returnval;

def download_from_url_with_request(httpurl, httpheaders, httpcookie, sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 if(isinstance(httpheaders, dict)):
  httpheaders = make_http_headers_from_dict_to_list(httpheaders);
 geturls_opener.addheaders = httpheaders;
 urllib.request.install_opener(geturls_opener);
 time.sleep(sleep);
 httpheaders = make_http_headers_from_list_to_dict(httpheaders);
 geturls_text = urlopen(Request(httpurl, headers=httpheaders));
 log.info("Downloading URL "+httpurl);
 if(geturls_text.headers.get("Content-Encoding")=="gzip" or geturls_text.headers.get("Content-Encoding")=="deflate"):
  if(sys.version[0]=="2"):
   strbuf = StringIO(geturls_text.read());
  if(sys.version[0]>="3"):
   strbuf = BytesIO(geturls_text.read());
  gzstrbuf = gzip.GzipFile(fileobj=strbuf);
  returnval_content = gzstrbuf.read()[:];
 if(geturls_text.headers.get("Content-Encoding")!="gzip" and geturls_text.headers.get("Content-Encoding")!="deflate"):
  returnval_content = geturls_text.read()[:];
 returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.headers), 'URL': geturls_text.geturl(), 'Code': geturls_text.getcode()};
 geturls_text.close();
 return returnval;

def download_from_url_file_with_request(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
 global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
 exec_time_start = time.time();
 myhash = hashlib.new("sha1");
 if(sys.version[0]=="2"):
  myhash.update(httpurl);
  myhash.update(str(buffersize));
  myhash.update(str(exec_time_start));
 if(sys.version[0]>="3"):
  myhash.update(httpurl.encode('utf-8'));
  myhash.update(str(buffersize).encode('utf-8'));
  myhash.update(str(exec_time_start).encode('utf-8'));
 newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
 if(sleep<0):
  sleep = geturls_download_sleep;
 urlparts = urlparse.urlparse(httpurl);
 if(urlparts.username is not None or urlparts.password is not None):
  inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
  httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
 geturls_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(httpcookie));
 if(isinstance(httpheaders, dict)):
  httpheaders = make_http_headers_from_dict_to_list(httpheaders);
 geturls_opener.addheaders = httpheaders;
 urllib.request.install_opener(geturls_opener);
 time.sleep(sleep);
 httpheaders = make_http_headers_from_list_to_dict(httpheaders);
 geturls_text = urlopen(Request(httpurl, headers=httpheaders));
 downloadsize = geturls_text.headers.get('Content-Length');
 if(downloadsize is not None):
  downloadsize = int(downloadsize);
 if downloadsize is None: downloadsize = 0;
 fulldatasize = 0;
 prevdownsize = 0;
 log.info("Downloading URL "+httpurl);
 with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
  tmpfilename = f.name;
  returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(geturls_text.headers), 'URL': geturls_text.geturl(), 'Code': geturls_text.getcode()};
  while True:
   databytes = geturls_text.read(buffersize);
   if not databytes: break;
   datasize = len(databytes);
   fulldatasize = datasize + fulldatasize;
   percentage = "";
   if(downloadsize>0):
    percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
   downloaddiff = fulldatasize - prevdownsize;
   log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
   prevdownsize = fulldatasize;
   f.write(databytes);
  f.close();
 geturls_text.close();
 exec_time_end = time.time();
 log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
 returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
 return returnval;

def download_from_url_to_file_with_request(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
 global geturls_download_sleep;
 if(sleep<0):
  sleep = geturls_download_sleep;
 if(not outfile=="-"):
  outpath = outpath.rstrip(os.path.sep);
  filepath = os.path.realpath(outpath+os.path.sep+outfile);
  if(not os.path.exists(outpath)):
   os.makedirs(outpath);
  if(os.path.exists(outpath) and os.path.isfile(outpath)):
   return False;
  if(os.path.exists(filepath) and os.path.isdir(filepath)):
   return False;
  pretmpfilename = download_from_url_file_with_request(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  log.info("Moving file "+tmpfilename+" to "+filepath);
  exec_time_start = time.time();
  shutil.move(tmpfilename, filepath);
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
  if(os.path.exists(tmpfilename)):
   os.remove(tmpfilename);
  returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]=="2"):
  pretmpfilename = download_from_url_file_with_request(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = StringIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 if(outfile=="-" and sys.version[0]>="3"):
  pretmpfilename = download_from_url_file_with_request(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
  tmpfilename = pretmpfilename['Filename'];
  downloadsize = os.path.getsize(tmpfilename);
  fulldatasize = 0;
  prevdownsize = 0;
  exec_time_start = time.time();
  with open(tmpfilename, 'rb') as ft:
   f = BytesIO();
   while True:
    databytes = ft.read(buffersize[1]);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.seek(0);
   fdata = f.getvalue();
   f.close();
   ft.close();
   os.remove(tmpfilename);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
  returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
 return returnval;

if(haverequests):
 def download_from_url_with_requests(httpurl, httpheaders, httpcookie, sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  if(isinstance(httpheaders, list)):
   httpheaders = make_http_headers_from_list_to_dict(httpheaders);
  time.sleep(sleep);
  geturls_text = requests.get(httpurl, headers=httpheaders, cookies=httpcookie);
  log.info("Downloading URL "+httpurl);
  if(geturls_text.headers.get('Content-Type')=="gzip" or geturls_text.headers.get('Content-Type')=="deflate"):
   if(sys.version[0]=="2"):
    strbuf = StringIO(geturls_text.content);
   if(sys.version[0]>="3"):
    strbuf = BytesIO(geturls_text.content);
   gzstrbuf = gzip.GzipFile(fileobj=strbuf);
   returnval_content = gzstrbuf.content[:];
  if(geturls_text.headers.get('Content-Type')!="gzip" and geturls_text.headers.get('Content-Type')!="deflate"):
   returnval_content = geturls_text.content[:];
  returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.headers), 'URL': geturls_text.url, 'Code': geturls_text.status_code};
  geturls_text.close();
  return returnval;

if(not haverequests):
 def download_from_url_with_requests(httpurl, httpheaders, httpcookie, sleep=-1):
  returnval = download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep)
  return returnval;

if(haverequests):
 def download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
  exec_time_start = time.time();
  myhash = hashlib.new("sha1");
  if(sys.version[0]=="2"):
   myhash.update(httpurl);
   myhash.update(str(buffersize));
   myhash.update(str(exec_time_start));
  if(sys.version[0]>="3"):
   myhash.update(httpurl.encode('utf-8'));
   myhash.update(str(buffersize).encode('utf-8'));
   myhash.update(str(exec_time_start).encode('utf-8'));
  newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  if(isinstance(httpheaders, list)):
   httpheaders = make_http_headers_from_list_to_dict(httpheaders);
  time.sleep(sleep);
  geturls_text = requests.get(httpurl, headers=httpheaders, cookies=httpcookie, stream=True);
  downloadsize = int(geturls_text.headers.get('Content-Length'));
  if(downloadsize is not None):
   downloadsize = int(downloadsize);
  if downloadsize is None: downloadsize = 0;
  fulldatasize = 0;
  prevdownsize = 0;
  log.info("Downloading URL "+httpurl);
  with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
   tmpfilename = f.name;
   returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(geturls_text.headers), 'URL': geturls_text.url, 'Code': geturls_text.status_code};
   for databytes in geturls_text.iter_content(chunk_size=buffersize):
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.close();
  geturls_text.close();
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
  returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
  return returnval;

if(not haverequests):
 def download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  returnval = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, sleep)
  return returnval;

if(haverequests):
 def download_from_url_to_file_with_requests(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  if(not outfile=="-"):
   outpath = outpath.rstrip(os.path.sep);
   filepath = os.path.realpath(outpath+os.path.sep+outfile);
   if(not os.path.exists(outpath)):
    os.makedirs(outpath);
   if(os.path.exists(outpath) and os.path.isfile(outpath)):
    return False;
   if(os.path.exists(filepath) and os.path.isdir(filepath)):
    return False;
   pretmpfilename = download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   log.info("Moving file "+tmpfilename+" to "+filepath);
   exec_time_start = time.time();
   shutil.move(tmpfilename, filepath);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
   if(os.path.exists(tmpfilename)):
    os.remove(tmpfilename);
   returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]=="2"):
   pretmpfilename = download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = StringIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]>="3"):
   pretmpfilename = download_from_url_file_with_requests(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = BytesIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  return returnval;

if(not haverequests):
 def download_from_url_to_file_with_requests(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  returnval = download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, outfile, outpath, sleep)
  return returnval;

if(haveurllib3):
 def download_from_url_with_urllib3(httpurl, httpheaders, httpcookie, sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  if(isinstance(httpheaders, list)):
   httpheaders = make_http_headers_from_list_to_dict(httpheaders);
  time.sleep(sleep);
  urllib_pool = urllib3.PoolManager(headers=httpheaders);
  geturls_text = urllib_pool.request("GET", httpurl, headers=httpheaders, preload_content=False);
  log.info("Downloading URL "+httpurl);
  if(geturls_text.info().get("Content-Encoding")=="gzip" or geturls_text.info().get("Content-Encoding")=="deflate"):
   if(sys.version[0]=="2"):
    strbuf = StringIO(geturls_text.read());
   if(sys.version[0]>="3"):
    strbuf = BytesIO(geturls_text.read());
   gzstrbuf = gzip.GzipFile(fileobj=strbuf);
   returnval_content = gzstrbuf.read()[:];
  if(geturls_text.info().get("Content-Encoding")!="gzip" and geturls_text.info().get("Content-Encoding")!="deflate"):
   returnval_content = geturls_text.read()[:];
  returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.status};
  geturls_text.close();
  return returnval;

if(not haveurllib3):
 def download_from_url_with_urllib3(httpurl, httpheaders, httpcookie, sleep=-1):
  returnval = download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep)
  return returnval;

if(haveurllib3):
 def download_from_url_file_with_urllib3(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
  exec_time_start = time.time();
  myhash = hashlib.new("sha1");
  if(sys.version[0]=="2"):
   myhash.update(httpurl);
   myhash.update(str(buffersize));
   myhash.update(str(exec_time_start));
  if(sys.version[0]>="3"):
   myhash.update(httpurl.encode('utf-8'));
   myhash.update(str(buffersize).encode('utf-8'));
   myhash.update(str(exec_time_start).encode('utf-8'));
  newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  if(isinstance(httpheaders, list)):
   httpheaders = make_http_headers_from_list_to_dict(httpheaders);
  time.sleep(sleep);
  urllib_pool = urllib3.PoolManager(headers=httpheaders);
  geturls_text = urllib3.request("GET", httpurl, headers=httpheaders, preload_content=False);
  downloadsize = int(geturls_text.headers.get('Content-Length'));
  if(downloadsize is not None):
   downloadsize = int(downloadsize);
  if downloadsize is None: downloadsize = 0;
  fulldatasize = 0;
  prevdownsize = 0;
  log.info("Downloading URL "+httpurl);
  with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
   tmpfilename = f.name;
   returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.status};
   while True:
    databytes = geturls_text.read(buffersize);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.close();
  geturls_text.close();
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
  returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
  return returnval;

if(not haveurllib3):
 def download_from_url_file_with_urllib3(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  returnval = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, sleep)
  return returnval;

if(haveurllib3):
 def download_from_url_to_file_with_urllib3(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  if(not outfile=="-"):
   outpath = outpath.rstrip(os.path.sep);
   filepath = os.path.realpath(outpath+os.path.sep+outfile);
   if(not os.path.exists(outpath)):
    os.makedirs(outpath);
   if(os.path.exists(outpath) and os.path.isfile(outpath)):
    return False;
   if(os.path.exists(filepath) and os.path.isdir(filepath)):
    return False;
   pretmpfilename = download_from_url_file_with_urllib3(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   log.info("Moving file "+tmpfilename+" to "+filepath);
   exec_time_start = time.time();
   shutil.move(tmpfilename, filepath);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
   if(os.path.exists(tmpfilename)):
    os.remove(tmpfilename);
   returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]=="2"):
   pretmpfilename = download_from_url_file_with_urllib3(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = StringIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]>="3"):
   pretmpfilename = download_from_url_file_with_urllib3(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = BytesIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  return returnval;

if(not haveurllib3):
 def download_from_url_to_file_with_urllib3(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  returnval = download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, outfile, outpath, sleep)
  return returnval;

if(havemechanize):
 def download_from_url_with_mechanize(httpurl, httpheaders, httpcookie, sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  geturls_opener = mechanize.Browser();
  if(isinstance(httpheaders, dict)):
   httpheaders = make_http_headers_from_dict_to_list(httpheaders);
  time.sleep(sleep);
  geturls_opener.addheaders = httpheaders;
  geturls_opener.set_cookiejar(httpcookie);
  geturls_opener.set_handle_robots(False);
  geturls_text = geturls_opener.open(httpurl);
  log.info("Downloading URL "+httpurl);
  if(geturls_text.info().get("Content-Encoding")=="gzip" or geturls_text.info().get("Content-Encoding")=="deflate"):
   if(sys.version[0]=="2"):
    strbuf = StringIO(geturls_text.read());
   if(sys.version[0]>="3"):
    strbuf = BytesIO(geturls_text.read());
   gzstrbuf = gzip.GzipFile(fileobj=strbuf);
   returnval_content = gzstrbuf.read()[:];
  if(geturls_text.info().get("Content-Encoding")!="gzip" and geturls_text.info().get("Content-Encoding")!="deflate"):
   returnval_content = geturls_text.read()[:];
  returnval = {'Type': "Content", 'Content': returnval_content, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.code};
  geturls_text.close();
  return returnval;

if(not havemechanize):
 def download_from_url_with_mechanize(httpurl, httpheaders, httpcookie, sleep=-1):
  returnval = download_from_url_with_urllib(httpurl, httpheaders, httpcookie, sleep)
  return returnval;

if(havemechanize):
 def download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  global geturls_download_sleep, tmpfileprefix, tmpfilesuffix;
  exec_time_start = time.time();
  myhash = hashlib.new("sha1");
  if(sys.version[0]=="2"):
   myhash.update(httpurl);
   myhash.update(str(buffersize));
   myhash.update(str(exec_time_start));
  if(sys.version[0]>="3"):
   myhash.update(httpurl.encode('utf-8'));
   myhash.update(str(buffersize).encode('utf-8'));
   myhash.update(str(exec_time_start).encode('utf-8'));
  newtmpfilesuffix = tmpfilesuffix + str(myhash.hexdigest());
  if(sleep<0):
   sleep = geturls_download_sleep;
  urlparts = urlparse.urlparse(httpurl);
  if(urlparts.username is not None or urlparts.password is not None):
   inurlencode = b64encode(str(urlparts.username+":"+urlparts.password).encode()).decode("UTF-8");
   httpheaders.update( { 'Authorization': "Basic "+inurlencode } );
  geturls_opener = mechanize.Browser();
  if(isinstance(httpheaders, dict)):
   httpheaders = make_http_headers_from_dict_to_list(httpheaders);
  time.sleep(sleep);
  geturls_opener.addheaders = httpheaders;
  geturls_opener.set_cookiejar(httpcookie);
  geturls_opener.set_handle_robots(False);
  geturls_text = geturls_opener.open(httpurl);
  downloadsize = int(geturls_text.info().get('Content-Length'));
  if(downloadsize is not None):
   downloadsize = int(downloadsize);
  if downloadsize is None: downloadsize = 0;
  fulldatasize = 0;
  prevdownsize = 0;
  log.info("Downloading URL "+httpurl);
  with tempfile.NamedTemporaryFile('wb+', prefix=tmpfileprefix, suffix=newtmpfilesuffix, delete=False) as f:
   tmpfilename = f.name;
   returnval = {'Type': "File", 'Filename': tmpfilename, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'Headers': dict(geturls_text.info()), 'URL': geturls_text.geturl(), 'Code': geturls_text.code};
   while True:
    databytes = geturls_text.read(buffersize);
    if not databytes: break;
    datasize = len(databytes);
    fulldatasize = datasize + fulldatasize;
    percentage = "";
    if(downloadsize>0):
     percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
    downloaddiff = fulldatasize - prevdownsize;
    log.info("Downloading "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Downloaded "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
    prevdownsize = fulldatasize;
    f.write(databytes);
   f.close();
  geturls_text.close();
  exec_time_end = time.time();
  log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to download file.");
  returnval.update({'Filesize': os.path.getsize(tmpfilename), 'DownloadTime': float(exec_time_start - exec_time_end), 'DownloadTimeReadable': hms_string(exec_time_start - exec_time_end)});
  return returnval;

if(not havemechanize):
 def download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize=524288, sleep=-1):
  returnval = download_from_url_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, sleep)
  return returnval;

if(havemechanize):
 def download_from_url_to_file_with_mechanize(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  global geturls_download_sleep;
  if(sleep<0):
   sleep = geturls_download_sleep;
  if(not outfile=="-"):
   outpath = outpath.rstrip(os.path.sep);
   filepath = os.path.realpath(outpath+os.path.sep+outfile);
   if(not os.path.exists(outpath)):
    os.makedirs(outpath);
   if(os.path.exists(outpath) and os.path.isfile(outpath)):
    return False;
   if(os.path.exists(filepath) and os.path.isdir(filepath)):
    return False;
   pretmpfilename = download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   log.info("Moving file "+tmpfilename+" to "+filepath);
   exec_time_start = time.time();
   shutil.move(tmpfilename, filepath);
   exec_time_end = time.time();
   log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to move file.");
   if(os.path.exists(tmpfilename)):
    os.remove(tmpfilename);
   returnval = {'Type': "File", 'Filename': filepath, 'Filesize': downloadsize, 'FilesizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]=="2"):
   pretmpfilename = download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = StringIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  if(outfile=="-" and sys.version[0]>="3"):
   pretmpfilename = download_from_url_file_with_mechanize(httpurl, httpheaders, httpcookie, buffersize[0], sleep);
   tmpfilename = pretmpfilename['Filename'];
   downloadsize = os.path.getsize(tmpfilename);
   fulldatasize = 0;
   prevdownsize = 0;
   exec_time_start = time.time();
   with open(tmpfilename, 'rb') as ft:
    f = BytesIO();
    while True:
     databytes = ft.read(buffersize[1]);
     if not databytes: break;
     datasize = len(databytes);
     fulldatasize = datasize + fulldatasize;
     percentage = "";
     if(downloadsize>0):
      percentage = str("{0:.2f}".format(float(float(fulldatasize / downloadsize) * 100))).rstrip('0').rstrip('.')+"%";
     downloaddiff = fulldatasize - prevdownsize;
     log.info("Copying "+get_readable_size(fulldatasize, 2, "SI")['ReadableWithSuffix']+" / "+get_readable_size(downloadsize, 2, "SI")['ReadableWithSuffix']+" "+str(percentage)+" / Copied "+get_readable_size(downloaddiff, 2, "IEC")['ReadableWithSuffix']);
     prevdownsize = fulldatasize;
     f.write(databytes);
    f.seek(0);
    fdata = f.getvalue();
    f.close();
    ft.close();
    os.remove(tmpfilename);
    exec_time_end = time.time();
    log.info("It took "+hms_string(exec_time_start - exec_time_end)+" to copy file.");
   returnval = {'Type': "Content", 'Content': fdata, 'Contentsize': downloadsize, 'ContentsizeAlt': {'IEC': get_readable_size(downloadsize, 2, "IEC"), 'SI': get_readable_size(downloadsize, 2, "SI")}, 'DownloadTime': pretmpfilename['DownloadTime'], 'DownloadTimeReadable': pretmpfilename['DownloadTimeReadable'], 'MoveFileTime': float(exec_time_start - exec_time_end), 'MoveFileTimeReadable': hms_string(exec_time_start - exec_time_end), 'Headers': pretmpfilename['Headers'], 'URL': pretmpfilename['URL'], 'Code': pretmpfilename['Code']};
  return returnval;

if(not havemechanize):
 def download_from_url_to_file_with_mechanize(httpurl, httpheaders, httpcookie, outfile="-", outpath=os.getcwd(), buffersize=[524288, 524288], sleep=-1):
  returnval = download_from_url_to_file_with_urllib(httpurl, httpheaders, httpcookie, buffersize, outfile, outpath, sleep)
  return returnval;

def download_file_from_ftp_file(url):
 urlparts = urlparse.urlparse(url);
 file_name = os.path.basename(urlparts.path);
 file_dir = os.path.dirname(urlparts.path);
 if(urlparts.username is not None):
  ftp_username = urlparts.username;
 else:
  ftp_username = "anonymous";
 if(urlparts.password is not None):
  ftp_password = urlparts.password;
 elif(urlparts.password is None and urlparts.username=="anonymous"):
  ftp_password = "anonymous";
 else:
  ftp_password = "";
 if(urlparts.scheme=="ftp"):
  ftp = FTP();
 elif(urlparts.scheme=="ftps"):
  ftp = FTP_TLS();
 else:
  return False;
 ftp.connect(urlparts.hostname, urlparts.port);
 ftp.login(urlparts.username, urlparts.password);
 if(urlparts.scheme=="ftps"):
  ftp.prot_p();
 ftpfile = BytesIO();
 ftp.retrbinary("RETR "+urlparts.path, ftpfile.write);
 #ftp.storbinary("STOR "+urlparts.path, ftpfile.write);
 ftp.close();
 ftpfile.seek(0, 0);
 return ftpfile;

def download_file_from_ftp_string(url):
 ftpfile = download_file_from_ftp_file(url);
 return ftpfile.read();

def upload_file_to_ftp_file(ftpfile, url):
 urlparts = urlparse.urlparse(url);
 file_name = os.path.basename(urlparts.path);
 file_dir = os.path.dirname(urlparts.path);
 if(urlparts.username is not None):
  ftp_username = urlparts.username;
 else:
  ftp_username = "anonymous";
 if(urlparts.password is not None):
  ftp_password = urlparts.password;
 elif(urlparts.password is None and urlparts.username=="anonymous"):
  ftp_password = "anonymous";
 else:
  ftp_password = "";
 if(urlparts.scheme=="ftp"):
  ftp = FTP();
 elif(urlparts.scheme=="ftps"):
  ftp = FTP_TLS();
 else:
  return False;
 ftp.connect(urlparts.hostname, urlparts.port);
 ftp.login(urlparts.username, urlparts.password);
 if(urlparts.scheme=="ftps"):
  ftp.prot_p();
 ftp.storbinary("STOR "+urlparts.path, ftpfile);
 ftp.close();
 ftpfile.seek(0, 0);
 return ftpfile;

def upload_file_to_ftp_string(ftpstring, url):
 ftpfileo = BytesIO(ftpstring);
 ftpfile = upload_file_to_ftp_file(ftpfileo, url);
 ftpfileo.close();
 return ftpfile;

if(haveparamiko):
 def download_file_from_sftp_file(url):
  urlparts = urlparse.urlparse(url);
  file_name = os.path.basename(urlparts.path);
  file_dir = os.path.dirname(urlparts.path);
  sftp_port = urlparts.port;
  if(urlparts.port is None):
   sftp_port = 22;
  else:
   sftp_port = urlparts.port;
  if(urlparts.username is not None):
   sftp_username = urlparts.username;
  else:
   sftp_username = "anonymous";
  if(urlparts.password is not None):
   sftp_password = urlparts.password;
  elif(urlparts.password is None and urlparts.username=="anonymous"):
   sftp_password = "anonymous";
  else:
   sftp_password = "";
  if(urlparts.scheme!="sftp"):
   return False;
  ssh = paramiko.SSHClient();
  ssh.load_system_host_keys();
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
  try:
   ssh.connect(urlparts.hostname, port=sftp_port, username=urlparts.username, password=urlparts.password);
  except paramiko.ssh_exception.SSHException:
   return False;
  sftp = ssh.open_sftp();
  sftpfile = BytesIO();
  sftp.getfo(urlparts.path, sftpfile);
  sftp.close();
  ssh.close();
  sftpfile.seek(0, 0);
  return sftpfile;
else:
 def download_file_from_sftp_file(url):
  return False;

if(haveparamiko):
 def download_file_from_sftp_string(url):
  sftpfile = download_file_from_sftp_file(url);
  return sftpfile.read();
else:
 def download_file_from_ftp_string(url):
  return False;

if(haveparamiko):
 def upload_file_to_sftp_file(sftpfile, url):
  urlparts = urlparse.urlparse(url);
  file_name = os.path.basename(urlparts.path);
  file_dir = os.path.dirname(urlparts.path);
  sftp_port = urlparts.port;
  if(urlparts.port is None):
   sftp_port = 22;
  else:
   sftp_port = urlparts.port;
  if(urlparts.username is not None):
   sftp_username = urlparts.username;
  else:
   sftp_username = "anonymous";
  if(urlparts.password is not None):
   sftp_password = urlparts.password;
  elif(urlparts.password is None and urlparts.username=="anonymous"):
   sftp_password = "anonymous";
  else:
   sftp_password = "";
  if(urlparts.scheme!="sftp"):
   return False;
  ssh = paramiko.SSHClient();
  ssh.load_system_host_keys();
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
  try:
   ssh.connect(urlparts.hostname, port=sftp_port, username=urlparts.username, password=urlparts.password);
  except paramiko.ssh_exception.SSHException:
   return False;
  sftp = ssh.open_sftp();
  sftp.putfo(sftpfile, urlparts.path);
  sftp.close();
  ssh.close();
  sftpfile.seek(0, 0);
  return sftpfile;
else:
 def upload_file_to_sftp_file(sftpfile, url):
  return False;

if(haveparamiko):
 def upload_file_to_sftp_string(sftpstring, url):
  sftpfileo = BytesIO(sftpstring);
  sftpfile = upload_file_to_sftp_files(ftpfileo, url);
  sftpfileo.close();
  return sftpfile;
else:
 def upload_file_to_sftp_string(url):
  return False;
