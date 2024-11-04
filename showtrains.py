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

import argparse
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

# We add --start and --dest as optional commandline args, so the script can
# easily be called by a shellscript or similar for frequent journeys
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start",
                    help="departure station (three-letter code)")
parser.add_argument("-d", "--dest",
                    help="arrival station (three-letter code)")
parser.add_argument("-r", "-rev", "--reverse",
                    help="also display reverse journey", action="store_true")
args = parser.parse_args()

# TODO: commandline --l flag that lists 3-letter codes mapped to
# station names. Apparently there are about 2500 stations in the UK, so the
# implementation will require a bit of thought. :)

def list_trains(my_start, my_dest):
    my_start = my_start.upper()
    my_dest = my_dest.upper()
    # GetDepBoardWithDetails is limited to listing 10 departures.
    # But we have to use it, because it's the endpoint that includes stops
    # for each train. In contrast, GetDeparturesBoard retrieves unlimited
    # departures, but no stops, only the 'destination'.
    # This refers to the final stop on the train's route.
    # A hacky workaround (to be implemented) is to use time offsets to get
    # more results; you can offset by up to 2 hours, with timeOffset=119.
    # That's still not very  much,
    # though for smaller stations it may be sufficient.
    # Hopefully there's some way around this limitation...
    res = client.service.GetDepBoardWithDetails(numRows=10, crs=my_start, _soapheaders=[header_value])

    print("\n Trains from " + res.locationName)
    print("===============================")

    trainServices= res.trainServices
    print(my_start + " to " + my_dest)
    try:
        for train in trainServices["service"]:
            lists_of_stops = train.subsequentCallingPoints['callingPointList']
            for list_of_stops in lists_of_stops:
                # this is the actual list of stops, per train
                for stop in list_of_stops['callingPoint']:
                    stop_code = (stop['crs'])
                    if stop_code == my_dest:
                        if train['isCancelled']:
                            print("\n [[Cancelled train hidden from list.]]\n")
                        else:
                            print("\n Train leaves " + my_start + " at " + train['std'])
                            print("Train leaves from platform " + str(train['platform']))
                            print("Train arrives at " + my_dest + " at " + stop['st'])
    except TypeError:
        print("NO TRAINS.")
    print("\n")

# Check for commandline arguments; if none, ask user for input interactively
if args.start and args.dest != None:
    list_trains(args.start, args.dest)
    if args.reverse:
        list_trains(args.dest, args.start)
else:
    print("What station are you going from? (Input 3 letter code)")
    start = input()

    # TODO: Let user list multiple destinations at once
    print("What station are you going to? (Input 3 letter code)")
    dest = input()
    list_trains(start, dest)
    print("Reverse journey? (y/n)")
    if input() == "y" or "Y" or "yes" or "YES":
        list_trains(dest, start)
