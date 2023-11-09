from typing import List

from models import Master
from models.relationship import MasterRepair
from models.service import ServiceType, Device, ServiceCategory, RepairType
from schemas.service import MasterRepairEdit, RepairTypeIn, RepairTypeEdit
from services.main import AppCRUD
from utils.app_exceptions import AppException


class ServiceCRUD(AppCRUD):
    def get_service_type(self, id: int) -> ServiceType | Exception:
        service_type = self.db.query(ServiceType).filter(ServiceType.id == id).first()
        if service_type is None:
            return AppException.NotFoundException(detail="Услуга не найдена!")
        return service_type

    def get_service_types(self) -> List[ServiceType]:
        types = self.db.query(ServiceType).all()
        return list(types) if len(types) else []

    def get_service_types_by_category(self, id: int) -> List[ServiceType]:
        types = self.db.query(ServiceType).filter(ServiceType.category_id == id).all()
        return list(types) if len(types) else []

    def get_device(self, id: int) -> Device:
        device = self.db.query(Device).filter(Device.id == id).first()
        return device

    def get_devices(self) -> List[Device]:
        devices = self.db.query(Device).all()
        return list(devices) if len(devices) else []

    def get_devices_by_service_type(self, id: int) -> List[Device]:
        devices = self.db.query(Device).filter(Device.service_id == id).all()
        return list(devices) if len(devices) else []

    def get_category(self, id: int) -> ServiceCategory:
        category = (
            self.db.query(ServiceCategory).filter(ServiceCategory.id == id).first()
        )
        return category

    def get_categories(self) -> List[ServiceCategory]:
        categories = self.db.query(ServiceCategory).all()
        return list(categories) if len(categories) else []

    def create_repair_type(
        self, data: RepairTypeIn, master: Master
    ) -> RepairType | Exception:
        new_repair_type = RepairType(
            name=data.name,
            description=data.description,
            price=data.price,
            device_id=data.device_id,
            is_custom=True,
            created_by=master.username,
        )
        self.db.add(new_repair_type)
        self.db.commit()
        self.db.refresh(new_repair_type)
        new_master_repair = MasterRepair(
            master_id=master.username,
            address_latitude=master.address_latitude,
            address_longitude=master.address_longitude,
            repair_id=new_repair_type.id,
            price=data.price,
            time=data.time,
        )
        self.db.add(new_master_repair)
        self.db.commit()
        return new_repair_type

    def get_repair_type(self, id: int) -> RepairType:
        repair_type = self.db.query(RepairType).filter(RepairType.id == id).first()
        return repair_type

    def get_repair_types(self) -> List[RepairType]:
        repair_types = self.db.query(RepairType).all()
        return list(repair_types) if len(repair_types) else []

    def get_repair_types_by_device(self, id: int) -> List[RepairType] | Exception:
        repair_types = (
            self.db.query(RepairType).filter(RepairType.device_id == id).all()
        )
        return list(repair_types) if len(repair_types) else []

    def update_repair_type(
        self, id: int, data: RepairTypeEdit, master: Master
    ) -> RepairType | Exception:
        repair_type = self.db.query(RepairType).filter(RepairType.id == id).first()
        if not repair_type:
            return AppException.NotFoundException("Вид ремонта не найден!")
        if not repair_type.is_custom:
            return AppException.ForbiddenException("Этот вид ремонта нельзя изменить!")
        if repair_type.created_by != master.username:
            return AppException.ForbiddenException("Нет доступа!")

        for attr in data.model_dump(mode="python", exclude_unset=True):
            if hasattr(repair_type, attr):
                setattr(repair_type, attr, data.__getattribute__(attr))
        self.db.commit()
        self.db.refresh(repair_type)
        self.update_master_repair(
            repair_type.id,
            MasterRepairEdit(**data.model_dump(exclude_unset=True)),
            master,
        )
        return repair_type

    def update_master_repair(
        self, repair_id: int, data: MasterRepairEdit, master: Master
    ) -> MasterRepair:
        master_repair = (
            self.db.query(MasterRepair)
            .filter(
                MasterRepair.repair_id == repair_id,
                MasterRepair.master_id == master.username,
            )
            .first()
        )
        if not master_repair:
            new_master_repair = MasterRepair(
                master_id=master.username,
                repair_id=repair_id,
                price=data.price,
                time=data.time,
                address_longitude=master.address_longitude,
                address_latitude=master.address_latitude,
            )
            self.db.add(new_master_repair)
            self.db.commit()
            self.db.refresh(new_master_repair)
            return new_master_repair
        for attr in data.model_dump(exclude_unset=True):
            if hasattr(master_repair, attr):
                setattr(master_repair, attr, data.__getattribute__(attr))
        self.db.commit()
        self.db.refresh(master_repair)
        return master_repair

    def get_all_master_repairs(self) -> List[MasterRepair]:
        master_repairs = self.db.query(MasterRepair).all()
        master_usernames = set()
        new_master_repairs = list()
        for master_repair in master_repairs:
            if master_repair.master_id in master_usernames:
                continue
            master = (
                self.db.query(Master)
                .filter(Master.username == master_repair.master_id)
                .first()
            )
            if not master:
                continue
            if not master.is_active:
                master_usernames.add(master.username)
            else:
                new_master_repairs.append(master_repair)
        return list(new_master_repairs)

    def get_all_master_services(self, username: str) -> dict:
        master_repairs = (
            self.db.query(MasterRepair).filter(MasterRepair.master_id == username).all()
        )
        response = dict()
        devices = set()
        repairs = set()
        services = set()
        response["service_types"] = list()
        response["devices"] = list()
        response["repair_types"] = list()
        for master_repair in master_repairs:
            if master_repair in repairs:
                continue
            repair = (
                self.db.query(RepairType)
                .filter(RepairType.id == master_repair.repair_id)
                .first()
            )
            response["repair_types"].append(repair)
            repairs.add(repair.id)
            if repair.device_id in devices:
                continue
            device = self.db.query(Device).filter(Device.id == repair.device_id).first()
            response["devices"].append(device)
            devices.add(device.id)
            if device.service_id in services:
                continue
            service = (
                self.db.query(ServiceType)
                .filter(ServiceType.id == device.service_id)
                .first()
            )
            response["service_types"].append(service)
            services.add(service.id)
        return response

    def delete_master_repair_by_repair_id(
        self, repair_id: int, master: Master
    ) -> dict | Exception:
        master_repair = (
            self.db.query(MasterRepair)
            .filter(
                MasterRepair.repair_id == repair_id,
                MasterRepair.master_id == master.username,
            )
            .first()
        )
        if not master_repair:
            return AppException.NotFoundException(
                "Связь между мастером и видом ремонта не найдена!"
            )
        self.db.delete(master_repair)
        self.db.commit()
        return {"result": "Success!"}
