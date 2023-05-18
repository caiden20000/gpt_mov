import aiohttp

async def get_session():
    return aiohttp.ClientSession()

# Inefficient for multiple requests, later save and reuse session
async def send_get_request(session, url, headers=None):
    async with session.get(url, headers=headers) as response:
        return await response

async def send_post_request(session, url, headers, json):
    async with session.post(url, headers=headers, json=json) as response:
        return await response