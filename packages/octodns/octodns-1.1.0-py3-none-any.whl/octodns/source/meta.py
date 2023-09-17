#
#
#

from datetime import datetime
from logging import getLogger
from uuid import uuid4

from .. import __VERSION__
from ..record import Record
from .base import BaseSource


class MetaSource(BaseSource):
    SUPPORTS_GEO = False
    SUPPORTS_DYNAMIC = False
    SUPPORTS = {'TXT'}

    def __init__(
        self,
        id,
        record_name='meta',
        include_time=True,
        include_uuid=False,
        include_version=False,
        ttl=60,
    ):
        self.log = getLogger(f'MetaSource[{id}]')
        super().__init__(id)
        self.log.info(
            '__init__: record_name=%s, include_time=%s, include_uuid=%s, include_version=%s, ttl=%d',
            record_name,
            include_time,
            include_uuid,
            include_version,
            ttl,
        )
        self.record_name = (record_name,)
        values = []
        if include_time:
            time = datetime.utcnow().isoformat()
            values.append(f'time={time}')
        if include_uuid:
            uuid = uuid4() if include_uuid else None
            values.append(f'uuid={uuid}')
        if include_version:
            values.append(f'version={__VERSION__}')
        self.values = values
        self.ttl = ttl

    def populate(self, zone, target=False, lenient=False):
        self.log.debug(
            'populate: name=%s, target=%s, lenient=%s',
            zone.name,
            target,
            lenient,
        )

        before = len(zone.records)

        if self.values:
            meta = Record.new(
                zone,
                self.record_name,
                {'type': 'TXT', 'ttl': self.ttl, 'values': self.values},
            )
            zone.add_record(meta)

        self.log.info(
            'populate:   found %s records', len(zone.records) - before
        )
