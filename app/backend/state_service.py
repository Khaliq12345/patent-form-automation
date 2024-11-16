import httpx


async def get_states(country_code: str) -> dict:
    print('Getting the states')
    states = {}
    if country_code:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://patentcenter.uspto.gov/filing/public/v1/references/{country_code}/regions"
                )
                if response.status_code == 200:
                    json_data = response.json()
                    for x in json_data:
                        states[x["ictValueText"]] = x["descriptionText"]
            return states
        except Exception as e:
            print(f"Error: {e}")
            return {}
    else:
        return states
