#
# Ignores AWS ACM validation CNAME records.
#

from logging import getLogger

logger = getLogger('Route53')
try:
    logger.warning(
        'octodns_route53 shimmed. Update your processor class to '
        'octodns_route53.processor.AwsAcmMangingProcessor. '
        'Shim will be removed in 1.0'
    )
    from octodns_route53.processor import AwsAcmMangingProcessor

    AwsAcmMangingProcessor  # pragma: no cover
except ModuleNotFoundError:
    logger.exception(
        'AwsAcmMangingProcessor has been moved into a separate '
        'module, octodns_route53 is now required. Processor '
        'class should be updated to '
        'octodns_route53.processor.AwsAcmMangingProcessor'
    )
    raise
