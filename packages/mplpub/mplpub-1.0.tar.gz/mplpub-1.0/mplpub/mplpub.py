import os
from ast import literal_eval
from collections import OrderedDict

import matplotlib
from matplotlib import rcParams


def read_template(template_file):
    """ Returns a matploblib rc configurations dict created from
    template_file which should consist lines having the format::

        key1 = value1
        key2 = value2
        ...

    where whitespaces are ignored and everything following
    a ``#`` is a comment. The values can be numbers, strings,
    lists or dictionaries.
    """
    template = {}
    with open(template_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            elif line == '':
                continue
            else:
                line_split = line.split('=')
                key = line_split[0].strip()
                value = line_split[1]
                if '#' in value:
                    value = value[: value.index('#')]
                value = value.strip()
                value = literal_eval(value)
                template[key] = value
    return template


# ---------------------------------------------------
# Color sets
# ---------------------------------------------------
# Standard tableau 20 set
tableau = OrderedDict(
    [
        ('blue', '#1F77B4'),
        ('orange', '#FF7F0E'),
        ('green', '#2CA02C'),
        ('red', '#D62728'),
        ('purple', '#9467BD'),
        ('brown', '#8C564B'),
        ('pink', '#E377C2'),
        ('grey', '#7F7F7F'),
        ('yellow', '#BCBD22'),
        ('turquoise', '#17BECF'),
        ('lightblue', '#AEC7E8'),
        ('lightorange', '#FFBB78'),
        ('lightgreen', '#98DF8A'),
        ('lightred', '#FF9896'),
        ('lightpurple', '#C5B0D5'),
        ('lightbrown', '#C49C94'),
        ('lightpink', '#F7B6D2'),
        ('lightgrey', '#C7C7C7'),
        ('lightyellow', '#DBDB8D'),
        ('lightturquoise', '#9EDAE5'),
    ]
)


# ---------------------------------------------------
def setup(
    tex: bool = True,
    template: str = None,
    width: float = None,
    height: float = None,
    font_family: str = 'sans-serif',
    color_cycle=tableau.values(),
    extra_settings: dict = None,
):

    """Set up publication quality plotting by changing the ``rcparams``
    dictionary and various other options.

    Parameters
    ----------
    tex
        use external (system) TeX-engine
    template
        name of template
    width
        width of the figure in inches
    height
        height of the figure in inches
    font_family
        font family (e.g., ``'sans-serif'``)
    extra_settings
        extra parameters that are used to update the ``rcParams`` dictionary
    """

    # ------------------------------------
    # load settings from templates, start with base
    dir_module = os.path.dirname(os.path.realpath(__file__))
    dir_templates = os.path.join(dir_module, 'templates')

    template_base = read_template(os.path.join(dir_templates, 'base'))
    if int(matplotlib.__version__[0]) >= 2:  # settings for version >= 2.0
        template_base.update(
            read_template(os.path.join(dir_templates, 'base_2.0_update'))
        )
    rcParams.update(template_base)

    # overload with journal specific template
    if template:
        new_template = read_template(os.path.join(dir_templates, template))
        rcParams.update(new_template)

    # ------------------------------------
    # set font properties
    rcParams['font.family'] = font_family
    if tex:
        rcParams['text.usetex'] = True
        preamble_list = [r'\usepackage{amsmath}']
        if font_family == 'sans-serif':
            preamble_list += [
                r'\usepackage{helvet}',  # use helvetica sans font
                r'\usepackage{sansmath}',  # also use for math
                r'\sansmath',
                # Dirty hack to get uppercase greek letters:
                r"""\newcommand{
                 \UG}[1]{\text{\unsansmath\ensuremath{#1}\sansmath}}"""
                r"""\newcommand{
                 \angs}{\text{\normalfont\AA}}""",
            ]

            # in older versions of matplotlib the preamble must be a list of strings
            def versiontuple(v):
                return tuple(map(int, (v.split('.'))))

            if versiontuple(matplotlib.__version__) < versiontuple('3.1'):
                rcParams['text.latex.preamble'] = preamble_list
            else:
                rcParams['text.latex.preamble'] = '\n'.join(preamble_list)
    else:  # choose fonts if we are not using tex
        rcParams['font.sans-serif'] = 'Liberation Sans'
        rcParams['font.serif'] = 'Palatino'

    # ------------------------------------
    # other properties
    # set custom size
    if width or height:
        if not width:
            size = (rcParams['figure.figsize'][0], height)
        elif not height:
            size = (width, rcParams['figure.figsize'][1])
        else:
            size = (width, height)
        rcParams['figure.figsize'] = size

    # set color cycle to tableau, note that the cycler is not available
    # in older versions of matplotlib so we have to try it
    try:
        from matplotlib import cycler

        rcParams['axes.prop_cycle'] = cycler(color=color_cycle)
    except Exception:
        print('Note: color cycler is not supported by this version of matplotlib.')

    # update dict with extra parameters
    if extra_settings:
        rcParams.update(extra_settings)
