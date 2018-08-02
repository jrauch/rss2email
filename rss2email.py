import feedparser
import datetime
import dateutil.parser
from os import environ
import json
import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import requests
from hashlib import sha256
#from ipdb import set_trace

def send_email(email):
	msg = MIMEMultipart()
	msg['Subject'] = email["subject"]
	msg["From"] = email["from"]
	msg["To"] = email["to"]
	msg.preamble = "Multipart message.\n"
	part = MIMEText(email["body"], "html")
	msg.attach(part)

	client = boto3.client("ses")
	return client.send_raw_email(RawMessage = {'Data':msg.as_string()}, 
		Source=msg["From"], 
		Destinations = [ x.strip() for x in msg["To"].split(",")])

def rss_to_email_handler(event, context):
	feeds = [ x.strip() for x in environ.get("FEEDS").split(',')]

	interval = environ.get("INTERVAL") # this acts as a first-run break - I don't want to see things since the beginning of time.
	interval = 360 if not interval else int(interval)

	preamble = environ.get("PREAMBLE")
	preamble = "" if not preamble else preamble

	bucketname = environ.get("S3BUCKET")
	bucketname = "REPLACEME-rss2email" if not bucketname else bucketname

	time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=interval)
	lastrun = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
	email = {}
	email["from"] = environ.get("FROM_EMAIL")
	email["to"] = environ.get("TO_EMAIL")
	s3 = boto3.client("s3")

	for feed in feeds:
		print(feed)
		f = requests.get(feed)
		print(f.status_code)
		if f.status_code == 200:
			d = feedparser.parse(f.text)

			old_feed_hash = sha256(feed.encode("utf-8")).hexdigest()
			response = s3.list_objects_v2(Bucket=bucketname, Prefix=old_feed_hash)
			#set_trace()
			if response["KeyCount"] > 0:
				old_feed_contents = s3.get_object(Bucket=bucketname, Key=old_feed_hash)
				old_feed = feedparser.parse(old_feed_contents["Body"].read())
				old_feed_index = {}
				for entry in old_feed.entries:
					old_feed_index[entry.title] = entry.link # if the subject and link are the same, they're the same 8)
			else:
				old_feed_index = {}

			for entry in d.entries:
				if "published" in entry:
					pubdate = dateutil.parser.parse(entry.published)
				elif "updated" in entry:
						pubdate = dateutil.parser.parse(entry.updated)
				else:
					continue
				if entry.title not in old_feed_index or old_feed_index[entry.title] != entry.link:
					if len(old_feed_index) > 0 or pubdate > time: 
						email["subject"] = "{}{}".format(preamble,entry.title)
						email["body"] = "{} (details at: {})".format(entry.summary if "summary" in entry else "", entry.link)
						print("{} {} {}".format(email["subject"], pubdate, time))
						send_email(email)
					else:
						#set_trace()
						print("timeout {}".format(time-pubdate))

			s3.put_object(Bucket=bucketname, Key=old_feed_hash, Body=f.text)

if __name__ == "__main__":
	print("hi")
	rss_to_email_handler(None, None)
