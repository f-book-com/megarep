# PDC - Poetry Database Connector

## Project description

This Python library provides functionality to query poetical databases
that are connected by a catalog of query templates. The development is
supervised by Levente Seláf, Eötvös Loránd University, Budapest,
Hungary, who also led the development of a pilot about ten years before
by Péter Király. The project complements somewhat the Averell software
developed within the EU-funded POSTDATA research. Links to these
projects can be found at the bottom of this document.

### Current connections between poetical databases.

The pilot project of Péter Király connected databases by requiring them
to provide a standardized query system, which the connecting program
used to find poems from all databases. The result was a list of poems,
with hyperlinks to their corresponding web pages.

One of the POSTDATA project’s goals is to find a common ground, a
“domain model” of European poetry, in order to facilitate a Linked Open
Data model of European poetry repositories. This “domain model” defines
a very detailed standard of annotating documents for enabling
comparative research. The Averell software connects the collaborating
repositories by allowing the user to download them and providing a tool
for converting them into a uniform JSON format for further processing.

### Claims

This PDC system claims to offer the following new features,
especially to complement the Averell software’s functionality.

1.  The system requires the absolute minimum work from the maintainers
    of collaborating databases.

    -   This system uses every database’s own query system, so that
        database maintainers do not have to provide a special search
        engine (such as Apache Lucene) on their own.
    -   Queries are assembled using query templates. These templates
        must follow certain rules, but they are essentially identical to
        normal queries of the same database. Database maintainers only
        have to provide queries they are familiar with.

2.  PDC itself allows for very complex queries while being easy to
    use and combine with other tools. These queries can be far more
    complex than anything that would be possible on traditional web
    interfaces of poetry databases.
3.  PDC provides tools for finding poems and accessing their
    metadata (and if available, their text) without having to download
    any unnecessary data.

    -   While the repositories provided through the Averell software
        contain vast amounts of annotated texts, the POSTDATA system
        offers very little help so far in finding specific poems. With
        the Averell software, the user downloads complete corpora for
        further processing. If the user wishes to select or sort
        specific poems, they have to code or use different programs to
        do so.
    -   The PDC system should in the future be connected to Averell.
        The selected poems’ annotated text should be compiled by Averell
        into a processable common JSON file for further analysis. Or, if
        the computerized close reading of Averell JSON corpora returns a
        list of poems that are interesting, this list should be possible
        to combine with PDC search results.

## Catalog format

The catalog is in a MariaDB/MySQL database. The catalog contains three
tables. - repertoire: the list of repertories that take part in the
collaboration, including login data that is necessary for obtaining a
read-only access of their databases - dbtype: the list of database types
handled by the PDC engine - connector: the actual catalog of
query templates

Each row of the connector table must provide four pieces of information.
1. id\_repertoire: for which repertory the query templates in that row
have been designed 2. parameter: which parameter (eg. author, title,
incipit etc.) the query templates search/show 3. code\_search: query
template for searching for the given parameter 4. code\_show: query
template for showing the data belonging to the given parameter in case
of a given list of poems

The code\_search queries look for identifiers of poem variants that fit
the parameter and the given value. For databases that are based on poems
rather than every variant of poems, these queries return identifiers of
poems. For databases that describe poem variants as basic entities (eg.
Répertoire de la poésie hongroise ancienne), there are special queries
that connect variants to poems and vice versa (see later). The
code\_search queries take one value for one parameter, and they can use
various search methods (in the case of MySQL, for example, LIKE, =,
REGEXP, etc), and they return a list of poem/variant IDs.

The code\_show queries take a list of poem/variant IDs (poem or variant
depending on the database) and return a list of strings as a result.

This way, the catalog can connect many databases by defining *search*
and *show* queries that use the same input and output format. In many
cases, it will be hard or even impossible to define such queries,
because different poetical traditions deal with somewhat different
concepts. The possibility of creating catalog entries for certain
parameters will map the common characteristics as well as the conceptual
differences of the collaborating databases.

There is one catalog currently hosted on gepeskonyv.org.

## Library

The Python library (pdc.py) is designed to use this catalog for
accessing poetical databases, and also to provide some useful features
in dealing with query results.

### Basic search with the library

The PDC library currently requires the pymysql and re libraries.
After importing the library, it is necessary to establish a connection
to the catalog database. This is done by initializing an instance of the
PDC class. (To obtain the password to the catalog please write me an
e-mail.)

    import pdc
    rep = pdc.PDC(dbhost="gepeskonyv.org", dbuser="gepeskonyv\_rpha\_client", dbpassword="***", dbname="gepeskonyv\_MEGAREP")

At this point, the variable “rep” represents the whole mega-repertory.
You can search it as if it was one single database, but you can also use
any of its member databases separate from the others.

    query1 = rep.search('incipit', ['Ave'])
    print(query1)

At the end of this code, the variable “query1” contains all of the poems
that have the string “ave” in their incipit in any of the databases. The
example shows that the default search method is case-insensitive and
disregards spaces and punctuation. Every element of the result list is
itself a list of two elements: the ID of the repertory and the ID of the
variant/poem. This is why the list of results from database nr. 2 can be
simply added to the results from database nr. 1 in the for loop: the
results will still be differentiated.

At it’s current state, the PDC connects two databases
(Répertoire de la poésie hongroise ancienne and Le Nouveau Naetebus),
and “query1” would look like this:

    ['NN-v3', 'NN-v8', 'NN-v14', 'NN-v18', 'NN-v22', 'NN-v23', 'NN-v95', 'NN-v161', 'NN-v162', 'NN-v163', 'NN-v164', 'NN-v165', 'NN-v215', 'NN-v259', 'NN-v260', 'NN-v261', 'NN-v347', 'NN-v353', 'NN-v354', 'NN-v372', 'NN-v386', 'NN-v402', 'NN-v403', 'NN-v408', 'NN-v412', 'NN-v413', 'NN-v444', 'NN-v447', 'NN-v449', 'NN-v458', 'NN-v459', 'NN-v460', 'RPHA-v24373', 'RPHA-v24595', 'RPHA-v24604', 'RPHA-v24693', 'RPHA-v24694', 'RPHA-v24695', 'RPHA-v26926', 'RPHA-v27093', 'RPHA-v27356', 'RPHA-v27367', 'RPHA-v27693', 'RPHA-v28125', 'RPHA-v28340']

For listing parameter values that belong to the poems represented by
these numbers, the “show” function can be used.

    result1 = rep.show(\['incipit'\], query1)
    print(result1)

Here the output will be longer, but let’s see the beginning and the end.

    [['NN-v3', ['Ave en cui sans nul nombre a']], ['NN-v8', ['Glorieuse vierge Royne En cui par la vertu divine']], ['NN-v14', ['Ave dame des angres de paradis royne']], ['RPHA-v27367', ['Sírva veszékel most szegény Magyarország']], ['RPHA-v27693', ['Dávid mikor a veszedelmet látá']], ['RPHA-v28125', ['Nemes földjét a szent népnek pogány rablá, veszté']], ['RPHA-v28340', ['Vitézek, mi lehet e széles föld felett szebb dolog a végeknél']]]

Notice that “par la vertu divine” contains “a…ve” and is shown as a query
result. Of course, a more precise result set might be obtained if the
search query uses regular expressions:

    query1 = rep.search('incipit', ['(^|.+ )([Aa]ve)( .*|$)'], 'REGEXP')

The tolerant search currently gives 45 hits, while the precise search
only 31 hits. If needed, the library will be extended to other database
servers as well (such as Oracle), but it has to be noted that there
might be issues if two servers have a different interpretation of
regular expression syntax.

#### Variants and poems

As noted before, some databases might use poems as their most basic
structure, while in the case of other literary traditions, a more
detailed approach might prove to be useful. You can consider poems or
variants to be the basic unit of a database. If the database does not
deal with variants, the PDC system considers “variant” as a synonym
for “poem”. On the other hand, for those databases where variants are
the basic unit, some special parameters had to be added.

1.  mainlist: The PDC system considers data belonging to the poem as
    a whole to belong to the “main variant” of the poem. In the case of
    such databases, this “main variant” is an idealized, abstract
    entity, which does not have any original source. The parameter
    “mainlist” is a technical one, and it only has a “code\_search”
    entry: it is used by the PDC library, which, when loading each
    database, uses this query to retrieve all the variant IDs that
    belong to whole poems (or “main variants”).
2.  poem: This parameter links variant IDs to poem IDs. If the database
    does not deal with variants, the output of this query will be the
    same as its input. In variant-based databases, “code\_search” will
    return all the variants that belong to a specific poem, while
    “code\_show” will return the poem IDs that belong to a given list of
    poem variant IDs.
3.  variant: This parameter links the physically existing variants to
    any variant. If the database is based on poems, the output will
    mirror the input. In variant-based databases, “code\_search” will
    return all the real variants of the poem to which the input variant
    belongs. In other words, this query will return all the variants
    except for the “main variant”. “code\_show” is useless, it mirrors
    the input.
4.  mainvariant: This parameter is the opposite of the “variant”
    parameter. It returns only the main variant belonging to the poem to
    which the input variant belongs.“code\_show” is again useless.

These catalog entries make it possible to use some special search
methods. The function “searchm” returns only “main variants” as results.
The function “msearch” returns the “main variants” that belong to the
input variants. These functions allow the researcher to use
variant-based databases as if they were poem-based, so it is possible to
compare results despite this fundamental difference between certain
databases.

### Manipulating results

The functions described above make it possible to do simple searches and
to retrieve values of specific parameters. However, the library provides
some useful functionality in combining and manipulating queries.

#### Logical operations

The functions repAnd, repOr and repAndNot all take two parameters (two
query results) and use set operations (intersection, union and
difference) to implement these operations.

    query1 = rep.searchm('author', ['Balassi'])
    query2 = rep.searchm('incipit', ['Julia', 'Caelia'])
    query3 = repAnd(query1, query2)
    query4 = repAndNot(query2, query1)
    query5 = repOr(query1, query2)
    print(len(query1))
    print(len(query2))
    print(len(query3))
    print(len(query4))
    print(len(query5))

This example will print out the numbers 118, 12, 11, 1, 119, which show
that there is indeed only one old Hungarian poem with “Julia” or
“Caelia” in the incipit, which was not written by Bálint Balassi.

#### Evaluating operations

##### repVal(data, index=1)

This function gives a list of all the values (without repetition) in an
output from a show function. It will process the column of the repShow
results according to the value of index (default 1).

##### repStat(data, index=1)

This function takes the same arguments as repVal, but evaluates data a
little more. The output of this function is a dictionary, where possible
values are the key, and the dictionary value is a list containing the
count of results belonging to that value and the percentage of that
value among the results. Percentage values are rounded and therefore
never completely precise, so they are presented as string variables for
easier reading. The count value, which is precise, should be used if
further calculations are necessary.

##### repDisp(result)

This function prints the results of a show, repVal or repStat function
in a readable way on the Python console. It might be used with the
output of any of the PDC functions.

##### repExport(result, path)

This function creates a usable CSV export from the results of any of the
PDC functions. Warning: this function overwrites the file under
“path” if it exists.

##### Example

    query1 = rep.searchm('genre', ['história'])
    result1 = rep.show(['author'], query1)
    repDisp(repVal(query1))

This code will produce a list of the authors.

    Alistáli Márton
    Balassi Bálint
    Baranyai Pál
    ...
    Zombori Antal
    Ádám János

Note the inability of the library to sort accented characters properly.
It is of course possible to implement a correct sorting method, but this
is not a priority at this development stage. Adding the following code
will also produce the statistical results.

    repDisp(repStat(result1))

The output is the following.

    [22, '11.9%']
    Alistáli Márton [1, '0.5%']
    Balassi Bálint  [1, '0.5%']
    Baranyai Pál    [1, '0.5%']
    Batizi András   [5, '2.7%']
    Beythe András   [1, '0.5%']
    Biai Gáspár [1, '0.5%']
    Bogáti Fazakas Miklós   [14, '7.6%']
    ...
    Zombori Antal   [1, '0.5%']
    Ádám János  [1, '0.5%']

The first row of the results represents an empty string, where the author is unknown. These outputs are obviously better handled by a spreadsheet application, or they should be processed further.

    repExport(repStat(result1), 'export.csv')

## Serious limitations

It is at this stage of the development that further parameters will be
implemented, first for the Répertoire de la poésie hongroise ancienne
database. So far, the following parameters have been implemented for
this database:

-   acrostic
-   author
-   colophon
-   date
-   dedication
-   genre
-   incipit
-   length
-   melody
-   melrefd (The poem’s melody is referenced by another poem.)
-   metre
-   refsmel (The poem references another poem’s melody.)
-   rhyme
-   syllables
-   text (This is available for approximately 10% of the database.)
-   title

The code lacks proper error handling and should be consistently
commented for easier readability. Feel free to write any comments or
suggestions.

## Links to the referenced projects

https://github.com/pkiraly/megarep

https://kirunews.blog.hu/2014/10/26/federated\_search\_engine\_of\_european\_poetical\_databases

https://averell.readthedocs.io/en/latest/readme.html

https://github.com/linhd-postdata/averell/tree/de65877ab2ae8f02a8cb7fd21d275417dc52cd42

https://postdata.linhd.uned.es/results/ontologies/domain-model-ep/
