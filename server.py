import datetime
from flask import Flask, request
import json
import psycopg2
from collections import OrderedDict

app = Flask(__name__)

VARIANT_DBNAME = 'variant_search'

serialize_date = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)

conn = psycopg2.connect(dbname=VARIANT_DBNAME)

# curl http://127.0.0.1:5000/suggestions?gene=OA
@app.route('/suggestions')
def show_suggestions():
    gene = request.args.get('gene').upper()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT name
        FROM genes
        WHERE name LIKE %s
        ORDER BY name ASC;
        """,
        (gene + '%',)
    )
    results = []
    for row in cur.fetchall():
        results.append(row[0])
    cur.close()
    return json.dumps(results)

# curl http://127.0.0.1:5000/variants?gene=OAT
@app.route('/variants')
def show_variants():
    gene = request.args.get('gene').upper()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT genes.name, nucleotide_change, protein_change, alias, region,
            reported_classifications.name, last_evaluated, last_updated, url
        FROM variants
        INNER JOIN genes ON variants.gene_id = genes.id
        INNER JOIN reported_classifications
          ON variants.reported_classification_id = reported_classifications.id
        WHERE genes.name = %s
        ORDER BY genes.name,nucleotide_change,protein_change ASC;
        """,
        (gene,)
    )
    columns = (
        'Gene', 'Nucleotide Change', 'Protein Change', 'Alias', 'Region',
        'Reported Classification', 'Last Evaluated',
        'Last Updated', 'More Info'
    )
    results = []
    for row in cur.fetchall():
        results.append(OrderedDict(zip(columns, row)))
    cur.close()
    return json.dumps(results, default=serialize_date)
