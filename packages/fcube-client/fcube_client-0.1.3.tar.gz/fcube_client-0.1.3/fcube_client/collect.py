import asyncio
import httpx
import time

start_time = time.time()

async def main():
    pokemon_url = 'https://pokeapi.co/api/v2/pokemon/ditto'

    async with httpx.AsyncClient() as client:

        resp = await client.get(pokemon_url)

        pokemon = resp.json()
        print(pokemon['name'])

asyncio.run(main())
