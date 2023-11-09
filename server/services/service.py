import models
from cruds.user import UserCRUD
from schemas.service import (
    MasterRepairEdit,
    RepairTypeIn,
    RepairTypeEdit,
    MasterRepair,
)
from utils.app_exceptions import AppException
from cruds.service import ServiceCRUD
from services.main import AppService
from utils.service_result import ServiceResult, handle_result


class ServiceTypeService(AppService):
    def get_service_type(self, id: int) -> ServiceResult:
        service_type = ServiceCRUD(self.db).get_service_type(id)
        return ServiceResult(service_type)

    def get_service_types(self) -> ServiceResult:
        types = ServiceCRUD(self.db).get_service_types()
        return ServiceResult(types)

    def get_service_types_by_category(self, category_id: int):
        types = ServiceCRUD(self.db).get_service_types_by_category(category_id)
        return ServiceResult(types)


class DeviceService(AppService):
    def get_device(self, id: int) -> ServiceResult:
        device = ServiceCRUD(self.db).get_device(id)
        if not device:
            return ServiceResult(
                AppException.NotFoundException(detail="Устройство не найдено!")
            )
        return ServiceResult(device)

    def get_devices(self) -> ServiceResult:
        devices = ServiceCRUD(self.db).get_devices()
        return ServiceResult(devices)

    def get_devices_by_service_type(self, id: int) -> ServiceResult:
        devices = ServiceCRUD(self.db).get_devices_by_service_type(id)
        return ServiceResult(devices)


class CategoryService(AppService):
    def get_category(self, id: int) -> ServiceResult:
        category = ServiceCRUD(self.db).get_category(id)
        if not category:
            return ServiceResult(
                AppException.NotFoundException(detail="Категория не найдена!")
            )
        return ServiceResult(category)

    def get_categories(self) -> ServiceResult:
        categories = ServiceCRUD(self.db).get_categories()
        return ServiceResult(categories)


class RepairTypeService(AppService):
    def create_repair_type(
        self, data: RepairTypeIn, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        new_repair_type = ServiceCRUD(self.db).create_repair_type(data, master)
        return ServiceResult(new_repair_type)

    def get_repair_type(self, id: int) -> ServiceResult:
        repair_type = ServiceCRUD(self.db).get_repair_type(id)
        if not repair_type:
            return ServiceResult(
                AppException.NotFoundException(detail="Вид ремонта не найден!")
            )
        return ServiceResult(repair_type)

    def get_repair_types(self) -> ServiceResult:
        repair_types = ServiceCRUD(self.db).get_repair_types()
        return ServiceResult(repair_types)

    def get_repair_types_by_device(self, id: int) -> ServiceResult:
        repair_types = ServiceCRUD(self.db).get_repair_types_by_device(id)
        return ServiceResult(repair_types)

    def patch_repair_type(
        self, id: int, data: RepairTypeEdit, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        new_repair_type = ServiceCRUD(self.db).update_repair_type(id, data, master)
        return ServiceResult(new_repair_type)

    def patch_master_repair(
        self, repair_id: int, data: MasterRepairEdit, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        master_repair = ServiceCRUD(self.db).update_master_repair(
            repair_id, data, master
        )
        if not master_repair:
            return ServiceResult(AppException.NotFoundException("Not found!"))
        return ServiceResult(master_repair)

    def get_master_repairs(self, master_username: str):
        master_repairs = ServiceCRUD(self.db).get_all_master_repairs()
        new_master_repairs = list()
        for master_repair in master_repairs:
            pydantic_model = MasterRepair(**master_repair.__dict__)
            repair_type = handle_result(self.get_repair_type(master_repair.repair_id))
            if master_username:
                if repair_type.is_custom and repair_type.created_by != master_username:
                    continue
            if (
                master_repair.master_id != master_username
                and master_username is not None
            ):
                continue
            device = handle_result(
                DeviceService(self.db).get_device(repair_type.device_id)
            )
            pydantic_model.device = device.name
            pydantic_model.device_id = device.id
            pydantic_model.repair_name = repair_type.name
            pydantic_model.repair_description = repair_type.description
            pydantic_model.is_custom = repair_type.is_custom
            new_master_repairs.append(pydantic_model)
        return ServiceResult(new_master_repairs)

    def get_master_services(self, username: str):
        master_services = ServiceCRUD(self.db).get_all_master_services(username)
        return ServiceResult(master_services)

    def delete_master_repair(
        self, repair_id: int, user: models.user.Client
    ) -> ServiceResult:
        master = UserCRUD(self.db).get_master_by_client(user)
        response = ServiceCRUD(self.db).delete_master_repair_by_repair_id(
            repair_id, master
        )
        return ServiceResult(response)

    def get_all_services(self) -> ServiceResult:
        categories = ServiceCRUD(self.db).get_categories()
        service_types = ServiceCRUD(self.db).get_service_types()
        devices = ServiceCRUD(self.db).get_devices()
        repair_types = ServiceCRUD(self.db).get_repair_types()
        all_services = {
            "categories": categories,
            "service_types": service_types,
            "devices": devices,
            "repair_types": repair_types,
        }
        return ServiceResult(all_services)
