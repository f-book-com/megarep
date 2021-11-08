# MegaRep - a poetical mega-repertory

## Aim

This Python library provides functionality to query poetical databases that are connected by a catalogue of query templates.
The development was preceded by a pilot project about ten years before by Péter Király, and both projects were supervised by Levente Seláf, Eötvös Loránd University, Budapest, Hungary. Links to the pilot project can be found at the bottom of this document.

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

### Basic search with the library

The MegaRep library currently requires the pymysql and re libraries. After importing the library, it is necessary to establish a connection to the catalogue database. This is done by initializing an instance of the MegaRep class. (To obtain the password to the catalogue please write me an e-mail.)

    import megarep
    mega = megarep.MegaRep(dbhost="gepeskonyv.org", dbuser="gepeskonyv_rpha_client",
                          dbpassword="***", dbname="gepeskonyv_MEGAREP")

At this point, the variable "mega" represents the whole mega-repertory. You can search it as if it was one single database, but you can also use any of its member databases separate from the others.

    query1 = mega.search('incipit', ['Ave'])
    print(query1)

At the end of this code, the variable "query1" contains all of the poems that have the string "ave" in their incipit in any of the databases. The example shows that the default search method is case-insensitive and disregards spaces and punctuation. Every element of the result list is itself a list of two elements: the ID of the repertory and the ID of the variant/poem. This is why the list of results from database nr. 2 can be simply added to the results from database nr. 1 in the for loop: the results will still be differentiated.

At it's current state, the mega-repertory connects two databases (Répertoire de la poésie hongroise ancienne and Le Nouveau Naetebus), and "query1" would look like this:

    ['1|24373', '1|24595', '1|24604', '1|24693', '1|24694', '1|24695', '1|26926', '1|27093', '1|27356', '1|27367', '1|27693', '1|28125', '1|28340', '2|3', '2|8', '2|14', '2|18', '2|22', '2|23', '2|95', '2|161', '2|162', '2|163', '2|164', '2|165', '2|215', '2|259', '2|260', '2|261', '2|347', '2|353', '2|354', '2|372', '2|386', '2|402', '2|403', '2|408', '2|412', '2|413', '2|444', '2|447', '2|449', '2|458', '2|459', '2|460']

For listing parameter values that belong to the poems represented by these numbers, the "show" function can be used.

    result1 = mega.show(['incipit'], query1)
    print(result1)

Here the output will be longer, but let's see the beginning and the end.

    [['1|24373', 'Ave salutis hostia'], ['1|24595', 'Patris sapientia, veritas divina'], ['1|24604', 'O crux ave spes unica'], ..., ['2|459', 'Ave virge Marie'], ['2|460', 'Ave seynte Marie, mere al creatur']]

Notice that "sapientia, veritas" contains "a...ve" and is shown as a query result. Of course, a more precise result set might be obtained if the search query uses regular expressions:

    query1 = mega.search('incipit', ['(^|.+ )([Aa]ve)( .*|$)'], 'REGEXP')

The tolerant search currently gives 45 hits, while the precise search only 31 hits. If needed, the library will be extended to other database servers as well (such as Oracle), but it has to be noted that there might be issues if two servers have a different interpretation of regular expression syntax.

#### Variants and poems

As noted before, some databases might use poems as their most basic structure, while in the case of other literary traditions, a more detailed approach might prove to be useful. You can consider poems or variants to be the basic unit of a database. If the database does not deal with variants, the MegaRep system considers "variant" as a synonym for "poem". On the other hand, for those databases where variants are the basic unit, some special parameters had to be added.

1. mainlist: The MegaRep system considers data belonging to the poem as a whole to belong to the "main variant" of the poem. In the case of such databases, this "main variant" is an idealized, abstract entity, which does not have any original source. The parameter "mainlist" is a technical one, and it only has a "code_search" entry: it is used by the MegaRep library, which, when loading each database, uses this query to retreive all the variant IDs that belong to whole poems (or "main variants").
2. poem: This parameter links variant IDs to poem IDs. If the database does not deal with variants, the output of this query will be the same as its input. In variant-based databases, "code_search" will return all the variants that belong to a specific poem, while "code_show" will return the poem IDs that belong to a given list of poem variant IDs.
3. variant: This parameter links the physically existing variants to any variant. If the database is based on poems, the output will mirror the input. In variant-based databases, "code_search" will return all the real variants of the poem to which the input variant belongs. In other words, this query will return all the variants except for the "main variant". "code_show" is useless, it mirrors the input.
4. mainvariant: This parameter is the opposite of the "variant" parameter. It returns only the main variant belonging to the poem to which the input variant belongs."code_show" is again useless.

These catalogue entries make it possible to use some special search methods. The function "searchm" returns only "main variants" as results. The function "msearch" returns the "main variants" that belong to the input variants. These functions allow the researcher to use variant-based databases as if they were poem-based, so it is possible to compare results despite this fundamental difference between certain databases.

### Manipulating results

The functions described above make it possible to do simple searches and to retrieve values of specific parameters. However, the library provides some useful functionality in combining and manipulating queries.

#### Logical operations

The functions repAnd, repOr and repAndNot all take two parameters (two query results) and use set operations (intersection, union and difference) to implement these operations.

    query1 = mega.searchm('author', ['Balassi'])
    query2 = mega.searchm('incipit', ['Julia', 'Caelia'])
    query3 = repAnd(query1, query2)
    query4 = repAndNot(query2, query1)
    query5 = repOr(query1, query2)
    print(len(query1))
    print(len(query2))
    print(len(query3))
    print(len(query4))
    print(len(query5))

This example will print out the numbers 118, 12, 11, 1, 119, which show that there is indeed only one old Hungarian poem with "Julia" or "Caelia" in the incipit, which was not written by Bálint Balassi.

#### Evaluating operations

##### repVal(data, index=1)

This function gives a list of all the values (without repetition) in an output from a show function. It will process the column of the repShow results according to the value of index (default 1).

##### repStat(data, index=1)

This function takes the same arguments as repVal, but evaluates data a little more. The output of this function is a dictionary, where possible values are the key, and the dictionary value is a list containing the count of results belonging to that value and the percentage of that value among the results. Percentage values are rounded and therefore never completely precise, so they are presented as string variables for easier reading. The count value, which is precise, should be used if further calculations are necessary.

##### repDisp(result)

This function prints the results of a show, repVal or repStat function in a readable way on the Python console. It might be used with the output of any of the MegaRep functions.

##### repExport(result, path)

This function creates a usable CSV export from the results of any of the MegaRep functions. Warning: this function overwrites the file under "path" if it exists.

##### Example

    query1 = mega.searchm('genre', ['história'])
    result1 = mega.show(['author'], query1)
    repDisp(repVal(query1))

This code will produce a list of the authors.

    Alistáli Márton
    Balassi Bálint
    Baranyai Pál
    ...
    Zombori Antal
    Ádám János
    
Note the inability of the library to sort accented characters properly. It is of course possible to implement a correct sorting method, but this is not a priority at this development stage. Adding the following code will also produce the statistical results.

    repDisp(repStat(result1))

The output is the following.

    	[22, '11.9%']
    Alistáli Márton	[1, '0.5%']
    Balassi Bálint	[1, '0.5%']
    Baranyai Pál	[1, '0.5%']
    Batizi András	[5, '2.7%']
    Beythe András	[1, '0.5%']
    Biai Gáspár	[1, '0.5%']
    Bogáti Fazakas Miklós	[14, '7.6%']
    ...
    Zombori Antal	[1, '0.5%']
    Ádám János	[1, '0.5%']

These outputs are obviously better handled by a spreadsheet application, or they should be processed further.

    repExport(repStat(result1), 'export.csv')

## Serious limitations

It is at this stage of the development, that further parameters will be implemented, first for the Répertoire de la poésie hongroise ancienne database. So far, the following parameters have been implemented for this database:

author
date
dedication
genre
incipit
melrefd (The poem's melody is referenced by another poem.)
refsmel (The poem references another poem's melody.)
text (This is available for approximately 10% of the database.)
title

The code lacks proper error handling and should be consistently commented for easier readability. Feel free to write any comments or suggestions.

## Links to the former pilot project

https://github.com/pkiraly/megarep
https://kirunews.blog.hu/2014/10/26/federated_search_engine_of_european_poetical_databases
