# LastFM API wrapper

![CircleCI](https://circleci.com/gh/dshomoye/lastfm-visualizer.svg?style=svg&circle-token=bfe9a145894b73da27fbe342d038da72fe6c9e79)

API orchestration to get better insight into LastFM listening history/date bank.
available at [https://lastfm-wrapper.appspot.com]
Currently only relies on history to provide:

1: Streaming history.

`/scrobbles/:lastfm username`

- scrobbles within a provided date range.

parameters:

- `start` (required): the start of the date range, supports most standard date formats
- `end` (required): same as `start`

sample reqeust:
`/scrobbles/sonofatailor`

data (application/json):

```json

{
    "start": "2018-5-02 ",
    "end": "2018-5-03 12:0:0 "
}
```

sample response:

```json

{
    "start": "2018-05-02 00:00:00",
    "end": "2018-05-03 12:00:00",
    "scrobbles": [
        {
            "Album": "Can't Hide feat. Ashe",
            "Artist": "Whethan",
            "Date": "2018-05-02 23:12:51",
            "Title": "Can't Hide"
        },
        {
            "Album": "Elixir",
            "Artist": "Breaux",
            "Date": "2018-05-02 23:09:34",
            "Title": "Elixir"
        },
        ...
    ]
}
```

2: Top songs listened to:

`/scrobbles/:lastfm username/top-tracks`

parameters:

- start
- end
- limit (optional) - how many items to return, default 5.

sample request data:

```json
{
    "start": "2018-5-02 ",
    "end": "2018-5-03 12:0:0 ",
    "limit":3
}

```

sample response:

```json

{
    "start": "2018-05-02 00:00:00",
    "end": "2018-05-03 12:00:00",
    "top tracks": [
        {
            "played": 2,
            "track": {
                "album": "Work It Out (Live)",
                "artist": "Tye Tribbett",
                "title": "Work It Out - Live"
            }
        },
        {
            "played": 1,
            "track": {
                "album": "Can't Hide feat. Ashe",
                "artist": "Whethan",
                "title": "Can't Hide"
            }
        },
        {
            "played": 1,
            "track": {
                "album": "Elixir",
                "artist": "Breaux",
                "title": "Elixir"
            }
        }
    ]
}

```

3: Top albums listened to:
same parameters as `/top-tracks/`

`/scrobbles/:lastfm username/top-albums`

sample repsonse:

```json
{
    "start": "2017-06-02 00:00:00",
    "end": "2017-06-16 12:00:00",
    "top albums": [
        {
            "album": "V2...",
            "album artist": "J Moss",
            "played": 4
        },
        {
            "album": "Shibuya",
            "album artist": "DROELOE",
            "played": 3
        },
        {
            "album": "Ready",
            "album artist": "Wide Awake",
            "played": 3
        }
    ]
}
```

4: Top artists listened to:
same parameters as `2`

sample response:

```json
{
    "start": "2017-05-02 00:00:00", 
    "end": "2018-05-03 12:00:00",
    "top albums": [
        {
            "artist": "Phyno",
            "played": 53
        },
        {
            "artist": "AyokAy",
            "played": 46
        },
        {
            "artist": "Sean Tizzle",
            "played": 44
        }
    ]
}
```

5: Frequency of listening per period

parameters:

- `start` and `end` datetime as other endpoints
- `scale`: the scale to count listens for (i.e tracks streamed per hour, day, week...)
    acepted values: *hours, days, weeks, months, years*

sample request:

```json
{
    "start":"2018-06-19",
    "end": "2018-06-21",
    "scale":"hours"
}
```

sample reponse:

```json
{
    "end": "2018-06-21 00:00:00",
    "frequency": {
        "2018-06-19 00:00:00": 1,
        "2018-06-19 01:00:00": 0,
        "2018-06-19 02:00:00": 0,
        "2018-06-19 03:00:00": 6,
        "2018-06-19 04:00:00": 0,
        "2018-06-19 05:00:00": 0,
        "2018-06-19 06:00:00": 0,
        "2018-06-19 07:00:00": 0,
        "2018-06-19 08:00:00": 0,
        "2018-06-19 09:00:00": 0,
        "2018-06-19 10:00:00": 0,
        "2018-06-19 11:00:00": 0,
        "2018-06-19 12:00:00": 0,
        "2018-06-19 13:00:00": 10,
        "2018-06-19 14:00:00": 4,
        "2018-06-19 15:00:00": 0,
        ...
    },
    "start": "2018-06-19 00:00:00"
}
```

6. Update user scrobbles: updates the database with scrobbles from last fm (takes a long time for the first time/depening on scrobbling history)
`/scrobbles/:username/update`
