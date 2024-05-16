# aha-auto-test

### Install Docker

- #### Download: 
https://www.docker.com/get-started/
- #### Ubuntu follow this page: 
https://docs.docker.com/engine/install/ubuntu/ 

<br/>

### Apply Slack and SendGrid API

- #### Slack api: 
https://api.slack.com/
- #### Slack api set up follow this page: 
https://www.datacamp.com/tutorial/how-to-send-slack-messages-with-python
- #### SendGrid api: 
https://sendgrid.com/en-us/solutions/email-api

<br/>

### Edit Config File

- #### Fill in the API token and parameters into the config 
config/UI_TEST_setting_config.yaml

- #### Fill in the email and password for testing into the config.
config/UI_TEST_setting_config.yaml

<br/>

### Build Docker Images

> docker build -t auto-test .
<br/>

### Run Docker Container

> docker run -it --cpuset-cpus=[cpu number] -v [local path]:/app/log auto-test

- #### Example:
> docker run -it --cpuset-cpus="0-4" -v ./log:/app/log auto-test
