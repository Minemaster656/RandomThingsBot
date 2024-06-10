import asyncio

from factcheckexplorer.factcheckexplorer import FactCheckLib
import AIIO
async def func():
    asked = await AIIO.askBetterLLM([{"role": "user", "content": "Что такое сахар?"}])
    fact_check = FactCheckLib(query=asked["result"], language="ru", num_results=100)


    rjson = fact_check.fetch_data()
    data = fact_check.clean_json(rjson)
    result= fact_check.extract_info(data)
    print(result)

asyncio.run(func())
