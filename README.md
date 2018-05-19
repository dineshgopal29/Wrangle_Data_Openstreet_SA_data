# Wrangle OpenStreetMap Data - Project 4 Udacity

## DataSet
I have used San Antonio City map for the project. I have used a small subset of the map for analysis.

https://www.openstreetmap.org/export#map=10/29.4587/-98.5178

## Datasize
Below are the files extracted from the script and their corresponding sizes.

File Name | Size(MB)
------------ | -------------
sa_map|112.9
ways_nodes|1.6
ways|3.8
nodes|39.6
nodes_tags|1.6
ways_nodes|13.7
ways_tags|10.4

## Data Wrangling
I have repurposed the code from Udacity assigments for the analysis. I have used a map for streamlining the adress notations.

```
# Address Mapping
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue",
            "street":"Street"
            }

```

Also have to set the encoding to UTF-8 as I was getting errors while extracting the information from tags.

```
import sys
reload(sys)
sys.setdefaultencoding('utf8')
```

## DataSet Metrics
SQLite 3 is used for querying and analysisng the extracted data. I have created a DB called **SanAntonioData.db** to store the data. Also used SQLiteStudio GUI to execute queries.

### Total number of Users contributed for the dataset 
Total number of unique users **500**

Contributors | 500
------------ | -------------

#### Sql Query:
```
SELECT count(DISTINCT(uid)) AS "Unique Contributors"
FROM (SELECT uid FROM nodes 
      UNION 
      SELECT uid FROM ways) AS u;
```

### Top 10 Amenities
Top ten amenities for the dataset.

Amenities | Available Locations
------------ | -------------
place_of_worship|1708
school	|482
fast_food	|234
restaurant	|232
parking_entrance|	166
bench	|142
toilets	|100
pharmacy	|94
kindergarten	|70
fuel|	66

#### SQL Query:
```
-- Query
SELECT value AS "Amenities", COUNT(value) AS "Available Locations"
FROM	(SELECT *
	FROM nodes_tags
	UNION ALL
	SELECT *
	FROM nodes_tags) as a
WHERE key = 'amenity'
GROUP BY value
ORDER BY "Available Locations" DESC
LIMIT 10
```
### Top 10 Favourite Eats
Burger looks like the favourite cusines for the dataset under consideration

Eats | Favourites
------------ | -------------
burger	|96
mexican	|52
chicken	|34
sandwich|	28
american|	22
pizza	|19
regional|	14
coffee_shop|	13
chinese	|12
barbecue|	9

#### SQL Query:
```
SELECT value AS "Eats", COUNT(*) AS "Favourites"
FROM	(SELECT *
	FROM nodes_tags
	UNION ALL
	SELECT *
	FROM nodes_tags) as t
WHERE key = 'cuisine'
GROUP BY value
ORDER BY "Favourites" DESC
LIMIT 10
```
### Top 10 Favourite Sports
Favourite sports for the given dataset is Baseball with **263** mentions on the same.

Sport | Favourites
------------ | -------------
baseball	|263
tennis	|213
soccer	|100
basketball	|88
american_football	|43
softball	|31
swimming	|21
multi	|10
volleyball	|8
beachvolleyball	|5

#### SQL Query:
```
SELECT value AS "Sport", COUNT(*) AS "Favourites"
FROM	(SELECT *
	FROM nodes_tags
	UNION ALL
	SELECT *
	FROM nodes_tags) as t
WHERE key = 'sport'
GROUP BY value
ORDER BY "Favourites" DESC
LIMIT 10
```

### Top 10 Office Buildings
Favourite office buildings for the given dataset

Offices | Types
------------ | -------------
company	|10
insurance	|7
lawyer	|6
estate_agent|	4
government	|2
it	|2
accountant	|1
newspaper	|1
pest_control|	1
research	|1

#### SQL Query:
```
SELECT value AS "Offices", COUNT(*) AS "Types"
FROM	(SELECT *
	FROM nodes_tags
	UNION ALL
	SELECT *
	FROM nodes_tags) as t
WHERE key = 'office'
GROUP BY value
ORDER BY "Types" DESC
LIMIT 10
```

### Sample Buildings
Sample Building | Types 
------------ | -------------
H-E-B Pharmacy|	33
Kingdom Hall of Jehovahs Witnesses|	20
Subway	|13
Starbucks	|12
Valero	|11
James Avery Jewelry|	8
Pizza Hut	|8
Schlotzsky's Deli	|6
Batteries Plus Bulbs|	5
Church's Chicken	|5

### Top 10 Shopping Locations
Favourite sports for the given dataset is Baseball with **263** mentions on the same.

Shopping | Locations 
------------ | -------------
convenience	|77
supermarket	|71
car	|29
car_repair	|26
department_store|	22
storage_rental	|19
doityourself	|16
art	|15
electronics	|12
furniture	|12

#### SQL Query:
```
SELECT value AS "Shopping", COUNT(*) AS "Locations"
FROM	(SELECT *
	FROM nodes_tags
	UNION ALL
	SELECT *
	FROM nodes_tags) as t
WHERE key = 'shop'
GROUP BY value
ORDER BY "Locations" DESC
LIMIT 10
```

## Additional Improvements
The openstreet map dataset can be a little more cleaner. The tage names for the nodes are same for group nodes and indidvidual nodes.

## References
* SQLite Tutorial http://www.sqlitetutorial.net/sqlite-sample-database/
* Map Features https://wiki.openstreetmap.org/wiki/Map_Features#Tourism
* Tags https://wiki.openstreetmap.org/wiki/Tags
* Mastering Markdown https://guides.github.com/features/mastering-markdown/
* Pragmatic Unicode https://nedbatchelder.com/text/unipain.html
* https://markhneedham.com/blog/2015/05/21/python-unicodeencodeerror-ascii-codec-cant-encode-character-uxfc-in-position-11-ordinal-not-in-range128/
