.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/borasem-waste.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/borasem-waste
    .. image:: https://readthedocs.org/projects/borasem-waste/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://borasem-waste.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/borasem-waste/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/borasem-waste
    .. image:: https://img.shields.io/pypi/v/borasem-waste.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/borasem-waste/
    .. image:: https://img.shields.io/conda/vn/conda-forge/borasem-waste.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/borasem-waste
    .. image:: https://pepy.tech/badge/borasem-waste/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/borasem-waste
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/borasem-waste

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

=======================================
Borås Energi och Miljö Waste Collection
=======================================


    Simple package to get the schedule for upcoming waste pickups.




.. _pyscaffold-notes:

Example
=======

.. code-block:: language

    
    import asyncio
    import aiohttp
    from borasem_waste import auth,borasem

    valid_address = 'Validated address from async_get_address()'
    search_address = 'Any address to search on.'

    async def main():

        async with aiohttp.ClientSession() as session:
            
            authObj = auth.Auth(session)
            api = borasem.BorasEM(authObj)

            # Get Waste Schedule
            schedule = await api.async_get_schedule(valid_address)

            # Print states
            for scheduleEntry in schedule:
                print(f"The entry {scheduleEntry.containerId} is being picked up at {scheduleEntry.NextWastePickup}")

            # Get Waste Schedule
            addressList = await api.async_get_address(search_address)

            # Print states
            for address in addressList:
                print(address)

    asyncio.run(main())
