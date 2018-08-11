import requests, json, inspect, time
from random import randint
from datetime import datetime

def display_debug(expression, indent = "", debug = False):
   if not debug:
      return
   caller = inspect.stack()[1][3]
   print("{}[DEBUG] : [{}] : {}".format(indent, caller, expression))


def serialize(response, debug = False):
   display_debug("Serializing JSON for TV show: {}".format(response.get("name")), indent="    ", debug=debug)

   serialized = {
      "id"           : response.get("id"),
      "name"         : response.get("name"),
      "status"       : response.get("status"),
      "air_time"     : response.get("schedule").get("time"),
      "air_days"     : response.get("schedule").get("days"),
      "imdb_id"      : response.get("externals").get("imdb"),
      "next_episode" : None
   }

   try:
      nextepisode = response.get("_embedded").get("nextepisode")
      serialized["next_episode"] = {
         "id": nextepisode.get("id"),
         "season": nextepisode.get("season"),
         "episode": nextepisode.get("number"),
         "name": nextepisode.get("name"),
         "air_date": nextepisode.get("airdate"),
         "air_time": nextepisode.get("airtime")
      }
   except:
      display_debug("No new episodes found for TV show: {}".format(response.get("name")), indent="    ", debug=debug)
      pass

   return serialized


def get_details(shows, hard_refresh = False, debug = False):
   with open(shows, 'r') as f:
      shows_json = json.load(f)
   display_debug("Found {} TV shows to process.".format(len(shows_json)), indent="", debug=debug)
   
   api_url = "https://api.tvmaze.com/shows/{}?embed=nextepisode"
   for show_id, show_details in shows_json.iteritems():
      display_debug("Processing TV show: {}".format(show_id), indent="  ", debug=debug)
      url = api_url.format(show_id)
      if show_details is not None:
         name = show_details.get("name")
         status = show_details.get("status")
         next_episode = show_details.get("next_episode")
         if status.lower() == "ended":
            display_debug("[CACHED] Skipping TV show: {} since it has already ended.".format(name), indent="    ", debug=debug)
            continue
         elif next_episode is None and not hard_refresh:
            display_debug("[CACHED] Skipping TV show: {} since it's currently missing nextepisode.".format(name), indent="    ", debug=debug)
            continue
      display_debug("[GET] {}".format(url), indent="    ", debug=debug)
      r = requests.get(url)
      shows_json[show_id] = serialize(json.loads(r.content), debug=debug)
      time.sleep(randint(3, 7))

   with open(shows, 'w') as f:
      f.write(json.dumps(shows_json, indent=4))

   return shows_json


def display_next_episode(shows_json, debug = False):
   shows_json = [ show_details for show_id, show_details in shows_json.iteritems() if show_details.get("next_episode") is not None ]
   shows_json = sorted(shows_json, key=lambda x: (x["next_episode"]["air_date"], x["next_episode"]["air_time"]))
   
   timestamp = datetime.fromtimestamp(time.time()).strftime("%Y.%m.%d-%H.%M.%S")
   html_string = """
   <html>
      <head>
         <title>Next Episodes</title>
      </head>
      
      <body>"""
   html_string += "\n      <p>Updated on {}</p>".format(timestamp)
   html_string += "\n      <table border=\"1\">\n"
   html_string += """         <tr><th>air_days</th><th>air_date</th><th>air_time</th><th>name</th><th>season</th><th>episode</th><th>title</th></tr>"""
   html_string += "\n"
   
   for item in shows_json:
      air_date = item["next_episode"]["air_date"]
      air_time = item["next_episode"]["air_time"]
      name = item["name"]
      season = item["next_episode"]["season"]
      episode = item["next_episode"]["episode"]
      title = item["next_episode"]["name"]
      air_days = ",".join(item["air_days"])
      html_string = html_string + "         <tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format( \
         air_days, air_date, air_time, name, season, episode, title)

   html_string += """      </table>
      </body>
   </html>"""

   with open("next_episode_{}.html".format(timestamp), 'w') as f:
      f.write(html_string)
   
   return


def main():
   import argparse
   parser = argparse.ArgumentParser(description="Get the next episode for TV shows.")
   required_arguments = parser.add_argument_group('required arguments')
   required_arguments.add_argument("-s", "--shows", help="specify the json file where tvmaze identifiers are present", dest="shows", required=True)
   parser.add_argument("-hr", "--hard-refresh", help="forces GET for TV shows with current unknown nextepisode", dest="hard_refresh", action="store_true")
   parser.add_argument("-d", "--debug", help="display debug information", dest="debug", action="store_true")
   args = parser.parse_args()

   shows_json = get_details(shows=args.shows, hard_refresh=args.hard_refresh, debug=args.debug)
   display_next_episode(shows_json=shows_json, debug=args.debug)
   
   return


if __name__ == "__main__":
   main()

