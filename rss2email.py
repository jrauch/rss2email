import feedparser
import datetime
import dateutil.parser
from os import environ
import json
import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

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

	time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=60)
	lastrun = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
	email = {}
	email["from"] = environ.get("FROM_EMAIL")
	email["to"] = environ.get("TO_EMAIL")

	for feed in feeds:
		print(feed)
		d = feedparser.parse(feed, modified=lastrun)
		
		if d.status == 200:
			for entry in d.entries:
				if "published" in entry:
					pubdate = dateutil.parser.parse(entry.published)
				elif "updated" in entry:
						pubdate = dateutil.parser.parse(entry.updated)
				else:
					continue
				if pubdate > time:
					email["subject"] = "[r2e] {}".format(entry.title)
					email["body"] = "{} (details at: {})".format(entry.summary if "summary" in entry else "", entry.link)
					print("{} {}".format(email["subject"],email["body"]))
					send_email(email)

if __name__ == "__main__":
	rss_to_email_handler(None, None)
