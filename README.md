# Next Episode


## Overview

A simple script that generates next episode and their air date for TV shows using [TVmaze API](https://www.tvmaze.com/api). The information cached for each TV show has the below structure:

```
"show_id":
          {
            "id": integer,
            "name": string,
            "status": string,
            "air_time": string,
            "air_days": list,
            "imdb_id": string,
            "next_episode": {
                "id": integer,
                "season": integer,
                "episode": integer,
                "name": string,
                "air_date": string,
                "air_time": string
            }
          }
```

This enables request limiting since there is no need to GET information about TV shows that have ended. Also if currently the nextepisode is missing it means that the renewal status is unknown; it's better to avoid those requests frequently.

## Dependencies

This project is built in Python 2.7 however it should run in Python 3.x as well. Apart from **requests** all the libraries used are part of the default python environment.

## Running the script

In a terminal or command window, execute `next_episode.py --shows=path_to_json_file` to update the same file with updated details from the api. The json file passed to `--shows` parameter should contain at least one show_id as keys as shown below:

```
{
    "show_id" : null or valid json,
}
```

If the above value in json is null, the script would update it with details as defined in the above section. However if it contains valid information, the script would update the same.

### Command line options

In a terminal or command window, execute `next_episode.py --help` to see all the command line options.

## View results

The script has a function defined that generates the result in a table in an html file with name `next_episode_{timestamp}.html` with the following headers: **air\_days, air\_date, air\_time, name, season, episode and title**. However since we have the data in a structured format a separate technique can easily be used to display the result, for example in a plain text format.
