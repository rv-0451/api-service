import logging
from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import ValidationError
from core.schemas.data import Data, DataQuery
from core.databases.mongo import MongoManager
from typing import List
from typing_extensions import Annotated


log = logging.getLogger()


router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
)


@router.get("", response_model=List[Data])
async def read_data(
    request: Request,
    mm: Annotated[MongoManager, Depends(MongoManager)],
):
    """
    Search for data with query
    """

    query = request.url.query
    log.info(f"search query passed to db: {query}")
    try:
        DataQuery(query=query)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is malformed"
        )

    return mm.find_data(query)
