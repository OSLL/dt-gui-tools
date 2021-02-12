from forms.show_selialize import SerializeForm
import yaml


def serialize(layer):
    SerializeForm(yaml.safe_dump(dict(layer)['data'], default_flow_style=None)).exec_()
