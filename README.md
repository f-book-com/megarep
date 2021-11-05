# MegaRep -- a poetical mega-repertory

## Aim

This Python library provides functionality to query poetical databases that are connected by a catalogue of query templates.

## Catalogue format

The catalogue is in a MariaDB/MySQL database. The catalogue contains three tables.
- repertoire: the list of repertories that take part in the collaboration, including login data that is necessary for obtaining a read-only access of their databases
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

The MegaRep library currently requires the pymysql and re libraries. After importing the library, it is necessary to establish a connection to the catalogue database. To obtain the password to the catalogue please write me an e-mail.

    import megarep
    mega = megarep.loadMegaRep(dbhost="gepeskonyv.org", dbuser="gepeskonyv_rpha_client",
                          dbpassword="***", dbname="gepeskonyv_MEGAREP")

At this point, the variable "mega" is a list of all the collaborating databases. A for cycle can be used to search for something in all of the repertories.

    query1 = []
    for rep in mega:
        query1 = query1 + rep.search('incipit', ['Ave'])

At the end of this code, the variable "query1" contains all of the poems that have the string "ave" in their incipit. The example shows that the default search method is case-insensitive and disregards spaces and punctuation. Every element of the result list is itself a list of two elements: the ID of the repertory and the ID of the variant/poem. This is why the list of results from database nr. 2 can be simply added to the results from database nr. 1 in the for loop: the results will still be differentiated.

At it's current state, the mega-repertory connects two databases (Répertoire de la poésie hongroise ancienne and Le Nouveau Naetebus), and "query1" would look like this:

    [[1, 24373], [1, 24595], [1, 24604], [1, 24693], [1, 24694], [1, 24695], [1, 26926], [1, 27093], [1, 27356], [1, 27367], [1, 27693], [1, 28125], [1, 28340], [2, 3], [2, 8], [2, 14], [2, 18], [2, 22], [2, 23], [2, 95], [2, 161], [2, 162], [2, 163], [2, 164], [2, 165], [2, 215], [2, 259], [2, 260], [2, 261], [2, 347], [2, 353], [2, 354], [2, 372], [2, 386], [2, 402], [2, 403], [2, 408], [2, 412], [2, 413], [2, 444], [2, 447], [2, 449], [2, 458], [2, 459], [2, 460]]

For listing the results in a more informative way, the "value" function can be used.

    
