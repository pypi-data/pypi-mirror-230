MarkdownMail
============

Purpose
-------

Send e-mails with generated html content.

The content has to be written in Markdown syntax. The text part of the e-mail
will be filled verbatim; the html part will be a converted HTML from the
Markdown content.

![E-mail rendering for the user (HTML part)](https://www.yaal.fr/media/softwares/markdownmail-screenshot.png)

Install
-------

`$ pip install markdownmail`


Basic Usage
-----------

```python
import markdownmail

CONTENT = u"""
SPAMS AND EGGS
==============

This is a demo with a list:

1. Spam
2. Second spam
3. ...and eggs
"""

email = markdownmail.MarkdownMail(
    from_addr=u'alice@example.org',
    to_addr=u'bob@example.org',
    subject=u'MarkdownMail demo',
    content=CONTENT
)

email.send('localhost')
```

Content must be unicode.


More infos
----------

Additional informations are addable:

```python
email = markdownmail.MarkdownMail(
    from_addr=(u'alice@example.org', u'Alice'),
    to_addr=(u'bob@example.org', u'Bob'),
    subject=u'MarkdownMail demo',
    content=CONTENT
)
```

`cc_addr` and `bcc_addr` are optional.
The `from_addr`, `to_addr`, `cc_addr` and `bcc_addr` parameters are the same as
[Enveloppe](http://pypi.org/pypi/Envelopes/) library.


Change SMTP port:

```python
email.send("example.org", port=3325)
```

Change SMTP login and password:

```python
email.send("example.org", login="user", password="password")
```

Use TLS:

```python
email.send("example.org", tls=True)
```

Style
-----

A default CSS is automatically added to the e-mail. It includes a font sans serif and minor improvements.

To override the default CSS, pass a string including the style to the `css` optional parameter of `MardownMail`:

```python
import markdownmail

email = markdownmail.MarkdownMail(
    from_addr=u'alice@example.org',
    to_addr=u'bob@example.org',
    subject=u'MarkdownMail demo',
    content="CONTENT",
    css="font-family:monospace; color:green;"
)
```

Run tests
---------

Tox is automatically installed in virtualenvs before executing the tests.
Execute them with:

`$ python setup.py test`


Disable sending e-mails in your tests
-------------------------------------

The e-mail is not send if the parameter passed to `send()` method is an instance of `NullServer`.

```python
email = markdownmail.MarkdownMail(
    #params
)

email.send(markdownmail.NullServer())
```

Assert about e-mails in your tests
----------------------------------

Subclassing `NullServer` allows to provide a custom behaviour in the `check()`
method:

```python
class MyServer(markdownmail.NullServer):
    def check(self, email):
        assert u'bob@example.org' == email.to_addr[0]

email.send(MyServer())
```


Useful links
------------

[Envelopes library](https://pypi.org/pypi/Envelopes/0.4)
(MardownMail is a wrapper around Envelopes library.)

[Markdown syntax](https://daringfireball.net/projects/markdown/syntax)
