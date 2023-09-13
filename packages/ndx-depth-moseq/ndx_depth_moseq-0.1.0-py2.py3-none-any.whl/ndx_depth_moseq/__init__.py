import os
from pynwb import load_namespaces, get_class

# Set path of the namespace.yaml file to the expected install location
ndx_moseq_specpath = os.path.join(
    os.path.dirname(__file__),
    'spec',
    'ndx-depth-moseq.namespace.yaml'
)

# If the extension has not been installed yet but we are running directly from
# the git repo
if not os.path.exists(ndx_moseq_specpath):
    ndx_moseq_specpath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..',
        'spec',
        'ndx-depth-moseq.namespace.yaml'
    ))

# Load the namespace
load_namespaces(ndx_moseq_specpath)

# TODO: import your classes here or define your class using get_class to make
# them accessible at the package level
DepthImageSeries = get_class('DepthImageSeries', 'ndx-depth-moseq')
MoSeqExtractGroup = get_class('MoSeqExtractGroup', 'ndx-depth-moseq')
MoSeqExtractParameterGroup = get_class('MoSeqExtractParameterGroup', 'ndx-depth-moseq')