from zeep import Client, Settings, xsd
from zeep.plugins import HistoryPlugin
import pandas as pd

LDB_TOKEN = ''
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
#Station list 
crs_list = ['PTH', 'DEE', 'ABD', 'INV']

#DEPARTURES CODE
depart = []

for crs in crs_list:
    try:
        dep = client.service.GetDepartureBoard(numRows=10, crs=crs, _soapheaders=[header_value])
        services = dep.trainServices.service
        for service in services:
            depart.append({
                "type": "Departure",
                "station": dep.locationName,
                "std": service.std,
                "destination": service.destination.location[0].locationName,
                "etd": service.etd, 
                "platform": service.platform, 
                "cancelled": service.isCancelled, 
                "cancel_reason": service.cancelReason, 
                "delay_reason": service.delayReason
                
            })
    except Exception as e:
        print(f"Failed to fetch data for CRS: {crs}. Error: {e}")

df_depart = pd.DataFrame(depart)
df_depart.to_csv(r"data/departures.csv", index = False)


#ARRIVALS CODE
arrive = []

for crs in crs_list:
    try:
        arr = client.service.GetArrBoardWithDetails(numRows=10, crs=crs, _soapheaders=[header_value])
        serv_arriv = arr.trainServices.service
        for service in serv_arriv:
            arrive.append({
                "type": "Arrival",
                "station": arr.locationName,
                "sta": service.sta,
                "destination": service.origin.location[0].locationName,
                "eta": service.eta, 
                "platform": service.platform,
                "cancelled": service.isCancelled, 
                "cancel_reason": service.cancelReason, 
                "delay_reason": service.delayReason
            })
    except Exception as e:
        print(f"Failed to fetch data for CRS: {crs}. Error: {e}")

df_arrive = pd.DataFrame(arrive)
df_arrive.to_csv(r"data/arrivals.csv", index = False)


