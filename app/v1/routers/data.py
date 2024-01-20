import logging
from fastapi import APIRouter, Path, HTTPException, status, Depends
from core.schemas.data import Data
from core.databases.mongo import MongoManager
from typing import List
from typing_extensions import Annotated


log = logging.getLogger()


router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)


@router.get("", response_model=List[Data])
async def read_all_data(mm: Annotated[MongoManager, Depends(MongoManager)]):
    """
    Get all data
    """

    return mm.find_all_data()


@router.get("/{name}", response_model=Data)
async def read_data(
    mm: Annotated[MongoManager, Depends(MongoManager)],
    name: str = Path(examples=["name"]),
):
    """
    Get data data, expects data name,
    returns 404 if the data is not found
    """

    data_found = mm.find_one(name)
    if data_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found"
        )

    return data_found


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Data)
async def create_data(
    mm: Annotated[MongoManager, Depends(MongoManager)],
    data: Data,
):
    """
    Create data (fail if it already exists):

    - **name**: full data name
    - **metadata**: some metadata
    """

    data_found = mm.find_one(data.name)
    if data_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data already exists"
        )

    try:
        mm.insert_one(data.model_dump())
    except Exception as e:
        log.error(f"Failed to save data to db: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Backend failed to save data"
        )

    data_created_found = mm.find_one(data.name)
    if data_created_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data was not created"
        )

    return data_created_found


@router.put("/{name}", response_model=Data)
async def update_data(
    mm: Annotated[MongoManager, Depends(MongoManager)],
    data: Data,
    name: str = Path(examples=["name"]),
):
    """
    Update data (fail if it does not exist),
    this will replace a data:

    - **name**: full data name
    - **metadata**: some metadata
    """

    data_found = mm.find_one(name)
    if data_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found"
        )

    new_name = data.name
    new_data_found = mm.find_one(new_name)
    if new_data_found and new_data_found != data_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data already exists"
        )

    try:
        mm.replace_one(name, data.model_dump())
    except Exception as e:
        log.error(f"Failed to replace data in db: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Backend failed to replace data"
        )

    data_updated_found = mm.find_one(new_name)

    return data_updated_found


@router.delete("/{name}", response_model=Data)
async def delete_data(
    mm: Annotated[MongoManager, Depends(MongoManager)],
    name: str = Path(examples=["name"]),
):
    """
    Delete data, expects full data name,
    return 404 if the data is not found
    """

    data_found = mm.find_one(name)
    if data_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found"
        )

    try:
        mm.delete_one(name)
    except Exception as e:
        log.error(f"Failed to delete data from db: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Backend failed to delete data"
        )

    data_deleted = Data(**data_found)

    return data_deleted
