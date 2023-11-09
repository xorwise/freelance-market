from pydantic import BaseModel
from typing import Optional, List

from schemas.user import Master


class Category(BaseModel):
    id: int
    name: str


class ServiceType(BaseModel):
    id: int
    name: str
    category_id: int


class ServiceTypeInfo(BaseModel):
    name: str


class Device(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None
    service_id: int


class RepairType(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    device_id: int
    is_custom: bool
    master: Optional[Master] = None


class RepairTypeIn(BaseModel):
    name: str
    description: Optional[str]
    price: float
    device_id: int
    time: str


class RepairTypeEdit(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    time: Optional[str] = None


class MasterRepairEdit(BaseModel):
    price: Optional[float] = None
    time: Optional[str] = None


class MasterRepair(BaseModel):
    repair_id: int
    master_id: str
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    price: Optional[float] = None
    time: Optional[str] = None
    device: Optional[str] = None
    device_id: Optional[int] = None
    repair_name: Optional[str] = None
    repair_description: Optional[str] = None
    is_custom: Optional[bool] = None


class AllServices(BaseModel):
    categories: Optional[List[Category]] = None
    service_types: List[ServiceType]
    devices: List[Device]
    repair_types: List[RepairType]
