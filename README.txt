* To build func for lambda deployment:
mkdir tempfunc
cp rss2email.py tempfunc
(cd tempfunc && pip install -r ../requirements -t `pwd` && zip ../rss2email.zip -r *)

* Required environment variables:
FROM_EMAIL: email to send to (e.g. vulns@latacora.com)
TO_EMAIL: email to send from (e.g. vulnsource@latacora.com)
FEEDS: comma separated list of RSS feeds to parse
INTERVAL: (optional) the frequency this will run at

This lambda should be deployed as a scheduled event.  It'll default to 60

* Required IAM policy:
AWSLambdaBasicExecutionRole plus:

{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":[
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource":"*"
    }
  ]
}
