import os

ARCH_REPO = 'git@github.com:EneasJr-Rodrigues/archetype-core-nlp.git'
CORE_REPO = 'git@github.com:EneasJr-Rodrigues/archetype-core-nlp.git'
CORE_TEXT_REPO = 'git@github.com:EneasJr-Rodrigues/archetype-core-nlp.git'
CORE_IMAGE_REPO = 'git@github.com:EneasJr-Rodrigues/archetype-core-nlp.git'
CORE_SPEECH_REPO = 'git@github.com:EneasJr-Rodrigues/archetype-core-nlp.git'

DEPS = (
    ('arch_lakehouse_core', ARCH_REPO, 'CORE_VERSION'),
    ('arch_lakehouse_text', CORE_TEXT_REPO, 'CORE_TEXT_VERSION'),
    ('arch_lakehouse_image', CORE_IMAGE_REPO, 'CORE_IMAGE_VERSION'),
    ('arch_lakehouse_speech', CORE_SPEECH_REPO, 'CORE_SPEECH_VERSION'),    
)

LOGGING_FORMAT = '%(message)s'

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

ARTIFACTS = ('notebooks', 'jobs')
