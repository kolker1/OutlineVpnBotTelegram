from db.models import User
from db.models import session


async def add_user(chat_id: int, username: str) -> User:
    async with session() as sess:
        user = User(chat_id=chat_id, username=username)

        if not await sess.get(User, chat_id):
            sess.add(user)
        else:
            user = await sess.merge(user)

        await sess.commit()
        await sess.refresh(user)

        return user


async def update_user(user: User) -> None:
    async with session() as sess:
        await sess.merge(user)
        await sess.commit()


async def get_user(chat_id: int) -> User:
    async with session() as sess:
        return await sess.get(User, chat_id)
