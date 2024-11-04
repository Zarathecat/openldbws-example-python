#
# Open Live Departure Boards Web Service (OpenLDBWS) API Demonstrator
# Copyright (C)2018-2024 OpenTrainTimes Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# THE ORIGINAL EXAMPLE IS TAKEN FROM HERE:
# https://github.com/openraildata/openldbws-example-python
# GPL! GPL!
# The SOAP stuff is all copied from there.

# This script lets you see what trains are leaving from some station,
# to some other station. You'd think it'd be very simple, but.

from zeep import Client, Settings, xsd
from zeep.plugins import HistoryPlugin


with open(".apikey") as file:
    LDB_TOKEN = file.read().rstrip()
WSDL = 'http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01'

if LDB_TOKEN == '':
    raise Exception("Please configure your OpenLDBWS token in getDepartureBoardExample!")

settings = Settings(strict=False)

history = HistoryPlugin()

client = Client(wsdl=WSDL, settings=settings, plugins=[history])

header = xsd.Element(
    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
    xsd.ComplexType([
        xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
            xsd.String()),
    ])
)
header_value = header(TokenValue=LDB_TOKEN)

# TODO: commandline --h flag that lists 3-letter codes mapped to
# station names.

print("What station are you going from? (Input 3 letter code)")
start = input()

# TODO: Let user list multiple destinations at once
print("What station are you going to? (Input 3 letter code)")
dest = input()


def list_trains(my_start, my_dest):
    station = my_start
    # GetDepBoardWithDetails is limited to listing 10 departures.
    # But we have to use it, because it's the endpoint that includes stops
    # for each train. In contrast, GetDeparturesBoard retrieves unlimited
    # departures, but no stops, only the 'destination'.
    # This refers to the final stop on the train's route.
    # A hacky workaround (to be implemented) is to use time offsets to get
    # more results; you can offset by up to 2 hours. That's still not very
    # much, though for smaller stations it may be sufficient.
    # Hopefully there's some way around this limitation...
    res = client.service.GetDepBoardWithDetails(numRows=10, crs=station, _soapheaders=[header_value])

    print("Trains at " + res.locationName)
    print("===============================")

    trainServices= res.trainServices
    print("For station: " + station + " to: " + my_dest)
    for train in trainServices["service"]:
        lists_of_stops = train.subsequentCallingPoints['callingPointList']
        for list_of_stops in lists_of_stops:
            # this is the actual list of stops, per train
            for stop in list_of_stops['callingPoint']:
                stop_code = (stop['crs'])
                if stop_code == my_dest:
                    if train['isCancelled']:
                        print("[[Cancelled train hidden from list.]]\n")
                    else:
                        print("\n")
                        print("Train leaves at " + train['std'])
                        print("Train leaves from platform " + str(train['platform']))
                        print("Train arrives at " + my_dest + " at " + stop['st'])
                        print("\n")

list_trains(start, dest)
print("Reverse journey? (y/n)")
if input() == "y":
    list_trains(dest, start)
