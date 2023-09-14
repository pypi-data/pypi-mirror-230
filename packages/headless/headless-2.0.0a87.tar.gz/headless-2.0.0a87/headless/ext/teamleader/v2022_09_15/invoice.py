# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import date

from httpx import AsyncClient

from ..resource import TeamleaderResource


class Invoice(TeamleaderResource):
    id: str
    invoice_number: str | None = None
    invoice_date: date | None = None

    @classmethod
    def get_retrieve_url(cls, resource_id: int | str | None) -> str:
        return f'{cls._meta.base_endpoint}.info'

    async def download(self, fmt: str = 'pdf') -> bytes:
        """Download the invoice and return a byte-sequence holding the data."""
        response = await self._client.post(
            url=f'{self._meta.base_endpoint}.download',
            params={'id': self.id, 'format': fmt}
        )
        response.raise_for_status()
        dto = await response.json()
        async with AsyncClient() as client:
            response = await client.get(url=dto['data']['location'])
            response.raise_for_status()
        return response.content

    class Meta(TeamleaderResource.Meta):
        base_endpoint: str = '/invoices'