# 'Frizzing Curl' Challenge

_Definition_:
   
      'Frizzing': human directed fuzzing of curl.

## Can you break curl ?

[Curl](https://curl.se) is a command line tool (and library) for transferring data with URL syntax, supporting DICT, FILE, FTP, FTPS, GOPHER, GOPHERS, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, POP3, POP3S, RTMP, RTMPS, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET, TFTP, WS and WSS and so on ...

Breaking **curl** is a _dance_ between **curl** and whatever protocol and server it is interfacing with ... this usually means
setting up a server and invoke curl to communicate with that server. 

## Requirements
* clone this [repo](https://github.com/JimFuller-RedHat/frizzing-curl-challenge)
* [podman](https://podman.io/)
* python

then build containers:
```commandline
cd frizzing-curl-challenge
make build
```

## How to play ?

First review curl [vulnerability disclosure page](https://curl.se/dev/vuln-disclosure.html) which gives a good 
overview of how vulnerabilities are handled, what we consider are real vulnerabilities.

Now review how the game is played by looking at a player [example submissions](example_submissions) and run one

```commandline
> make play-h2-submission
```
 or run directly

```commandline
python3 judge_submission.py example_submissions/h2_exploit \
		--command "--http2-prior-knowledge -v http://localhost:{port}"
```
this python script will ensure submission is built then run and tested if anything crashes/breaks:

```commandline
python3 judge_submission.py example_submissions/h2_exploit \
	--command "--http2-prior-knowledge -v http://localhost:{port}"
******************************* Frizzing curl **************************************
Target: example_submissions/h2_exploit
Curl victim image: quay.io/curl/curl:latest
************************************************************************************
Building player submission from example_submissions/h2_exploit...
Launching Victim (quay.io/curl/curl:latest)
Curl Args: --http2-prior-knowledge -v http://localhost:8080
Curl survived.
```

which indicates curl was not broken and **survived**.

To use a custom curl image (the default is [quay.io/curl/curl:latest](quay.io/curl/curl:latest) use the `--victim` flag: 
```commandline
python3 judge_submission.py example_submissions/h2_exploit \
		--victim localhost/custom_curl \ 
		--command "--http2-prior-knowledge -v http://localhost:{port}"
```
which uses the already built custom curl [image](Containerfile.CustomCurl).

### Create a submission

Crafting a submission usually means defining a server which is built in a way to try and 'break' curl - this can be as simple
as having the server send over unexpected data that curl breaks on ... but as we have had years of fixes its unlikely such 
direct fuzzing will result (we invite you to try and break curl!).

### Judge submission

As with example submission - to judge it run 
```commandline
python3 judge_submission.py my_submissions/myevil_http_exploit \
        --port 80
		--victim localhost/custom_curl \ 
		--command "--http2-prior-knowledge http://localhost:{port}"
```

where --victim denotes custom curl (enabled with sanitizers) and --command is the set of curl commands passed to curl image.

### Did you win ?

There is no reason to play the game ... it is just a bit of fun to help people (who might not normally) start
trying to break curl ;) 

If you think you found something you can reach us at:

* report a curl [bug](https://github.com/curl/curl/issues)
* report a curl [vulnerability](https://hackerone.com/curl)
* [IRC](https://curl.se/docs/irc.html)
* email [curl-users](https://lists.haxx.se/listinfo/curl-users) 

If you really (really) think you broke curl and none of the above work for you then zip up your submission and
email to **security (at curl dot se)**.