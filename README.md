# BESK - Kodcentrum - Attendance system
<img src="https://github.com/thuma/BESK/blob/master/static/img/BESK.png" height="64" alt="BESK">
<img src="https://github.com/thuma/BESK/blob/master/static/img/kodcentrum-logo.svg" height="64" alt="kodcentrum">

Handle applications for and attendance on the Kodcentrum kodstugor.

## Getting Started

Clone and run the main file:

```
python main.py
```

### Prerequisites

You need to get the python modules in the requirements.txt file:

```
pip install -r requirements.txt
```

You need to set up a BESK.ini file:

```
[slack]
redirect_uri=http://localhost:9191/login
client_id=476744412819.789508806369
client_secret=<slack secret key for login verification>
token=<slack secret token for interactivity with slack>
[46elks]
username=<46elks username>
password=<46elks password>
```

## Production setup:

* [Glesys](https://www.glesys.se) KVM server.
* [Debian](https://www.debian.org/) as server OS.
* [OpenSSH](https://www.openssh.com/) Remote access key auth only, no password.
* [Postfix](http://www.postfix.org/) for mail sending, TLS enabled, local access only.
* [Systemd](https://www.freedesktop.org/wiki/Software/systemd/) for running the BESK server.
* [NGINX](https://nginx.org/en/) https and reverse proxy.
* [Let’s Encrypt](https://letsencrypt.org/) for free SSL cert.
* [Certbot](https://certbot.eff.org/) automatic update of SSL cert.
* [Cron](https://www.gnu.org/software/mcron/) for automatic automatic backup.

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
