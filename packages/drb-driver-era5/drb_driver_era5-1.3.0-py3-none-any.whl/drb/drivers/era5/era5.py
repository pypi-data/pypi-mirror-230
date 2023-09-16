from __future__ import annotations

import abc
from enum import Enum
from urllib.parse import urlparse

import keyring
from deprecated.classic import deprecated
from drb.core import Predicate, DrbNode, ParsedPath, DrbFactory
from drb.drivers.http import DrbHttpNode
from drb.exceptions.core import DrbException, DrbFactoryException
from drb.nodes.abstract_node import AbstractNode
from drb.topics import resolver
from requests.auth import AuthBase, HTTPBasicAuth
from typing import List, Union
import cdsapi

list_predefined_variables_era5_land = [
    '10m_u_component_of_wind', '10m_v_component_of_wind',
    '2m_dewpoint_temperature',
    '2m_temperature', 'evaporation_from_bare_soil',
    'evaporation_from_open_water_surfaces_excluding_oceans',
    'evaporation_from_the_top_of_canopy',
    'evaporation_from_vegetation_transpiration', 'forecast_albedo',
    'lake_bottom_temperature', 'lake_ice_depth', 'lake_ice_temperature',
    'lake_mix_layer_depth', 'lake_mix_layer_temperature', 'lake_shape_factor',
    'lake_total_layer_temperature', 'leaf_area_index_high_vegetation',
    'leaf_area_index_low_vegetation',
    'potential_evaporation', 'runoff', 'skin_reservoir_content',
    'skin_temperature', 'snow_albedo', 'snow_cover',
    'snow_density', 'snow_depth', 'snow_depth_water_equivalent',
    'snow_evaporation', 'snowfall', 'snowmelt',
    'soil_temperature_level_1', 'soil_temperature_level_2',
    'soil_temperature_level_3',
    'soil_temperature_level_4', 'sub_surface_runoff',
    'surface_latent_heat_flux',
    'surface_net_solar_radiation', 'surface_net_thermal_radiation',
    'surface_pressure',
    'surface_runoff', 'surface_sensible_heat_flux',
    'surface_solar_radiation_downwards',
    'surface_thermal_radiation_downwards', 'temperature_of_snow_layer',
    'total_evaporation',
    'total_precipitation', 'volumetric_soil_water_layer_1',
    'volumetric_soil_water_layer_2',
    'volumetric_soil_water_layer_3', 'volumetric_soil_water_layer_4']

list_predefined_variables_era5_singles_levels = [
    '100m_u_component_of_wind', '100m_v_component_of_wind',
    '10m_u_component_of_neutral_wind',
    '10m_u_component_of_wind', '10m_v_component_of_neutral_wind',
    '10m_v_component_of_wind',
    '10m_wind_gust_since_previous_post_processing', '2m_dewpoint_temperature',
    '2m_temperature',
    'air_density_over_the_oceans', 'angle_of_sub_gridscale_orography',
    'anisotropy_of_sub_gridscale_orography',
    'benjamin_feir_index', 'boundary_layer_dissipation',
    'boundary_layer_height',
    'charnock', 'clear_sky_direct_solar_radiation_at_surface',
    'cloud_base_height',
    'coefficient_of_drag_with_waves', 'convective_available_potential_energy',
    'convective_inhibition',
    'convective_precipitation', 'convective_rain_rate', 'convective_snowfall',
    'convective_snowfall_rate_water_equivalent',
    'downward_uv_radiation_at_the_surface', 'duct_base_height',
    'eastward_gravity_wave_surface_stress',
    'eastward_turbulent_surface_stress',
    'evaporation',
    'forecast_albedo', 'forecast_logarithm_of_surface_roughness_for_heat',
    'forecast_surface_roughness',
    'free_convective_velocity_over_the_oceans', 'friction_velocity',
    'geopotential',
    'gravity_wave_dissipation', 'high_cloud_cover', 'high_vegetation_cover',
    'ice_temperature_layer_1', 'ice_temperature_layer_2',
    'ice_temperature_layer_3',
    'ice_temperature_layer_4', 'instantaneous_10m_wind_gust',
    'instantaneous_eastward_turbulent_surface_stress',
    'instantaneous_large_scale_surface_precipitation_fraction',
    'instantaneous_moisture_flux',
    'instantaneous_northward_turbulent_surface_stress',
    'instantaneous_surface_sensible_heat_flux', 'k_index',
    'lake_bottom_temperature',
    'lake_cover', 'lake_depth', 'lake_ice_depth',
    'lake_ice_temperature', 'lake_mix_layer_depth',
    'lake_mix_layer_temperature',
    'lake_shape_factor', 'lake_total_layer_temperature', 'land_sea_mask',
    'large_scale_precipitation', 'large_scale_precipitation_fraction',
    'large_scale_rain_rate',
    'large_scale_snowfall', 'large_scale_snowfall_rate_water_equivalent',
    'leaf_area_index_high_vegetation',
    'leaf_area_index_low_vegetation',
    'low_cloud_cover', 'low_vegetation_cover',
    'maximum_2m_temperature_since_previous_post_processing',
    'maximum_individual_wave_height',
    'maximum_total_precipitation_rate_since_previous_post_processing',
    'mean_boundary_layer_dissipation', 'mean_convective_precipitation_rate',
    'mean_convective_snowfall_rate',
    'mean_direction_of_total_swell', 'mean_direction_of_wind_waves',
    'mean_eastward_gravity_wave_surface_stress',
    'mean_eastward_turbulent_surface_stress', 'mean_evaporation_rate',
    'mean_gravity_wave_dissipation',
    'mean_large_scale_precipitation_fraction',
    'mean_large_scale_precipitation_rate', 'mean_large_scale_snowfall_rate',
    'mean_northward_gravity_wave_surface_stress',
    'mean_northward_turbulent_surface_stress', 'mean_period_of_total_swell',
    'mean_period_of_wind_waves', 'mean_potential_evaporation_rate',
    'mean_runoff_rate',
    'mean_sea_level_pressure', 'mean_snow_evaporation_rate',
    'mean_snowfall_rate',
    'mean_snowmelt_rate', 'mean_square_slope_of_waves',
    'mean_sub_surface_runoff_rate',
    'mean_surface_direct_short_wave_radiation_flux',
    'mean_surface_direct_short_wave_radiation_flux_clear_sky',
    'mean_surface_downward_long_wave_radiation_flux',
    'mean_surface_downward_long_wave_radiation_flux_clear_sky',
    'mean_surface_downward_short_wave_radiation_flux',
    'mean_surface_downward_short_wave_radiation_flux_clear_sky',
    'mean_surface_downward_uv_radiation_flux',
    'mean_surface_latent_heat_flux',
    'mean_surface_net_long_wave_radiation_flux',
    'mean_surface_net_long_wave_radiation_flux_clear_sky',
    'mean_surface_net_short_wave_radiation_flux',
    'mean_surface_net_short_wave_radiation_flux_clear_sky',
    'mean_surface_runoff_rate', 'mean_surface_sensible_heat_flux',
    'mean_top_downward_short_wave_radiation_flux',
    'mean_top_net_long_wave_radiation_flux',
    'mean_top_net_long_wave_radiation_flux_clear_sky',
    'mean_top_net_short_wave_radiation_flux',
    'mean_top_net_short_wave_radiation_flux_clear_sky',
    'mean_total_precipitation_rate',
    'mean_vertical_gradient_of_refractivity_inside_trapping_layer',
    'mean_vertically_integrated_moisture_divergence', 'mean_wave_direction',
    'mean_wave_direction_of_first_swell_partition',
    'mean_wave_direction_of_second_swell_partition',
    'mean_wave_direction_of_third_swell_partition', 'mean_wave_period',
    'mean_wave_period_based_on_first_moment',
    'mean_wave_period_based_on_first_moment_for_swell',
    'mean_wave_period_based_on_first_moment_for_wind_waves',
    'mean_wave_period_based_on_second_moment_for_swell',
    'mean_wave_period_based_on_second_moment_for_wind_waves',
    'mean_wave_period_of_first_swell_partition',
    'mean_wave_period_of_second_swell_partition',
    'mean_wave_period_of_third_swell_partition',
    'mean_zero_crossing_wave_period',
    'medium_cloud_cover',
    'minimum_2m_temperature_since_previous_post_processing',
    'minimum_total_precipitation_rate_since_previous_post_processing',
    'minimum_vertical_gradient_of_refractivity_inside_trapping_layer',
    'model_bathymetry', 'near_ir_albedo_for_diffuse_radiation',
    'near_ir_albedo_for_direct_radiation',
    'normalized_energy_flux_into_ocean',
    'normalized_energy_flux_into_waves',
    'normalized_stress_into_ocean', 'northward_gravity_wave_surface_stress',
    'northward_turbulent_surface_stress',
    'ocean_surface_stress_equivalent_10m_neutral_wind_direction',
    'ocean_surface_stress_equivalent_10m_neutral_wind_speed',
    'peak_wave_period',
    'period_corresponding_to_maximum_individual_wave_height',
    'potential_evaporation', 'precipitation_type',
    'runoff', 'sea_ice_cover', 'sea_surface_temperature',
    'significant_height_of_combined_wind_waves_and_swell',
    'significant_height_of_total_swell',
    'significant_height_of_wind_waves',
    'significant_wave_height_of_first_swell_partition',
    'significant_wave_height_of_second_swell_partition',
    'significant_wave_height_of_third_swell_partition',
    'skin_reservoir_content', 'skin_temperature',
    'slope_of_sub_gridscale_orography',
    'snow_albedo', 'snow_density', 'snow_depth',
    'snow_evaporation', 'snowfall', 'snowmelt',
    'soil_temperature_level_1', 'soil_temperature_level_2',
    'soil_temperature_level_3',
    'soil_temperature_level_4', 'soil_type',
    'standard_deviation_of_filtered_subgrid_orography',
    'standard_deviation_of_orography', 'sub_surface_runoff',
    'surface_latent_heat_flux',
    'surface_net_solar_radiation', 'surface_net_solar_radiation_clear_sky',
    'surface_net_thermal_radiation',
    'surface_net_thermal_radiation_clear_sky', 'surface_pressure',
    'surface_runoff',
    'surface_sensible_heat_flux',
    'surface_solar_radiation_downward_clear_sky',
    'surface_solar_radiation_downwards',
    'surface_thermal_radiation_downward_clear_sky',
    'surface_thermal_radiation_downwards', 'temperature_of_snow_layer',
    'toa_incident_solar_radiation', 'top_net_solar_radiation',
    'top_net_solar_radiation_clear_sky',
    'top_net_thermal_radiation', 'top_net_thermal_radiation_clear_sky',
    'total_cloud_cover',
    'total_column_cloud_ice_water', 'total_column_cloud_liquid_water',
    'total_column_ozone',
    'total_column_rain_water', 'total_column_snow_water',
    'total_column_supercooled_liquid_water',
    'total_column_water', 'total_column_water_vapour', 'total_precipitation',
    'total_sky_direct_solar_radiation_at_surface', 'total_totals_index',
    'trapping_layer_base_height',
    'trapping_layer_top_height', 'type_of_high_vegetation',
    'type_of_low_vegetation',
    'u_component_stokes_drift', 'uv_visible_albedo_for_diffuse_radiation',
    'uv_visible_albedo_for_direct_radiation',
    'v_component_stokes_drift',
    'vertical_integral_of_divergence_of_cloud_frozen_water_flux',
    'vertical_integral_of_divergence_of_cloud_liquid_water_flux',
    'vertical_integral_of_divergence_of_geopotential_flux',
    'vertical_integral_of_divergence_of_kinetic_energy_flux',
    'vertical_integral_of_divergence_of_mass_flux',
    'vertical_integral_of_divergence_of_moisture_flux',
    'vertical_integral_of_divergence_of_ozone_flux',
    'vertical_integral_of_divergence_of_thermal_energy_flux',
    'vertical_integral_of_divergence_of_total_energy_flux',
    'vertical_integral_of_eastward_cloud_frozen_water_flux',
    'vertical_integral_of_eastward_cloud_liquid_water_flux',
    'vertical_integral_of_eastward_geopotential_flux',
    'vertical_integral_of_eastward_heat_flux',
    'vertical_integral_of_eastward_kinetic_energy_flux',
    'vertical_integral_of_eastward_mass_flux',
    'vertical_integral_of_eastward_ozone_flux',
    'vertical_integral_of_eastward_total_energy_flux',
    'vertical_integral_of_eastward_water_vapour_flux',
    'vertical_integral_of_energy_conversion',
    'vertical_integral_of_kinetic_energy',
    'vertical_integral_of_mass_of_atmosphere',
    'vertical_integral_of_mass_tendency',
    'vertical_integral_of_northward_cloud_frozen_water_flux',
    'vertical_integral_of_northward_cloud_liquid_water_flux',
    'vertical_integral_of_northward_geopotential_flux',
    'vertical_integral_of_northward_heat_flux',
    'vertical_integral_of_northward_kinetic_energy_flux',
    'vertical_integral_of_northward_mass_flux',
    'vertical_integral_of_northward_ozone_flux',
    'vertical_integral_of_northward_total_energy_flux',
    'vertical_integral_of_northward_water_vapour_flux',
    'vertical_integral_of_potential_and_internal_energy',
    'vertical_integral_of_potential_internal_and_latent_energy',
    'vertical_integral_of_temperature', 'vertical_integral_of_thermal_energy',
    'vertical_integral_of_total_energy',
    'vertically_integrated_moisture_divergence',
    'volumetric_soil_water_layer_1',
    'volumetric_soil_water_layer_2', 'volumetric_soil_water_layer_3',
    'volumetric_soil_water_layer_4',
    'wave_spectral_directional_width',
    'wave_spectral_directional_width_for_swell',
    'wave_spectral_directional_width_for_wind_waves',
    'wave_spectral_kurtosis', 'wave_spectral_peakedness',
    'wave_spectral_skewness',
    'zero_degree_level', ]

list_predefined_variables_era5_pressure = [
    'divergence', 'fraction_of_cloud_cover', 'geopotential',
    'ozone_mass_mixing_ratio', 'potential_vorticity', 'relative_humidity',
    'specific_cloud_ice_water_content',
    'specific_cloud_liquid_water_content', 'specific_humidity',
    'specific_rain_water_content', 'specific_snow_water_content',
    'temperature',
    'u_component_of_wind', 'v_component_of_wind', 'vertical_velocity',
    'vorticity'
]

list_product_type_hourly = ['ensemble_mean', 'ensemble_members',
                            'ensemble_spread', 'reanalysis']

list_product_type_monthly = [
    'monthly_averaged_ensemble_members',
    'monthly_averaged_ensemble_members_by_hour_of_day',
    'monthly_averaged_reanalysis',
    'monthly_averaged_reanalysis_by_hour_of_day']

list_product_type_land_monthly = [
    'monthly_averaged_reanalysis',
    'monthly_averaged_reanalysis_by_hour_of_day']


class Era5PredicateEra5Base(Predicate):
    def __init__(self,
                 **kwargs):

        self.arg_dict = dict(kwargs)

    def to_dict(self):
        arg_dict = {}
        for key, value in self.arg_dict.items():
            if value is not None:
                arg_dict[key] = value
        return arg_dict

    def matches(self, node) -> bool:
        return False

    @staticmethod
    def check_hour_product_type(product_type):
        if '_hour_of_day' in product_type:
            return True
        return False

    @staticmethod
    def check_hour_product_type_list(*args):
        for product_type in args:
            if Era5PredicateEra5Base.check_hour_product_type(product_type):
                return True
        return False

    def check_time_for_montly_predicate(self):
        time = self.arg_dict['time']

        if time != 0:
            if not Era5PredicateEra5Base.check_hour_product_type_list(
                    self.arg_dict['product_type']):
                raise DrbException(f'With product type to ' +
                                   self.arg_dict['product_type'] +
                                   f' time must be zero.')


class Era5PredicateEra5Land(Era5PredicateEra5Base):
    # reanalysis-era5-land
    def __init__(self,
                 year,
                 month,
                 time,
                 day,
                 area=None,
                 format='netcdf',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         day=day,
                         **kwargs)


class Era5PredicateEra5LandMonthly(Era5PredicateEra5Base):
    # reanalysis-era5-land-monthly-means 1950 ...
    def __init__(self,
                 year,
                 month,
                 time=0,
                 product_type='monthly_averaged_reanalysis',
                 area=None,
                 format='netcdf',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)

        self.check_time_for_montly_predicate()


class Era5PredicateEra5SingleLevelsByMonth(Era5PredicateEra5Base):
    # reanalysis-era5-single-levels-monthly-means
    def __init__(self,
                 year,
                 month,
                 time=0,
                 area=None,
                 format='netcdf',
                 product_type='monthly_averaged_reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)
        self.check_time_for_montly_predicate()


class Era5PredicateEra5SingleLevelsByHour(Era5PredicateEra5Base):
    # reanalysis-era5-single-levels
    def __init__(self,
                 year,
                 month,
                 day,
                 time,
                 area=None,
                 format='netcdf',
                 product_type='reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         day=day,
                         time=time,
                         area=area,
                         format=format,
                         product_type=product_type,
                         **kwargs)


class Era5PredicateEra5PressureLevelsByMonth(Era5PredicateEra5Base):
    #  reanalysis-era5-pressure-levels-monthly-means
    def __init__(self,
                 year,
                 month,
                 time=0,
                 area=None,
                 pressure_level=1,
                 format='netcdf',
                 product_type='monthly_averaged_reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         time=time,
                         area=area,
                         pressure_level=pressure_level,
                         format=format,
                         product_type=product_type,
                         **kwargs)
        self.check_time_for_montly_predicate()


class Era5PredicateEra5PressureLevelByHour(Era5PredicateEra5Base):
    # reanalysis-era5-pressure-levels
    def __init__(self,
                 year,
                 month,
                 day,
                 time,
                 area=None,
                 pressure_level=1,
                 format='netcdf',
                 product_type='reanalysis',
                 **kwargs):
        super().__init__(year=year,
                         month=month,
                         day=day,
                         time=time,
                         area=area,
                         pressure_level=pressure_level,
                         format=format,
                         product_type=product_type,
                         **kwargs)


class Era5ServiceNodeCommon(AbstractNode, abc.ABC):
    def __init__(self, parent: DrbNode):
        super().__init__()

        self._path = None
        self.parent = parent
        self.namespace_uri = 'ERA5'

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            if self._parent is None:
                self._path = ParsedPath(f'/{self.name}')
            else:
                self._path = self.parent.path / self.name
        return self._path

    def get_predicate_allowed(self):
        return None

    @property
    @abc.abstractmethod
    def client_cds(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class Era5ServiceNode(Era5ServiceNodeCommon):

    def __init__(self, path='https://cds.climate.copernicus.eu/api/v2',
                 auth: Union[AuthBase, str] = None):
        super().__init__(None)
        self._children = None

        self._path = path.replace('+era5', '') if '+era5' in path else path
        self.name = self._path
        if len(self._path) == 0:
            self._path = 'https://cds.climate.copernicus.eu/api/v2'
        self._auth = auth

        self._cds = None

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    def client_cds(self):
        if self._cds is None:
            key = None
            if isinstance(self.auth, str):
                key = self.auth
            elif isinstance(self.auth, AuthBase):
                key = self.auth.username + ':' + self.auth.password
            if key is not None:
                self._cds = cdsapi.Client(
                    url=self._path,
                    key=key, verify=True)
            else:
                self._cds = cdsapi.Client(
                    url=self._path, verify=True)
        return self._cds

    @property
    def auth(self) -> Union[AuthBase, str]:
        if self._auth is not None:
            return self._auth
        if self._auth is None:
            credential = keyring.get_credential(
                service_name=self.path.path,
                username=None
            )
            if credential is not None:
                self._auth = HTTPBasicAuth(
                    credential.username,
                    credential.password
                )
        return self._auth

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []

            for enum_data_set in DataSetERA5:
                self._children.append(Era5NodeDataSet(self, enum_data_set))

        return self._children


class Era5NodeDataSet(Era5ServiceNodeCommon):

    def __init__(self, parent: Era5ServiceNode, dataset_enum: DataSetERA5):
        super().__init__(parent)

        self.name = dataset_enum.name
        self._children_name = dataset_enum.children
        self._children = None
        self._list_product_type = dataset_enum.list_product_type

        self._predicate_class = dataset_enum.predicate_class
        self.__init_attributes()

    def __init_attributes(self):
        if self._list_product_type is not None:
            self @= ('product_type', [v for v in self._list_product_type])

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    @deprecated(version='1.2.0',
                reason='Only bracket browse should be use')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            for child_name in self._children_name:
                self._children.append(EraNode(self, child_name))
        return self._children

    def execute_request(self, item):
        res = self.client_cds.retrieve(self.name, item)
        return EraNodeData(self, res.toJSON())

    def __get_item_dict(self, dict_request):
        if 'variable' not in dict_request.keys():
            dict_request['variable'] = self._children_name

        return self.execute_request(dict_request)

    def __getitem__(self, item):
        if isinstance(item, dict):
            return self.__get_item_dict(item)
        elif isinstance(item, Era5PredicateEra5Base):
            return self.__get_item_dict(item.to_dict())
        else:
            return super().__getitem__(item)

    def get_predicate_allowed(self):
        return self._predicate_class


class EraNode(Era5ServiceNodeCommon):

    def __init__(self, parent: Era5ServiceNode, name: str):
        super().__init__(parent)
        self.name = name
        self.__init_attributes()

    def __init_attributes(self):
        for k, v in self.parent.attributes:
            self.__imatmul__((k, self.parent.attributes[(k, v)]))

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    @deprecated(version='1.2.0',
                reason='Only bracket browse should be use')
    def children(self) -> List[DrbNode]:
        return []

    def __getitem__(self, item):
        dict_request = {}
        if isinstance(item, dict):
            dict_request = item
        if isinstance(item, Era5PredicateEra5Base):
            dict_request = item.to_dict()
        if 'variable' not in dict_request.keys():
            dict_request['variable'] = self.name
        return self.parent.execute_request(dict_request)


class EraNodeData(Era5ServiceNodeCommon):

    def __init__(self, parent: Era5ServiceNode, res):
        super().__init__(parent)
        self._parent = parent
        self.value = res
        self._child = None

        parsed_uri = urlparse(res['location'])
        self.name = str(parsed_uri.path).split('/')[-1]
        self.__init_attributes()

    def __init_attributes(self):
        for k, v in self.value.items():
            self.__imatmul__((k, v))

    @property
    def client_cds(self):
        return self.parent.client_cds

    @property
    @deprecated(version='1.2.0',
                reason='Only bracket browse should be use')
    def children(self) -> List[DrbNode]:
        if self._child is None:
            url = self._res['location']
            node = DrbHttpNode(url)

            self._child = resolver.create(node)

        return [self._child]


class DataSetERA5(Enum):
    ERA5_LAND = (
        'reanalysis-era5-land',
        list_predefined_variables_era5_land,
        None,
        Era5PredicateEra5Land)
    ERA5_LAND_MONTHLY = (
        'reanalysis-era5-land-monthly-means',
        list_predefined_variables_era5_land,
        list_product_type_land_monthly,
        Era5PredicateEra5LandMonthly)
    ERA5_REANALYSIS_SINGLE_LEVELS = (
        'reanalysis-era5-single-levels',
        list_predefined_variables_era5_singles_levels,
        list_product_type_hourly,
        Era5PredicateEra5SingleLevelsByHour)
    ERA5_REANALYSIS_SINGLE_LEVELS_MONTHLY = (
        'reanalysis-era5-single-levels-monthly-means',
        list_predefined_variables_era5_singles_levels,
        list_product_type_monthly,
        Era5PredicateEra5SingleLevelsByMonth)
    ERA5_REANALYSIS_PRESSURE_LEVELS = (
        'reanalysis-era5-pressure-levels',
        list_predefined_variables_era5_pressure,
        list_product_type_hourly,
        Era5PredicateEra5PressureLevelByHour)
    ERA5_REANALYSIS_PRESSURE_LEVELS_MONTHLY = (
        'reanalysis-era5-pressure-levels-monthly-means',
        list_predefined_variables_era5_pressure,
        list_product_type_monthly,
        Era5PredicateEra5PressureLevelsByMonth)

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._name = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, children: list = None, list_product_type=None,
                 predicate_class=None):
        self._children = children
        self._list_product_type = list_product_type
        self._predicate_class = predicate_class

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> list:
        return self._children

    @property
    def list_product_type(self):
        return self._list_product_type

    @property
    def predicate_class(self):
        return self._predicate_class


class Era5Factory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, Era5ServiceNodeCommon):
            return node
        if isinstance(node, DrbHttpNode):
            node_era5_service = Era5ServiceNode(
                url=node.path.original_path,
                auth=node.auth)
        else:
            node_era5_service = Era5ServiceNode(node.path.name)
        try:
            node_era5_service.children
        except Exception:
            final_url = node.path.name.replace('+era5', '')
            raise DrbFactoryException(f'Unsupported Era5 service: {final_url}')
        return node_era5_service
