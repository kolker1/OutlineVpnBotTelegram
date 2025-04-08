from sqlalchemy import select

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


async def get_user(chat_id: int | None = None, username: str | None = None) -> User:
    async with session() as sess:

        query = select(User)

        if chat_id:
            query = query.where(User.chat_id == chat_id)
        else:
            query = query.where(User.username == username)

        user = await sess.execute(query)
        user = user.scalar_one_or_none()

        return user
