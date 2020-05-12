import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')
LOG_DATA = config.get('S3','LOG_DATA')
SONG_DATA = config.get('S3','SONG_DATA')
LOG_JSONPATH = config.get('S3','LOG_JSONPATH')
ARN = config['IAM_ROLE']['ARN']
# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS  staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_songs_table_create= ("""CREATE TABLE IF NOT EXISTS staging_songs(
                                 num_songs INTEGER,
                                 artist_id VARCHAR,
                                 artist_lattitude FLOAT,
                                 artist_longitude FLOAT,
                                 artist_location VARCHAR,
                                 artist_name VARCHAR,
                                 song_id VARCHAR,
                                 title VARCHAR,
                                 duration FLOAT,
                                 year INTEGER)
""")

staging_events_table_create = ("""CREATE TABLE IF NOT EXISTS staging_events(
                                  artist VARCHAR,
                                  auth VARCHAR,
                                  firstName VARCHAR,
                                  gender VARCHAR,
                                  itemInSession INTEGER,
                                  lastName VARCHAR,
                                  length REAL,
                                  level VARCHAR,
                                  location VARCHAR,
                                  method VARCHAR,
                                  page VARCHAR,
                                  registration DECIMAL,
                                  sessionId INTEGER,
                                  song VARCHAR,
                                  status INTEGER,
                                  ts TIMESTAMP,
                                  userAgent VARCHAR,
                                  userId INTEGER);
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays(
                            songplay_id INTEGER IDENTITY(0,1) PRIMARY KEY DISTKEY,
                            start_time TIMESTAMP,
                            user_id INTEGER,
                            level VARCHAR,
                            song_id VARCHAR,
                            artist_id VARCHAR,
                            session_id INTEGER,
                            location VARCHAR,
                            user_agent TEXT);
                            
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER IDENTITY(0,1) PRIMARY KEY DISTKEY,
                        first_name VARCHAR,
                        last_name VARCHAR,
                        gender VARCHAR,
                        level VARCHAR);
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs(
                        song_id VARCHAR PRIMARY KEY,
                        title VARCHAR,
                        artist_id VARCHAR,
                        year INTEGER,
                        duration FLOAT);
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists(
                          artist_id VARCHAR PRIMARY KEY,
                          name VARCHAR,
                          location VARCHAR,
                          lattitude REAL,
                          longitude REAL);
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time(
                        start_time TIMESTAMP PRIMARY KEY,
                        hour INTEGER,
                        day INTEGER,
                        week INTEGER,
                        month INTEGER,
                        year INTEGER,
                        weekday VARCHAR)
""")

# STAGING TABLES

staging_events_copy = ("""COPY staging_events FROM {}
                          CREDENTIALS 'aws_iam_role={}'
                          REGION 'us-west-2'
                          FORMAT AS JSON {}
                          TIMEFORMAT AS 'epochmillisecs'
                          
""").format(LOG_DATA, ARN, LOG_JSONPATH)

staging_songs_copy = ("""COPY staging_songs FROM {}
                         CREDENTIALS 'aws_iam_role={}'
                         REGION 'us-west-2'
                         FORMAT AS JSON 'auto'
""").format(SONG_DATA, ARN)

# FINAL TABLES

songplay_table_insert = ("""INSERT INTO songplays(start_time, 
                                                  user_id, 
                                                  level, 
                                                  song_id, 
                                                  artist_id, 
                                                  session_id, 
                                                  location,                               
                                                  user_agent)
                            SELECT DISTINCT se.ts,'1970-01-01'::date + ts/1000 * interval '1 second' AS start_time,
                                            se.userId,
                                            se.level,
                                            ss.song_id,
                                            ss.artist_id,
                                            se.sessionId,
                                            se.location,
                                            se.userAgent
                            FROM staging_events AS se JOIN staging_songs AS ss 
                                                      ON ss.artist_name = se.artist AND ss.title = se.song
                            WHERE page = 'NextSong'
                            
""")

user_table_insert = ("""INSERT INTO users(user_id, 
                                          first_name, 
                                          last_name, 
                                          gender, 
                                          level)
                        SELECT DISTINCT userId,
                                        firstName,
                                        lastName,
                                        gender,
                                        level
                        FROM staging_events
""")

song_table_insert = ("""INSERT INTO songs(song_id, 
                                          title, 
                                          artist_id, 
                                          year, 
                                          duration)
                        SELECT DISTINCT song_id,
                                        title,
                                        artist_id,
                                        year,
                                        duration
                        FROM staging_songs
""")

artist_table_insert = ("""INSERT INTO artists(artist_id, 
                                              name, 
                                              location, 
                                              lattitude, 
                                              longitude)
                          SELECT DISTINCT ss.artist_id,
                                          ss.artist_name,
                                          se.location,
                                          ss.latttitude,
                                          ss.longitude
                          FROM staging_events AS se JOIN staging_songs AS ss
                                                    ON ss.artist_name = se.artist AND ss.title = se.song
""")

time_table_insert = ("""INSERT INTO time(start_time, 
                                         hour, 
                                         day, 
                                         week, 
                                         month, 
                                         year, 
                                         weekday)
                        SELECT DISTINCT start_time,
                               EXTRACT(HOUR FROM start_time),
                               EXTRACT(DAY FROM start_time),
                               EXTRACT(WEEK FROM start_time),
                               EXTRACT(MONTH FROM start_time),
                               EXTRACT(YEAR FROM start_time),
                               EXTRACT(DOW FROM start_time)
                        FROM(
                             SELECT DISTINCT ts,'1970-01-01'::date + ts/1000 * interval '1 second' AS start_time
                             FROM staging_event)temp
                               
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]

#Change something.