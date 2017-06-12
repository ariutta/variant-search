import csv
from datetime import timedelta
import io
import psycopg2
import requests
import requests_cache
import stringcase
import zipfile

VARIANTS_DATASET_URL = 'http://clinvitae.invitae.com/download'
ADMIN_DBNAME = 'postgres'
VARIANT_DBNAME = 'variant_search'
expire_after = timedelta(weeks=4)
requests_cache.install_cache(
    cache_name='variant_search_cache',
    backend='sqlite',
    expire_after=expire_after)

# NOTE use this if you need to set these values
# import getpass
# username = getpass.getuser()
# password = getpass.getpass('Password:')


def snakecase_keys(d):
    snakecased_d = {}
    for key, value in d.items():
        # NOTE: we want to convert from 'Title Case' to 'snake_case', but
        # the stringcase library doesn't do exactly what we need.
        # Expected stringcase result (just one underscore):
        #   stringcase.snakecase('Hello World') # => 'hello_world'
        # Actual stringcase result (with TWO underscores):
        #   stringcase.snakecase('Hello World') # => 'hello__world'
        # To address this, we would ideally refactor stringcase itself,
        # but for now, I'm making a kludge here so we can properly convert
        # from 'Title Case' to 'snake_case'.
        snakecase_key = stringcase.snakecase(key.title().replace(' ', ''))
        snakecased_d[snakecase_key] = value
    return snakecased_d

print('Preparing database...')

conn = psycopg2.connect(dbname=ADMIN_DBNAME)
conn.autocommit = True
cur = conn.cursor()

cur.execute('DROP DATABASE IF EXISTS {0};'.format(VARIANT_DBNAME))
cur.execute('CREATE DATABASE {0};'.format(VARIANT_DBNAME))

cur.close()
conn.close()

conn = psycopg2.connect(dbname=VARIANT_DBNAME)
conn.autocommit = False
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE genes (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL
    );
    """
)
cur.execute(
    """
    CREATE UNIQUE INDEX name_idx ON genes (name);
    """
)

cur.execute(
    """
    CREATE TABLE inferred_classifications (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL
    );
    """
)
cur.execute(
    """
    CREATE TABLE reported_classifications (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL,
        inferred_classification_id integer REFERENCES inferred_classifications
    );
    """
)
cur.execute(
    """
    CREATE TABLE sources (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL
    );
    """
)
cur.execute(
    """
    CREATE TABLE variants (
        id serial PRIMARY KEY,
        gene_id integer REFERENCES genes,
        nucleotide_change text,
        protein_change text,
        other_mappings text,
        alias text,
        transcripts text,
        region text,
        reported_classification_id integer
            REFERENCES reported_classifications,
        inferred_classification_id integer
            REFERENCES inferred_classifications NOT NULL,
        source_id integer REFERENCES sources NOT NULL,
        last_evaluated date,
        last_updated date NOT NULL,
        url text NOT NULL,
        submitter_comment text,
        assembly text,
        chr text,
        genomic_start text,
        genomic_stop text,
        ref text,
        alt text,
        accession text,
        reported_ref text,
        reported_alt text
    );
    """
)


genes = set()
inferred_classifications = set()
reported_classifications = set()
sources = set()
with requests.Session() as s:
    download = s.get(VARIANTS_DATASET_URL)
    z = zipfile.ZipFile(io.BytesIO(download.content))
    with z.open('variant_results.tsv', ) as f:
        reader = csv.DictReader(
            io.TextIOWrapper(f, encoding='CP437'),
            delimiter='\t')
        for row in reader:
            snakecased_row = snakecase_keys(row)

            gene = snakecased_row['gene'].upper()
            if gene != '' and gene not in genes:
                genes.add(snakecased_row['gene'])
                cur.execute(
                    """
                    INSERT INTO genes (name)
                         VALUES (%s);
                    """,
                    (gene,)
                )

            inferred_classification = snakecased_row['inferred_classification']
            if (inferred_classification != '' and
                    inferred_classification not in inferred_classifications):
                inferred_classifications.add(
                    snakecased_row['inferred_classification'])
                cur.execute(
                    """
                    INSERT INTO inferred_classifications (name)
                         VALUES (%s);
                    """,
                    (inferred_classification,)
                )

            reported_classification = snakecased_row['reported_classification']
            if (reported_classification != '' and
                    reported_classification not in reported_classifications):
                reported_classifications.add(
                    snakecased_row['reported_classification'])
                cur.execute(
                    """
                    INSERT INTO reported_classifications (
                            name, inferred_classification_id)
                        VALUES (
                            %s,
                            (SELECT id
                             FROM inferred_classifications
                             WHERE name = %s));
                    """,
                    (reported_classification, inferred_classification)
                )

            source = snakecased_row['source']
            if source != '' and source not in sources:
                sources.add(snakecased_row['source'])
                cur.execute(
                    """
                    INSERT INTO sources (name)
                         VALUES (%s);
                    """,
                    (source,)
                )

            # TODO do we need to handle timezones?
            l_e_raw = snakecased_row['last_evaluated']
            last_evaluated = l_e_raw if l_e_raw != '' else None
            l_u_raw = snakecased_row['last_updated']
            last_updated = l_u_raw if l_u_raw != '' else None

            cur.execute(
                """
                INSERT INTO variants (
                    gene_id,
                    nucleotide_change,
                    protein_change,
                    other_mappings,
                    alias,
                    transcripts,
                    region,
                    reported_classification_id,
                    inferred_classification_id,
                    source_id,
                    last_evaluated,
                    last_updated,
                    url,
                    submitter_comment,
                    assembly,
                    chr,
                    genomic_start,
                    genomic_stop,
                    ref,
                    alt,
                    accession,
                    reported_ref,
                    reported_alt)
                VALUES (
                        (SELECT id FROM genes
                            WHERE name = %s),
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        (SELECT id FROM reported_classifications
                            WHERE name = %s),
                        (SELECT id FROM inferred_classifications
                            WHERE name = %s),
                        (SELECT id FROM sources
                            WHERE name = %s),
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s);
                """,
                (
                    snakecased_row['gene'].upper(),
                    snakecased_row['nucleotide_change'],
                    snakecased_row['protein_change'],
                    snakecased_row['other_mappings'],
                    snakecased_row['alias'],
                    snakecased_row['transcripts'],
                    snakecased_row['region'],
                    snakecased_row['reported_classification'],
                    snakecased_row['inferred_classification'],
                    snakecased_row['source'],
                    last_evaluated,
                    last_updated,
                    snakecased_row['url'],
                    snakecased_row['submitter_comment'],
                    snakecased_row['assembly'],
                    snakecased_row['chr'],
                    snakecased_row['genomic_start'],
                    snakecased_row['genomic_stop'],
                    snakecased_row['ref'],
                    snakecased_row['alt'],
                    snakecased_row['accession'],
                    snakecased_row['reported_ref'],
                    snakecased_row['reported_alt']
                    )
            )

conn.commit()
cur.close()
conn.close()

print('Database preparation complete')
