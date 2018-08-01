* To build func for lambda deployment:
mkdir tempfunc
cp rss2email.py tempfunc
(cd tempfunc && pip install -r ../requirements -t `pwd` && zip ../rss2email.zip -r *)

* Required environment variables:
FROM_EMAIL: email to send to (e.g. vulns@latacora.com)
TO_EMAIL: email to send from (e.g. vulnsource@latacora.com)
FEEDS: comma separated list of RSS feeds to parse (e.g. https://aws.amazon.com/security/security-bulletins/feed/,https://snyk.io/vuln/feed.xml?type=npm,https://snyk.io/vuln/feed.xml?type=maven,https://snyk.io/vuln/feed.xml?type=pip,http://www.oracle.com/ocom/groups/public/@otn/documents/webcontent/rss-otn-sec.xml)
INTERVAL: (optional) the frequency this will run at - prevents sending a spate of email the first time an RSS file is inspected as well
S3BUCKET: a bucket the lambda has list/read/write access to.
PREAMBLE: (optional) a string to preface all sent email subjects with

This lambda should be deployed as a scheduled event.  It'll default to 60

* Required IAM policy:
AWSLambdaBasicExecutionRole, read/write/list on an s3 bucket, ses:SendEmail and ses:SendRawEmail: