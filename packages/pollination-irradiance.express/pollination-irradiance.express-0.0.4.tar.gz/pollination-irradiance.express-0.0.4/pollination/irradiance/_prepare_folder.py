"""Prepare folder DAG."""
from pollination_dsl.dag import Inputs, GroupedDAG, task, Outputs
from dataclasses import dataclass
from pollination.honeybee_radiance.translate import CreateRadianceFolderGrid
from pollination.honeybee_radiance.grid import SplitGridFolder
from pollination.honeybee_radiance.octree import CreateOctree
from pollination.honeybee_radiance.sky import CreateSkyDome, CreateSkyMatrix
from pollination.honeybee_radiance.sun import CreateSunMatrix, ParseSunUpHours
from pollination.path.copy import Copy

# input/output alias
from pollination.alias.inputs.model import hbjson_model_grid_input
from pollination.alias.inputs.wea import wea_input
from pollination.alias.inputs.north import north_input
from pollination.alias.inputs.grid import grid_filter_input, \
    min_sensor_count_input, cpu_count


@dataclass
class SkyIrradiancePrepareFolder(GroupedDAG):
    """Prepare folder for sky irradiance."""

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

    @task(template=CreateRadianceFolderGrid, annotations={'main_task': True})
    def create_rad_folder(self, input_model=model, grid_filter=grid_filter):
        """Translate the input model to a radiance folder."""
        return [
            {
                'from': CreateRadianceFolderGrid()._outputs.model_folder,
                'to': 'model'},
            {
                'from': CreateRadianceFolderGrid()._outputs.sensor_grids_file,
                'to': 'results/grids_info.json'
            }
        ]

    @task(template=CreateSunMatrix)
    def generate_sunpath(self, north=north, wea=wea, output_type=1):
        """Create sunpath for sun-up-hours.

        The sunpath is not used to calculate radiation values.
        """
        return [
            {
                'from': CreateSunMatrix()._outputs.sunpath,
                'to': 'resources/sunpath.mtx'
            },
            {
                'from': CreateSunMatrix()._outputs.sun_modifiers,
                'to': 'resources/suns.mod'
            }
        ]

    @task(template=ParseSunUpHours, needs=[generate_sunpath])
    def parse_sun_up_hours(
        self, sun_modifiers=generate_sunpath._outputs.sun_modifiers, leap_year=leap_year,
        timestep=timestep
            ):
        return [
            {
                'from': ParseSunUpHours()._outputs.sun_up_hours,
                'to': 'results/sun-up-hours.txt'
            }
        ]

    @task(template=CreateOctree, needs=[create_rad_folder])
    def create_octree(
        self, model=create_rad_folder._outputs.model_folder, black_out=black_out
            ):
        """Create octree from radiance folder."""
        return [
            {
                'from': CreateOctree()._outputs.scene_file,
                'to': 'resources/scene.oct'
            }
        ]

    @task(
        template=SplitGridFolder, needs=[create_rad_folder],
        sub_paths={'input_folder': 'grid'}
    )
    def split_grid_folder(
        self, input_folder=create_rad_folder._outputs.model_folder,
        cpu_count=cpu_count, cpus_per_grid=1, min_sensor_count=min_sensor_count
    ):
        """Split sensor grid folder based on the number of CPUs"""
        return [
            {
                'from': SplitGridFolder()._outputs.output_folder,
                'to': 'resources/grid'
            },
            {
                'from': SplitGridFolder()._outputs.dist_info,
                'to': 'initial_results/final/_redist_info.json'
            }
        ]

    @task(template=CreateSkyDome)
    def create_sky_dome(self, sky_density=sky_density):
        """Create sky dome for daylight coefficient studies."""
        return [
            {
                'from': CreateSkyDome()._outputs.sky_dome,
                'to': 'resources/sky.dome'
            }
        ]

    @task(template=CreateSkyMatrix)
    def create_sky(
        self, north=north, wea=wea, sky_type='total', output_type='solar',
        output_format='ASCII', sky_density=sky_density, cumulative=cumulative,
        sun_up_hours='sun-up-hours'
    ):
        return [
            {
                'from': CreateSkyMatrix()._outputs.sky_matrix,
                'to': 'resources/sky.mtx'
            }
        ]

    model_folder = Outputs.folder(
        source='model', description='input model folder folder.'
    )

    resources = Outputs.folder(
        source='resources', description='resources folder.'
    )

    results = Outputs.folder(
        source='results', description='results folder.'
    )

    initial_results = Outputs.folder(
        source='initial_results', description='initial results folder.'
    )

    sensor_grids = Outputs.list(source='resources/grid/_info.json')
