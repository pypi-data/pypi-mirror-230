# ERA5 driver
 Climate reanalysis produced by ECMWF driver.

# Nodes
### Era5ServiceNode
Represents the Climate Data Store (CDS) service. This node allows to parse dataset of
Climate Data Store like https://cds.climate.copernicus.eu/api/v2.
The service have for children the era5 dataset:
    'reanalysis-era5-land'
    'reanalysis-era5-land-monthly-means'
    'reanalysis-era5-single-levels'
    'reanalysis-era5-single-levels-monthly-means'
    'reanalysis-era5-pressure-levels'
    'reanalysis-era5-pressure-levels-monthly-means'

### Era5NodeDataSet

Each child of Era5ServiceNode is a Era5NodeDataSet that represent a ERA5 dataset
Era5NodeDataSet have for children the variables of this Dataset

To access of data of the dataset we can access by children if the variable is predefined as children of dataset

Or directly from the Dataset by either a dict or a predicate

To know the predicate supported by the dataset

```
dataset_node.get_predicate_allowed()
```


### EraNode

EraNode are the children of dataset
They define the variables predefined of the dataset parent.
We can access to the no predefined variable of the dataset, by using predicate or by using dict (by define variable parameter)


### Era5Predicate

To access Data of Dataset, it is necessary to indicate the filter used
Each Dataset can be filtered by a Predicate or by a dict

Each Dataset have each predicate

List of dataset and associated predicate:
*    'reanalysis-era5-land'                          => Era5PredicateEra5Land
*    'reanalysis-era5-land-monthly-means'            => Era5PredicateEra5SingleLevelsByMonth
*    'reanalysis-era5-single-levels'                 => Era5PredicateEra5SingleLevelsByHour
*    'reanalysis-era5-single-levels-monthly-means'   => Era5PredicateEra5SingleLevelsByMonth
*    'reanalysis-era5-pressure-levels'               => Era5PredicateEra5PressureLevelByHour
*    'reanalysis-era5-pressure-levels-monthly-means' => Era5PredicateEra5PressureLevelsByMonth



If predicate is apply directly on dataset, it is used for all variables of the dataset


To create a predicate

```
my_predicate= Era5PredicateEra5SingleLevelsByHour(year=2011, 
                                                  month=12, 
                                                  day=1, 
                                                  time=[1, 2 ,3], 
                                                  product_type='ensemble_spread')
```

In predicate, we can define the variable parameter

If variable is not defined :

   - If the predicate is applied on aEra5NodeDataSet all predefined variables of the dataset are filtered
   - If the predicate is applied in a child of dataset EraNode, the predicate is applied only on this variable (except if variable is define din predicate)

Example wit variable defined

```
my_predicate= Era5PredicateEra5SingleLevelsByHour(year=2011, 
                                                  month=12, 
                                                  day=1, 
                                                  time=[1, 2 ,3], 
                                                  product_type='ensemble_spread',
                                                  variable=['2m_dewpoint_temperature', '2m_temperature'])
```

Each predicate have a year, month, time, area (by default None) and a format by default (netcdf)
Each parameter of constructor of predicate can be a list or a value 
except the format: in the example above the time are 1, 2 and 3 and the area that can be only a list.

Month begin 1 for january

Area if not None is a array that define the North, West, South and East in Latitude Longitude 

for example area = [90, -180, -90, 180] for the whole map.


All predicate except Era5PredicateEra5Land have product_type.
Product can be a unique product or a list of product 

like product_type = ['monthly_averaged_ensemble_members', 'monthly_averaged_reanalysis']

List of product possible for each dataset

'reanalysis-era5-land-monthly-means':
*    monthly_averaged_reanalysis (default value)
*    monthly_averaged_reanalysis_by_hour_of_day

'reanalysis-era5-single-levels' and 'reanalysis-era5-pressure-levels' :
*    ensemble_mean
*    ensemble_members
*    ensemble_spread
*    reanalysis (default value)

'reanalysis-era5-single-levels-monthly-means' and 'reanalysis-era5-pressure-levels-monthly-means' :
*    monthly_averaged_ensemble_members
*    monthly_averaged_ensemble_members_by_hour_of_day
*    monthly_averaged_reanalysis (default value)
*    monthly_averaged_reanalysis_by_hour_of_day

For Monthly predicate: If name(s) of product_type don't contain by_hour_of_day the only time value allowed is zero 
By default the value of time is zero by default for Monthly predicate.

The predicate that doesn't finish by Month have in addition a day parameter.
The day is the day in the month (begin by 1)

For predicate that name contains pressure a parameter pressure_level is defined (by default it is zero) the unit of this value is the hectopascal (hPa)

```
# Predicate to retrieve the mean of a variable for december 2011, for the pressure level 1 hPa
without take count of the hour of fay.
my_predicate_pressure= Era5PredicateEra5PressureLevelsByMonth(year=2011,
                                                            month=12)
```

In the example above the product_type is 'monthly_averaged_reanalysis' and time is 0
and pressure_level is 1

Same example with product_type, time and pressure level different


```
# Predicate to retrieve the mean of a variable for december 2011, for the pressure level 10 and 12 hPa
and at 1 PM

my_predicate_pressure= Era5PredicateEra5SingleLevelsByMonth(year=2011,
                                                            month=12, 
                                                            pressure_level=[10, 12],
                                                            product_type='monthly_averaged_reanalysis_by_hour_of_day',
                                                            time=13)
                                                            
                                                           
```


### Examples

Example without access child '2m_temperature' of Dataset 'reanalysis-era5-pressure-levels': 
```
import xarray
from drb.utils import keyringconnection

from drb.drivers.era5 import Era5ServiceNode, Era5PredicateEra5SingleLevelsByHour

# Add credential in the keyring
keyringconnection.kr_add(service='https://cds.climate.copernicus.eu/api/v2',
                         username='111111',
                         password='11111-9c6d-4a0c-8dce-5552c5f99878')

# by default the source is https://cds.climate.copernicus.eu/api/v2'
service_era5 = Era5ServiceNode()

predicate = Era5PredicateEra5SingleLevelsByHour(year=1959, month=1, day=1, time=[11, 12])



res = service_era5['reanalysis-era5-pressure-levels']['2m_temperature'][predicate]

res['root']['variables']['t2m'].get_impl(xarray.DataArray)
```

Example without access children of Dataset 'reanalysis-era5-pressure-levels':
```
import xarray

from drb.drivers.era5 import Era5ServiceNode, Era5PredicateEra5SingleLevelsByHour

my_id = '11111:11111-9c6d-4a0c-8dce-5552c5f99878'

service_era5 = Era5ServiceNode(auth=my_id)
# is same as service_rea5 = Era5ServiceNode('https://cds.climate.copernicus.eu/api/v2', auth=my_id)

predicate = Era5PredicateEra5SingleLevelsByHour(year=1959, month=1, day=1, time=0,
                                                variable='2m_temperature')



res = service_era5['reanalysis-era5-pressure-levels'][predicate]

res['root']['variables']['t2m'].get_impl(xarray.DataArray)

# you can make the same by dict

dict_request = {
    'product_type': 'reanalysis',
    'variable': '2m_temperature',
    'year': '1959',
    'month': '1',
    'day': '1',
    'time': '0',
    'format': 'netcdf'
}

res = service_era5['reanalysis-era5-pressure-levels'][dict_request]
# ...

# you can also request a list of variables or a list of product_type
# by default product_type in predicate is 'reanalysis'

predicate = Era5PredicateEra5SingleLevelsByHour(year=1959, month=1, day=1, time=0
                                                variable=['2m_temperature', 'skin_temperature'],
                                                product_type=['ensemble_mean', 'ensemble_members'])

res = service_era5['reanalysis-era5-pressure-levels'][predicate]

```



# Installation
```
pip install drb-driver-era5
```




