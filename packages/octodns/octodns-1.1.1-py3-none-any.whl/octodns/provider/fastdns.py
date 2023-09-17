#
#
#

from logging import getLogger

logger = getLogger('Akamai')
logger.warning(
    'AkamaiProvider has been moved into a separate module, '
    'octodns_edgedns is now required. Provider class should '
    'be updated to octodns_edgedns.AkamaiProvider. See '
    'https://github.com/octodns/octodns#updating-'
    'to-use-extracted-providers for more information.'
)
