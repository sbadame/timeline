# Aggregate information from email.

## Email integration

1. Create an app specific password for gmail https://security.google.com/settings/security/apppasswords
1. Create a file in configs/config.json

```javascript
{
  "login": "",   // GMAIL login
  "subject": "", // Subject to search for
  "password": "" // App specific password
}
```

## Drive integration

1. Read https://developers.google.com/drive/web/about-auth
1. Get a credential
1. Put it into configs/drive.key


## The workflow

* This code is written for python 3.5 You probably want virtualenv. requirements.txt is included so that you can easily install the required packages. My .gitignore hints that I have virtualenv setup in a venv folder. A quickstart for this project is:

```bash
virtualenv venv # Do this once.
source venv/bin/activate # Before developing, activate virtual env. Do this in every shell you run python in.
pip install requirements.txt # Do this the first time, and whenever requirements.txt changes.
# hack... hack... hack...
deactivate # undo the activate from before.
```

### The data translations

The scripts are super hacky. They output to STDOUT but assume a constant input so:

* `python email_script.py > email_script.json` Downloads the emails and attachments, converts them to json and dumps them.
* `python massage.py > massage.json` Reads email_script.json (The file path is hardcoded.) and makes the json more
  usable for a UI.
* `python -m http.server` Hosts <http://localhost:8000/src/timeline.html> and expects massage.json (The file path is hardcoded.) and renders the json data into a webpage.
