from fastapi import APIRouter, Depends
from services.service import (
    ServiceTypeService,
    DeviceService,
    CategoryService,
    RepairTypeService,
)
from schemas.service import (
    ServiceType,
    Device,
    Category,
    RepairType,
    MasterRepair,
    MasterRepairEdit,
    AllServices,
    RepairTypeIn,
    RepairTypeEdit,
)
from utils.dependencies import get_current_user
from utils.service_result import handle_result
from config.database import get_db
from typing import List

router = APIRouter(
    prefix="/service",
    tags=["services"],
    responses={404: {"description": "Not found"}},
)


@router.get("/type/{id}", response_model=ServiceType)
async def get_service_type(id: int, db: get_db = Depends()):
    result = ServiceTypeService(db).get_service_type(id)
    return handle_result(result)


@router.get("/types/{category_id}", response_model=List[ServiceType])
async def get_service_types_by_category(category_id: int, db: get_db = Depends()):
    result = ServiceTypeService(db).get_service_types_by_category(category_id)
    return handle_result(result)


@router.get("/types", response_model=List[ServiceType])
async def get_service_types(db: get_db = Depends()):
    result = ServiceTypeService(db).get_service_types()
    return handle_result(result)


@router.get("/device/{id}", response_model=Device)
async def get_device(id: int, db: get_db = Depends()):
    result = DeviceService(db).get_device(id)
    return handle_result(result)


@router.get("/devices", response_model=List[Device])
async def get_devices(db: get_db = Depends()):
    result = DeviceService(db).get_devices()
    return handle_result(result)


@router.get("/devices/{service_type_id}", response_model=List[Device])
async def get_devices_by_service_type(service_type_id: int, db: get_db = Depends()):
    result = DeviceService(db).get_devices_by_service_type(service_type_id)
    return handle_result(result)


@router.get("/category/{id}", response_model=Category)
async def get_category(id: int, db: get_db = Depends()):
    result = CategoryService(db).get_category(id)
    return handle_result(result)


@router.get("/categories", response_model=List[Category])
async def get_categories(db: get_db = Depends()):
    result = CategoryService(db).get_categories()
    return handle_result(result)


@router.post("/repair_type", response_model=RepairType)
async def create_repair_type(
    data: RepairTypeIn, user=Depends(get_current_user), db: get_db = Depends()
):
    result = RepairTypeService(db).create_repair_type(data, user)
    return handle_result(result)


@router.get("/repair_type/{id}", response_model=RepairType)
async def get_repair_type(id: int, db: get_db = Depends()):
    result = RepairTypeService(db).get_repair_type(id)
    return handle_result(result)


@router.get("/repair_types", response_model=List[RepairType])
async def get_repair_types(db: get_db = Depends()):
    result = RepairTypeService(db).get_repair_types()
    return handle_result(result)


@router.get("/repair_types/{device_id}", response_model=List[RepairType])
async def get_repair_types_by_device(device_id: int, db: get_db = Depends()):
    result = RepairTypeService(db).get_repair_types_by_device(device_id)
    return handle_result(result)


@router.patch("/repair_type/{id}", response_model=RepairType)
async def patch_repair_type(
    id: int,
    data: RepairTypeEdit,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = RepairTypeService(db).patch_repair_type(id, data, user)
    return handle_result(result)


@router.patch("/master-repair/{repair_id}", response_model=MasterRepair)
async def patch_master_repair(
    repair_id: int,
    data: MasterRepairEdit,
    user=Depends(get_current_user),
    db: get_db = Depends(),
):
    result = RepairTypeService(db).patch_master_repair(repair_id, data, user)
    return handle_result(result)


@router.get("/master-repairs", response_model=List[MasterRepair])
async def get_master_repairs(master_username: str = None, db: get_db = Depends()):
    result = RepairTypeService(db).get_master_repairs(master_username)
    return handle_result(result)


@router.delete("/master-repair/{repair_id}")
async def delete_master_repair(
    repair_id: int, user=Depends(get_current_user), db: get_db = Depends()
):
    result = RepairTypeService(db).delete_master_repair(repair_id, user)
    return handle_result(result)


@router.get("/master-services/{master_username}", response_model=AllServices)
async def get_master_services(
    master_username: str, user=Depends(get_current_user), db: get_db = Depends()
):
    result = RepairTypeService(db).get_master_services(master_username)
    return handle_result(result)


@router.get("/services", response_model=AllServices)
async def get_all_services(db: get_db = Depends()):
    result = RepairTypeService(db).get_all_services()
    return handle_result(result)
