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
[general]
email_key=<key for email api>
email_url=<url for email api>
admin_user=<inital admin email>
[slack]
redirect_uri=http://localhost:9191/login
client_id=476744412819.789508806369
client_secret=<slack secret key for login verification>
```

## Built With

* [Python 3](https://www.python.org/) - Programming language.
* [Bootstrap](https://getbootstrap.com/) -  Responsive toolkit for HTML and CSS. (Using [jQuery](https://jquery.com/))
* [Sqlite3](https://www.sqlite.org) - SQLite database engine.
* [Requests](https://3.python-requests.org/) - HTTP for Humans and Machines, alike.
* [Gevent](http://www.gevent.org/) - Coroutine based Python networking library.

## Code laws

* 4 spaces indentation

## Code guidelines

* [PEP 8](https://www.python.org/dev/peps/pep-0008/)

## Authors

* **Martin Harari Thuresson**

## License

This project is licensed under the GNU General Public License 3 - see the [LICENSE.md](LICENSE.md) file for details
