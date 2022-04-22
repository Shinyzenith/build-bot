import os

import aiosqlite


class SqliteSingleton:
    __connection__ = None

    async def get_connection():
        if SqliteSingleton.__connection__ == None:
            SqliteSingleton.__connection__ = await aiosqlite.connect('channel_data.db')
            cursor = await SqliteSingleton.__connection__.execute("""
                                                    CREATE TABLE IF NOT EXISTS channel_data(
                                                        guild_id INTEGER PRIMARY KEY,
                                                        stable_id INTEGER,
                                                        ptb_id INTEGER,
                                                        canary_id INTEGER
                                                    )
                                                """)
            await SqliteSingleton.__connection__.commit()
            await cursor.close()
        return SqliteSingleton.__connection__

    async def close_connection():
        await SqliteSingleton.__connection__.close()
        SqliteSingleton.__connection__ = None
