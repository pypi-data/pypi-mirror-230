async def _get_user_photo_url(user) -> str:
    user_photos = await user.get_profile_photos()
    if user_photos.photos:
        last_photo = user_photos.photos[0][-1]
        photo_url = await last_photo.get_url()
    else:
        photo_url = 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not' \
                    '-found-free-vector.jpg'
    return photo_url


async def _get_user_profile_url(user):
    if user.username:
        profile_url = f"https://t.me/{user.username}"
    else:
        profile_url = f"https://t.me/user?id={user.id}"

    return profile_url
