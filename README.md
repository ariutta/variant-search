# variant-search

A genomic variant web application that allows a user to search for genomic variants based on a gene name and display the results in a tabular view.

## Install

Install dependencies:
* PostgreSQL
* Python3, with packages `Flask`, `requests`, `requests_cache`, `psycopg2` and `stringcase`
* Node.js (`npm install`)

Create and load database: `python build.py`

Start servers:
Backend:
```
export FLASK_APP=server.py
python3 -m flask run
```
Frontend: `npm run start`

## Test

Backend: `python server.test.py`
Frontend: `npm run test`

## Data

The "Other Mappings" fields contain comma-separated values. They may contain both nucleotide and protein changes. Example:
`"NM_000762.5:c.479T>A,NG_008377.1:g.6820T>A,NC_000019.10:g.40848628A>T,NC_000019.9:g.41354533A>T,NP_000753.3:p.Leu160His"`

The More Info fields for rows with Source of "EmvClass" use URLs of this format:
http://genetics.emory.edu/egl/emvclass/emvclass.php?approved_symbol=OAT

But those URLs are broken. They should be updated to use this format:
https://www.egl-eurofins.com/emvclass/emvclass.php?approved_symbol=OAT

For Protein Change, should values like "p.=", "p.?", "-" and "p.(=)" be parsed as null?

## Server

Endpoints:
1. /suggestions?gene=OAT
  * Input two or more letters
  * Get back a list of matching gene names
2. /variants?gene=OAT
  * Input a gene name
  * Get back a table of details

Database tables:
* Gene names, indexed to allow suggestions
* Reported classifications
* Inferred Classifications
* Sources
* Variants (one per row of source data)

## Front-End

1. Gene name typeahead
2. Gene details table

## Notes and Future Improvements

* The autocomplete currently makes a request to the server every time the user types into the field beyond the first two characters. But once we've gotten the data based on the first two characters, we could avoid extra server requests by matching further characters in the browser in JS.
* The front-end tests are currently MINIMAL. They should be expanded.
* In production, we would not want to use the React dev server. We would compile the JS, including minifying it, and serve it as a static asset. We would also likely place the flask server behind Nginx, possibly additionally with a cache like Varnish.
* Since this is a very simple app, I didn't use Redux, but if it gets more complicated, Redux could become necessary.
* If the current system is too slow, we could look at speeding it up by de-normalizing data in PostgreSQL or even adding an additional persistence layer, possibly in the form of an ElasticSearch instance. ElasticSearch would index the relevant queries and return one document corresponding to the data in the variants table per each gene.
