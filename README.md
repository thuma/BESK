# BESK - Kodcentrum - Attendance system
<img src="https://github.com/thuma/BESK/blob/master/static/img/BESK.png" height="64" alt="BESK">
<img src="https://github.com/thuma/BESK/blob/master/static/img/kodcentrum-logo.svg" height="64" alt="kodcentrum">

Handle applications for and attendance on the Kodcentrum kodstugor.

## Getting Started

Clone and run the main file:

```
git clone git@github.com:thuma/BESK.git
cd BESK
python main.py
```

### Prerequisites

You need to get the python modules in the requirements.txt file:

```
pip install -r requirements.txt
```

You need to set up a BESK.ini file:

```
[general]
admins = test@test.com,<YOUR-EMAIL>

[slack]
redirect_uri = http://localhost:9191/login
client_id = <SLACK_CLIENT_ID>
client_secret = <SLACK_SECRET>
token = <SLACK_TOKEN>

[office365]
email=<FROM_EMAIL>
password=<O365_PASSWORD>

[46elks]
username = <46ELKS_API_USERNAME>
password = <46ELKS_API_PASSWORD>
```

For local testing you need to fill out:

<YOUR-EMAIL>, the email you use to login to slack.

<SLACK_CLIENT_ID> & <SLACK_SECRET>,
    1. Create an app for slack at [https://api.slack.com/apps](https://api.slack.com/apps).
    2. Click **Create New App** then select **Kodecetrum Sverige** as **Development Slack Workspace**.
    3. Add premisions this is done by **Add features and functionality** and then **Permissions**,
    4. Add **http://localhost:9191/login** to **Redirect URLs**.
    5. **Add Scopes** for **Bot Token Scopes**  add the scopes **users:read**, **users:read.email**.
    6. Finaly klick **Install App to Workspace**, confirm and get the <SLACK_TOKEN> from the field.

<46ELKS_API_USERNAME> & <46ELKS_API_PASSWORD>
Get account for [46elks](https://46elks.com) and get the API password and user name.

For local testing just leave <FROM_EMAIL> & <O365_PASSWORD> they are not needed for local testing. 

### Testing

Use pytest to run tests on the project:

```
pytest
```

## Deploy

```
./deploy.sh
```

## Production setup

* [Glesys](https://www.glesys.se) KVM VPS.
* [Debian](https://www.debian.org/) as server OS.
* [OpenSSH](https://www.openssh.com/) Remote access key auth only, no password.
* [Postfix](http://www.postfix.org/) for mail sending, TLS enabled, local access only.
* [Systemd](https://www.freedesktop.org/wiki/Software/systemd/) for running the BESK server.
* [NGINX](https://nginx.org/en/) https and reverse proxy.
* [Let’s Encrypt](https://letsencrypt.org/) for free SSL cert.
* [Certbot](https://certbot.eff.org/) automatic update of SSL cert.
* [Cron](https://www.gnu.org/software/mcron/) for automatic automatic backup.

## Production server

```
cd ansible
ansible-playbook besk.yml
```

<p>
Glesys stöttar Kodcentrum med en VPS för BESK.
Glesys erbjuder IT-infrastruktur som tjänst (IaaS) inom branscher med höga 
krav på tillgänglighet och upptid, som e-handel och cybersäkerhet.
De äger och driftar två egna datacenter, i Falkenberg och Stockholm.
Du kan själv testa deras 
<a href="https://glesys.se/vps">Cloud VPS från 60 kr/mån</a>. 
</p>
<p>
    <i>
    Som en av Sveriges ledande hostingleverantörer är vi glada över att 
    kunna stötta Kodcentrum i arbetet med att låta barn och ungdomar 
    utvecklas inom programmering och att vi tillsammans säkrar 
    framtidens behov av kompetens inom IT-branschen. 
    - Petter Knutsson, Marknadsansvarig
    </i>
</p>

## Built With

### Backend
* [Python 3](https://www.python.org/) - Programming language.
* [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) - Python Library port of Google's libphonenumber library.
* [arrow](https://arrow.readthedocs.io/en/latest/) - Sensible and human-friendly for dates and times.
* [markdown](https://python-markdown.github.io/#features) - Python implementation of John Gruber’s Markdown.
* [Sqlite3](https://www.sqlite.org) - SQLite database engine.
* [Requests](https://3.python-requests.org/) - HTTP for Humans and Machines, alike.
* [Gevent](http://www.gevent.org/) - Coroutine based Python networking library.

### GUI
* [Bootstrap](https://getbootstrap.com/) -  Responsive toolkit for HTML and CSS. (Using [jQuery](https://jquery.com/))
* [SweetAlert](https://sweetalert.js.org/) - A beautiful replacement for alert.
* [Showdown](http://showdownjs.com/) - A Markdown to HTML bidirectional converter.
* [Vue.js](http://www.vuejs.org/) - Reactive render engine.

## Code info

* 4 spaces indentation
* POST/DELETE/GET data format application/x-www-form-urlencoded
* Response format 200 OK JSON
* Response format !200 OK plain/text with error message.
* GUI get full list from server on every update.
* Login with slack account.

## Code guidelines

* [PEP 8](https://www.python.org/dev/peps/pep-0008/)

## Authors

* **Martin Harari Thuresson**

## License

This project is licensed under the GNU General Public License 3 - see the [LICENSE](LICENSE) file for details
