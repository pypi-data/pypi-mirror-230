SermonAudio.com API Client Library
==================================

This is the official Python client library for accessing the latest
[SermonAudio.com](http://www.sermonaudio.com/) APIs.

For documentation on the SermonAudio API, head to
[api.sermonaudio.com](http://api.sermonaudio.com/). Proper Python type
conversions have been made where appropriate (for example, dates are converted
to `datetime.date` objects). API functions are grouped into modules by API
family, just as in the main documentation (so Node API endpoint helpers are
in the `node` module). Endpoint request methods are given an appropriate
prefix such as `get`.

Detailed documentation is included with each method. If you have any questions
about how to use these methods, or feel the docstrings could be improved,
send a message to developer@sermonaudio.com.

Installation Notes
------------------

This library is written in Python 3.6+. Please ensure that you have the latest
version of OpenSSL installed. If you are on a Mac, you may need to use
[homebrew](http://brew.sh) to install a new verison of python linked against
the updated version via `brew install python3 --with-brewed-openssl`.
Unfortunately, older versions of OpenSSL do not support TLSv1.2. Older versions
have known security holes, so our server will refuse such connections.
Make sure to use the new (brewed) version of python for your virtual environment.

Quickstart
----------

The API functions are straightforward. All API methods validate the response
from the server, and return a logical value from the wrapped response, or throw
an exception. For example, a node that returns a single result will return only
the first item in the results list, if one exists. Additionally, the object(s)
returned are mapped to the correct type of object. Here are some code samples
to get you started.

```
import sermonaudio

from sermonaudio.node.requests import Node

# You must set your API key before making any requests
sermonaudio.set_api_key('YOUR-API-KEY')

sermon = Node.get_sermon('261601260')
# TODO: Something with this sermon

for sermon in Node.get_sermons(broadcaster_id='faith').results:
    # TODO: Something with each sermon in the list
    pass
```

All methods have docstrings, so you can refer to this documentation as you
write your application. We do encourage you to read the full documentation
referenced above for the most complete, up to date details.

Localization
------------

While our localization project is still in its early stages, this client
library is aware of the support. In general, it should "just work" if we support
your language and key strings will be localized server-side. However, if you are
running in an environment with a different locale than your users, you can override
the preferred language either globally or per-request. You can override it globally
using the top-level `set_preferred_language` function. All request methods also accept a
`preferred_language_override` keyword argument so you can override this globally. The
are passed via the HTTP `Accept-Language` header, and should follow that format.
For example, `en-US` for US English.
