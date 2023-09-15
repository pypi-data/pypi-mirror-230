"""Raytracing DAG for annual sky radiation."""
from pollination_dsl.dag import Inputs, DAG, task
from dataclasses import dataclass

from pollination.honeybee_radiance.coefficient import DaylightCoefficient


@dataclass
class SkyIrradianceRayTracing(DAG):
    # inputs
    name = Inputs.str(
        description='Sensor grid file name. This is useful to rename the final result '
        'file to {name}.res'
    )

    radiance_parameters = Inputs.str(
        description='The radiance parameters for ray tracing',
        default='-ab 2 -ad 5000 -lw 2e-05'
    )

    scene_file = Inputs.file(
        description='A Radiance octree file without suns or sky.',
        extensions=['oct']
    )

    sensor_grid = Inputs.file(
        description='Sensor grid file.',
        extensions=['pts']
    )

    sensor_count = Inputs.int(
        description='Number of sensors in the input sensor grid.'
    )

    sky_matrix = Inputs.file(
        description='Path to skymtx file.'
    )

    sky_dome = Inputs.file(
        description='Path to sky dome file.'
    )

    order_by = Inputs.str(
        description='Order of the output results. By default the results are ordered '
        'to include the results for a single sensor in each row.', default='sensor',
        spec={'type': 'string', 'enum': ['sensor', 'datetime']}
    )

    # TODO: add a step to set divide_by to 1/timestep if sky is cumulative.
    @task(template=DaylightCoefficient)
    def total_sky(
        self,
        name=name,
        radiance_parameters=radiance_parameters,
        fixed_radiance_parameters='-aa 0.0 -I -c 1',
        sensor_count=sensor_count,
        sky_matrix=sky_matrix,
        sky_dome=sky_dome,
        sensor_grid=sensor_grid,
        conversion='0.265 0.670 0.065',  # divide by 179
        scene_file=scene_file,
        output_format='a',
        order_by=order_by
            ):
        return [
            {
                'from': DaylightCoefficient()._outputs.result_file,
                'to': '../final/{{self.name}}.ill'
            }
        ]
