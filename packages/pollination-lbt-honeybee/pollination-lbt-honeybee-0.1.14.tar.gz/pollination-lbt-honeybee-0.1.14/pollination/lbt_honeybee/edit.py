from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class ModelModifiersFromConstructions(Function):
    """Assign honeybee Radiance modifiers based on energy construction properties.

    This includes matching properties for reflectance, absorptance and transmission.
    Furthermore, any dynamic window constructions can be translated to dynamic
    Radiance groups and shade transmittance schedules will be translated to
    dynamic shade groups.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    use_visible = Inputs.str(
        description='A switch to indicate whether the assigned radiance modifiers '
        'should follow the solar properties of the constructions or the visible '
        'properties.', default='solar',
        spec={'type': 'string', 'enum': ['solar', 'visible']}
    )

    dynamic_behavior = Inputs.str(
        description='A switch to note whether dynamic window constructions and '
        'window constructions with blinds/shades should be translated to dynamic '
        'aperture groups or just the static (bare) construction should be used.',
        default='dynamic',
        spec={'type': 'string', 'enum': ['dynamic', 'static']}
    )

    dynamic_shade = Inputs.str(
        description='A switch to note whether dynamic shade transmittance schedules '
        'should be translated to dynamic shade groups or just a static, fully-opaque '
        'construction should be used.',
        default='dynamic',
        spec={'type': 'string', 'enum': ['dynamic', 'static']}
    )

    exterior_offset = Inputs.float(
        description='A number for the distance at which the exterior Room faces should '
        'be offset in meters. This is used to account for the fact that the exterior '
        'material layer of the construction usually needs a different modifier '
        'from the interior. If set to 0, no offset will occur and all assigned '
        'modifiers will be interior.', default=0
    )

    @command
    def model_modifiers_from_constructions(self):
        return 'honeybee-energy edit modifiers-from-constructions model.hbjson ' \
            '--{{self.use_visible}} --{{self.dynamic_behavior}}-groups ' \
            '--{{self.dynamic_shade}}-groups ' \
            '--exterior-offset {{self.exterior_offset}} --output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its Radiance modifiers assigned based on its '
        'energy constructions.', path='new_model.hbjson'
    )
