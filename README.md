API orchestration to get better insight into LastFM listening history/date bank.
Currently only relies on history to provide:

`/scrobbles/:lastfm username`
- scrobbles within a provided date range.

parameters:
- `start` (required): the start of the date range, supports most standard date formats
- `end` (required): same as `start`

sample reqeust:
`/scrobbles/sonofatailor`

data (application/json):
```
{
	"start": "2018-5-02 ",
	"end": "2018-5-03 12:0:0 "
}
```

sample response:
```
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