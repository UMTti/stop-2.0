import requests
import json
import datetime


class StopSchedule:
    def __init__(self, stop_id="HSL:1362141"):
        date = datetime.datetime.now().strftime("%Y%m%d")
        self.url = "http://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
        self.headers = {'Content-Type': 'application/graphql'}

        self.query = ("{stop(id: \"%s\") {"
                      "  name"
                      "  code"
                      "  stoptimesForServiceDate(date: \"%s\"){"
                      "    pattern {"
                      "      id"
                      "      name"
                      "      directionId"
                      "      route {"
                      "        gtfsId"
                      "        shortName"
                      "        longName"
                      "      }"
                      "    }"
                      "      stoptimes {"
                      "        serviceDay"
                      "      	scheduledArrival"
                      "    	realtimeArrival"
                      "      }"
                      "    }"
                      "  }"
                      "}") % (stop_id, date)

    def schedule(self):
        r = requests.post(self.url, data=self.query, headers=self.headers)
        data = json.loads(r.text)["data"]["stop"]

        lines = data["stoptimesForServiceDate"]

        current_time = datetime.datetime.now()

        stop = {'stop_name': data["name"], 'stop_code': data["code"], 'schedule': []}
        schedule = []
        for line in lines:
            name = (line["pattern"]["route"]["shortName"])
            stoptimes = line["stoptimes"]
            for time in stoptimes:
                arrival = datetime.datetime.fromtimestamp(time["serviceDay"] + time["realtimeArrival"])
                if current_time < arrival:
                    schedule.append({'line': name, 'arrival': arrival.strftime("%s"),
                                     'routeId': line["pattern"]["route"]["gtfsId"],
                                     'direction': line["pattern"]["directionId"]})


        sorted_list = sorted(schedule, key=lambda k: k['arrival'])
        stop["schedule"] = sorted_list
        print(sorted_list)

        return stop
