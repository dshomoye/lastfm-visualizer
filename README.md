# LastFM API wrapper

API orchestration to get better insight into LastFM listening history/date bank.

> Also, the lastFM API is *not* great... 🤨

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
    "date": "2018-05-02 00:00:00 2018-05-03 12:00:00",
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
    "date": "2018-05-02 00:00:00 2018-05-03 12:00:00",
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
    "date": "2017-06-02 00:00:00 2017-06-16 12:00:00",
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
    "date": "2017-05-02 00:00:00 2018-05-03 12:00:00",
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