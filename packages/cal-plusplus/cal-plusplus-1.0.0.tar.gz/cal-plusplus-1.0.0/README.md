# cal-plusplus

`cal-plusplus` displays a calendar on your command line with [`workalendar`][workalendar] integration for showing working days.

![CLI output from the updated cal command showing weekends and public holidays in a lighter colour to regular weekdays](example.png)

### Installation

Install with pip:

```
pip install --user cal-plusplus
```


### Usage

Display current year, attempt to detect your region (it will be displayed in the title):

```
cal
```

Specify calendar from `workalendar` to use:

```
cal --calendar=AU-VIC
```

Alternatively you can set the `CALPLUSPLUS` environment variable to the name of the calendar you would like to use.

Specify a year to display a calendar for:

```
cal 2024
```

Output a list of valid calendars:

```
cal --show-calendars
```


  [workalendar]: https://github.com/workalendar/workalendar
