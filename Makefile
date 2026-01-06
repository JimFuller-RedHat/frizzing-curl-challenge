build-zoo:
	podman build -t curl-zoo -f Containerfile.ProtocolPettingZoo --tag curl-zoo
build-custom-curl:
	podman build -t custom_curl -f Containerfile.CustomCurl .
build: build-zoo, build-custom-curl

play-simple-http-submission:
	python judge_submission.py example_submissions/simple_http

play-h2-submission:
	python3 judge_submission.py example_submissions/h2_exploit \
		--command "--http2-prior-knowledge -v http://localhost:{port}"

play-mqtt-submission:
	python3 judge_submission.py example_submissions/mqtt_exploit \
  		--port 1883 \
  		--command "mqtt://localhost:{port}/test"

play-smtp-submission:
	python3 judge_submission.py example_submissions/smtp_exploit \
  		--port 2525 \
  		--command "smtp://localhost:{port} --mail-from pwn@example.com --mail-rcpt root@localhost"

play-gopher-submission:
	python3 judge_submission.py example_submissions/gopher_exploit \
		--port 70 \
		--command "gopher://localhost:{port}/1"

play-telnet-submission:
	python3 judge_submission.py example_submissions/telnet_exploit \
		--port 23 \
		--command "telnet://localhost:{port}/1"

play-dict-submission:
	python3 judge_submission.py example_submissions/dict_exploit \
		--port 2628 \
		--command "-vvv dict://localhost:{port}/word"

play-example-submissions: play-simple-http-submission play-h2-submission play-mqtt-submission play-smtp-submission play-gopher-submission play-telnet-submission play-dict-submission

play-with-official-curl:
	python judge_submission.py example_submissions/simple_http

play-with-custom-built-curl:
	python judge_submission.py --victim localhost/custom_curl example_submissions/simple_http

run-zoo:
	podman run --rm -d --name zoo \
  -p 8080:80 \
  -p 8443:443 \
  -p 2121:21 \
  -p 2222:2222 \
  -p 1883:1883 \
  -p 2323:23 \
  -p 6969:69/udp \
  localhost/curl-zoo
