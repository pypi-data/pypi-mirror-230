from pollination_dsl.dag import Inputs, DAG, task, Outputs
from dataclasses import dataclass
from pollination.honeybee_radiance.grid import MergeFolderData
from pollination.honeybee_radiance.coefficient import DaylightCoefficient

# input/output alias
from pollination.alias.inputs.model import hbjson_model_grid_input
from pollination.alias.inputs.wea import wea_input
from pollination.alias.inputs.north import north_input
from pollination.alias.inputs.radiancepar import rad_par_annual_input
from pollination.alias.inputs.grid import grid_filter_input, \
    min_sensor_count_input, cpu_count
from pollination.alias.outputs.daylight import annual_daylight_results

from ._prepare_folder import SkyIrradiancePrepareFolder


@dataclass
class SkyIrradianceEntryPoint(DAG):
    """Annual Sky Radiation entry point."""

    # inputs
    north = Inputs.float(
        default=0,
        description='A number for rotation from north.',
        spec={'type': 'number', 'minimum': -360, 'maximum': 360},
        alias=north_input
    )

    cpu_count = Inputs.int(
        default=50,
        description='The maximum number of CPUs for parallel execution. This will be '
        'used to determine the number of sensors run by each worker.',
        spec={'type': 'integer', 'minimum': 1},
        alias=cpu_count
    )

    min_sensor_count = Inputs.int(
        description='The minimum number of sensors in each sensor grid after '
        'redistributing the sensors based on cpu_count. This value takes '
        'precedence over the cpu_count and can be used to ensure that '
        'the parallelization does not result in generating unnecessarily small '
        'sensor grids. The default value is set to 1, which means that the '
        'cpu_count is always respected.', default=500,
        spec={'type': 'integer', 'minimum': 1},
        alias=min_sensor_count_input
    )

    radiance_parameters = Inputs.str(
        description='Radiance parameters for ray tracing.',
        default='-ab 2 -ad 5000 -lw 2e-05 -dr 0',
        alias=rad_par_annual_input
    )

    grid_filter = Inputs.str(
        description='Text for a grid identifier or a pattern to filter the sensor grids '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the sensor grids that have an identifier that starts with '
        'first_floor_. By default, all grids in the model will be simulated.',
        default='*',
        alias=grid_filter_input
    )

    sky_density = Inputs.int(
        default=1,
        description='The density of generated sky. This input corresponds to gendaymtx '
        '-m option. -m 1 generates 146 patch starting with 0 for the ground and '
        'continuing to 145 for the zenith. Increasing the -m parameter yields a higher '
        'resolution sky using the Reinhart patch subdivision. For example, setting -m 4 '
        'yields a sky with 2305 patches plus one patch for the ground.',
        spec={'type': 'integer', 'minimum': 1}
    )

    cumulative = Inputs.str(
        description='An option to generate a cumulative sky instead of an hourly sky',
        default='hourly', spec={'type': 'string', 'enum': ['hourly', 'cumulative']}
    )

    order_by = Inputs.str(
        description='Order of the output results. By default the results are ordered '
        'to include the results for a single sensor in each row.', default='sensor',
        spec={'type': 'string', 'enum': ['sensor', 'datetime']}
    )

    model = Inputs.file(
        description='A Honeybee model in HBJSON file format.',
        extensions=['json', 'hbjson'],
        alias=hbjson_model_grid_input
    )

    wea = Inputs.file(
        description='Wea file.', extensions=['wea'], alias=wea_input
    )

    timestep = Inputs.int(
        description='Input wea timestep. This value will be used to divide the '
        'cumulative results.', default=1,
        spec={'type': 'integer', 'minimum': 1, 'maximum': 60}
    )

    leap_year = Inputs.str(
        description='A flag to indicate if datetimes in the wea file are for a leap '
        'year.', default='full-year',
        spec={'type': 'string', 'enum': ['full-year', 'leap-year']}
    )

    black_out = Inputs.str(
        default='default',
        description='A value to indicate if the black material should be used for . '
        'the calculation. Valid values are default and black. Default value is default.',
        spec={'type': 'string', 'enum': ['black', 'default']}
    )

    @task(template=SkyIrradiancePrepareFolder)
    def prepare_folder_sky_irradiance(
        self, north=north, cpu_count=cpu_count, min_sensor_count=min_sensor_count,
        grid_filter=grid_filter, sky_density=sky_density, cumulative=cumulative,
        model=model, wea=wea, timestep=timestep, leap_year=leap_year,
        black_out=black_out
    ):
        return [
            {
                'from': SkyIrradiancePrepareFolder()._outputs.model_folder,
                'to': 'model'
            },
            {
                'from': SkyIrradiancePrepareFolder()._outputs.resources,
                'to': 'resources'
            },
            {
                'from': SkyIrradiancePrepareFolder()._outputs.results,
                'to': 'results'
            },
            {
                'from': SkyIrradiancePrepareFolder()._outputs.initial_results,
                'to': 'initial_results'
            },
            {
                'from': SkyIrradiancePrepareFolder()._outputs.sensor_grids
            }
        ]

    @task(
        template=DaylightCoefficient,
        needs=[prepare_folder_sky_irradiance],
        loop=prepare_folder_sky_irradiance._outputs.sensor_grids,
        sub_folder='initial_results/{{item.full_id}}',  # create a subfolder for each grid
        sub_paths={
            'scene_file': 'scene.oct',
            'sensor_grid': 'grid/{{item.full_id}}.pts',
            'sky_dome': 'sky.dome',
            'sky_matrix': 'sky.mtx'
            }
    )
    def sky_irradiance_raytracing(
        self,
        radiance_parameters=radiance_parameters,
        scene_file=prepare_folder_sky_irradiance._outputs.resources,
        sky_dome=prepare_folder_sky_irradiance._outputs.resources,
        sky_matrix=prepare_folder_sky_irradiance._outputs.resources,
        sensor_grid=prepare_folder_sky_irradiance._outputs.resources,
        sensor_count='{{item.count}}',
        conversion='0.265 0.670 0.065',
        output_format='a',
        order_by=order_by
    ):
        return [
            {
                'from': DaylightCoefficient()._outputs.result_file,
                'to': '../{{item.full_id}}.ill'
            }
        ]

    @task(
        template=MergeFolderData,
        needs=[sky_irradiance_raytracing]
    )
    def restructure_results(
        self, input_folder='initial_results', extension='ill'
    ):
        return [
            {
                'from': MergeFolderData()._outputs.output_folder,
                'to': 'results'
            }
        ]

    results = Outputs.folder(
        description='Total radiation results.',
        source='results',
        alias=annual_daylight_results
    )
