from outline_vpn import OutlineVPN

from config.loading import config


class MyClassOutlineVpn:
    async def __aenter__(self):
        self.client = OutlineVPN(api_url=config.API_URL_VPN.get_secret_value())
        await self.client.init(cert_sha256=config.CERT_SHA256_VPN.get_secret_value())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.client._close()

    async def create_new_key(self, chat_id: int) -> str:
        key = await self.client.create_key(str(chat_id))
        return key.access_url

    async def all_keys(self) -> list:
        return [key.name for key in await self.client.get_keys()]

    async def delete_key_func(self, chat_id: int) -> bool:
        for key in await self.client.get_keys():
            if key.name == str(chat_id):
                await self.client.delete_key(key.key_id)
                return True
        return False

    async def one_key_info(self, chat_id: int) -> tuple[str, str] | bool:
        for key in await self.client.get_keys():
            if key.name == str(chat_id):
                client_info = await self.client.get_key(key.key_id)
                return client_info.name, client_info.access_url
        return False
