from dotserve.client.cloud import dotserve_client
from fastapi import HTTPException


async def is_conversation_author(username: str, conversation_id: str):
    if not dotserve_client:
        raise HTTPException(status_code=401, detail="Unauthorized")

    conversation_author = await dotserve_client.get_conversation_author(conversation_id)

    if conversation_author != username:
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        return True
