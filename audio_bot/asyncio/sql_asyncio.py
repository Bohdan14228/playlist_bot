import aiosqlite
import asyncio


async def add_user(user) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(f"INSERT INTO users(user) VALUES (?)", (user,))
        await db.commit()


async def check_playlist(chat_id):
    async with aiosqlite.connect('playlists.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT name_genre FROM playlist "
                             f"WHERE user_id LIKE (SELECT id FROM users WHERE user LIKE ?)", (chat_id,))
        return [i for i in await cursor.fetchall()][0]


async def add_playlist(user_id, name_genre) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(
            "INSERT INTO playlist (user_id, name_genre) VALUES ((SELECT id FROM users WHERE user = ?), ?)",
            (user_id, name_genre))
        await db.commit()


async def add_track(name_playlist, name_track, id_track, user_id) -> None:
    async with aiosqlite.connect('playlists.db') as db:
        await db.execute(
            "INSERT INTO tracks (playlist_id, name_track, id_track) "
            "VALUES ((SELECT id FROM playlist WHERE user_id = (SELECT id FROM users WHERE user = ?)"
            " AND name_genre = ?), ?, ?)",
            (user_id, name_playlist, name_track, id_track))
        await db.commit()


# async def select(user, name_genre):
#     async with aiosqlite.connect('playlists.db') as db:
#         cursor = await db.cursor()
#         await cursor.execute("SELECT id FROM playlist WHERE user_id = (SELECT id FROM users WHERE user = ?) "
#                              "AND name_genre = ?", (user, name_genre))
#         return await cursor.fetchall()
#
# print(asyncio.get_event_loop().run_until_complete(select('428392590', ' Л л л')))
# print(asyncio.get_event_loop().run_until_complete(select()))
