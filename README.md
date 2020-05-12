## Discuss the purpose of this database in context of the startup, Sparkify, and their analytical goals.

In function, this database is similar with what we already made in earlier chapter, which can be used for search data by SQL queries, and input the result to BI softwares to help decision making. But, this database is implement on AWS Redshift, and data store in AWS S3. Comparing with earlier courses and assignments, it offers more scalability and less hardware requirement, but on the contrary, it may have some extra cost.

## State and justify your database schema design and ETL pipeline.

### Fact table:

**songplays** - records in event data associated with song plays i.e. records with page NextSong

>songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### Dimension table:

**users** - users in the app

>user_id, first_name, last_name, gender, level

**songs** - songs in music database
>song_id, title, artist_id, year, duration

**artists** - artists in music database
>artist_id, name, location, lattitude, longitude

**time** - timestamps of records in songplays broken down into specific units
>start_time, hour, day, week, month, year, weekday

## Setup

Fill the **dwh.cfg** file with your own info.

>[CLUSTER]
HOST=your host, which can be known at Redshift endpoint
DB_NAME=database name
DB_USER=database user name
DB_PASSWORD=DB_USER's passcode
DB_PORT=5439

>[IAM_ROLE]
ARN=IAM role arn

>[S3]
LOG_DATA='s3://udacity-dend/log_data'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data'