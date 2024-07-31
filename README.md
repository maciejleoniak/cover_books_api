# Cover books API
## What is it?

A service for interacting with the Google Books API to search for books by ISBN and save book thumbnails to a local JSON file with caching capabilities.


## How to:
### for windows:

`python -m venv venv`

`venv\Scripts\activate`

`pip install -r requirements.txt`

` cd app`

`python app.py`

### for macos:

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

` cd app`

`python app.py`


app run on port 5050

### example of usage:
`http://127.0.0.1:5050/get_book_cover?isbn=9781259642197`

### isbn example:
`
    "9780323393041",
    "9780323793759",
    "9781975154066",
    "9781259644030",
    "9780702070280",
    "9780323597128",
    "9781975160432",
    "9781496398178",
    "9780702069932",
    "9780071794763",
    "9780323529501",
    "9780071796750",
    "9781259642197",
    "9781451188805",`
