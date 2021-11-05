# MegaRep -- a poetical mega-repertory

## Aim

This Python library provides functionality to query poetical databases that are connected by a catalogue of query templates.

## Catalogue format

The catalogue is in a MariaDB/MySQL database. The catalogue contains three tables.
- repertoire: the list of repertories that take part in the collaboration
- dbtype: the list of database types handled by the mega-repertory engine
- connector: the actual catalogue of query templates

Each row of the connector table must provide four pieces of information.
1. id_repertoire: for which repertory the query templates in that row have been designed
2. parameter: which parameter (eg. author, title, incipit etc.) the query templates search/show
3. code_search: query template for searching for the given parameter
4. code_show: query template for showing the data belonging to the given parameter in case of a given list of poems

The code_search queries look for identifiers of poem variants that fit the parameter and the given value. For databases that are based on poems rather than every variant of poems, these queries return identifiers of poems. For databases that describe poem variants as basic entities (eg. Répertoire de la poésie hongroise ancienne), there are special queries that connect variants to poem and vice versa (see later). The code_search queries take one value for one parameter, and they can use various search methods (in the case of MySQL, for example, LIKE, =, REGEXP etc), and they return a list of poem/variant IDs.

The code_show queries take a list of poem/variant IDs (poem or variant depending on the database), and return a list of strings as a result.

This way, the catalogue can connect many databases by defining search and show queries that use the same input and output format. In many cases, it will be hard or even impossible to define such queries, because different poetical traditions deal with somewhat different concepts. The possibility of creating catalogue entries for certain parameters will map the common characteristics as well as the conceptual differences of the collaborating databases.

There is one catalogue currently hosted on gepeskonyv.org.

## Library

The Python library (megarep.py) is designed to use this catalogue for accessing poetical databases, and also to provide some useful features in dealing with query results.

### Basic use of the library

    import megarep
    mega = megarep.loadMegaRep(dbhost="gepeskonyv.org", dbuser="gepeskonyv_rpha_client",
                          dbpassword="***", dbname="gepeskonyv_MEGAREP")
