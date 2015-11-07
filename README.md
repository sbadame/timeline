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

The scripts are super hacky and assume the following workflow:

* Before developing, activate virtual env:
```bash
source venv/bin/activate
```

* If this is your first time, you'll need to install the python packages
```bash
pip install requirements.txt
```

### The data translations

The scripts are super hacky. They output to STDOUT but assume a constant input so:

* `python email_script.py > email_script.json` Downloads the emails and attachments, converts them to json and dumps them.
* `python massage.py > massage.json` Reads email_script.json (The file path is hardcoded.) and makes the json more
  usable for a UI.
* `python -m http.server` Hosts <http://localhost:8000/src/timeline.html> and expects massage.json (The file path is hardcoded.) and renders the json data into a webpage.
