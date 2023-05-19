import aiohttp

global_session = None

async def init_session():
    global_session = await aiohttp.ClientSession().__aenter__()

async def get_session():
    return aiohttp.ClientSession()

# Inefficient for multiple requests, later save and reuse session
async def send_get_request(session, url, headers=None):
    # if global_session is None: return False;
    basic_response = {"json": {}, "ok": False, "text": "", "content": None}
    async with session.get(url, headers=headers) as response:
        basic_response["json"] = await response.json()
        basic_response["ok"] = response.ok
        basic_response["text"] = await response.text()
        basic_response["content"] = await response.content
    return basic_response

async def send_post_request(session, url, headers, json):
    basic_response = {"json": {}, "ok": False, "text": "", "iter_content": None}
    async with session.post(url, headers=headers, json=json) as response:
        basic_response["json"] = await response.json()
        basic_response["ok"] = response.ok
        basic_response["text"] = await response.text()
        basic_response["iter_content"] = await response.iter_content()
    return basic_response