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

from zeep import Client, Settings, xsd
from zeep.plugins import HistoryPlugin

# I want to get trains that call at some two stations
# so I need any trains that leave station X and have callingPoints.crs Y
# First: hardcode stations
# Then: make it configurable

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

print("What station are you going from? (Input 3 letter code)")
my_start = input()
print("What station are you going to? (Input 3 letter code)")
my_dest = input()
crs_list = [my_start,]

for station in crs_list:
#    res = client.service.GetDepBoardWithDetails(numRows=30, crs=station, _soapheaders=[header_value])
    res = client.service.GetDepBoardWithDetails(numRows=10, crs=station, _soapheaders=[header_value])

    print("Trains at " + res.locationName)
    print("===============================")

    trainServices= res.trainServices
#    print(trains)
    print("For station: " + station + " to: " + my_dest)
    for train in trainServices["service"]:
#        print(train)
        lists_of_stops = train.subsequentCallingPoints['callingPointList']
        counter = 0
        for list_of_stops in lists_of_stops:
#            print(list_of_stops)
            # this is the actual list of stops, per train
#            print(list_of_stops['callingPoint'])
            for stop in list_of_stops['callingPoint']:
                stop_code = (stop['crs'])
                if stop_code == my_dest:
#                    print(train)
                    if train['isCancelled']:
                        print("[[Cancelled train hidden from list.]]\n")
                    else:
                        print("\n")
                        print("Train leaves at " + train['std'])
                        print("Train leaves from platform " + str(train['platform']))
                        print("Train arrives at " + my_dest + " at " + stop['st'])
                        print("\n")

