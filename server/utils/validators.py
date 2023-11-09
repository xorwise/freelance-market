import re
import os
from starlette.datastructures import UploadFile
from config.database import get_db
from models import tables_dict
import phonenumbers


def email_validator(email: str) -> bool:
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not re.fullmatch(regex, email):
        return False
    return True


def password_validator(password1: str, password2: str = None) -> bool:
    regex = "^(?=.*?[a-z])(?=.*?[0-9]).{5,}$"
    if not re.fullmatch(regex, password1):
        return False
    if not password2:
        return True
    if password1 != password2:
        return False
    return True


async def upload_file(
    data: dict, field_name: str, table_name: str, entity_id: int, multiple: bool
):
    files = []
    if (
        type(data.get(field_name)) == tuple
        or type(data.get(field_name)) == UploadFile
        or type(data.get(field_name)) == list
    ):
        if type(data.get(field_name)) == UploadFile:
            files = [data[field_name]]
        elif type(data.get(field_name)) == tuple:
            if type(data.get(field_name)[0]) == UploadFile:
                files = [data[field_name][0]]
            else:
                files = data[field_name][0]
        elif type(data.get(field_name) == list):
            files = data[field_name]

        new_files = list()
        for file in files:
            if file.filename != "":
                if os.path.exists(f"media/files/{file.filename}"):
                    i = 1
                    paths_parts = [
                        file.filename[: file.filename.rindex(".")],
                        file.filename[file.filename.rindex(".") + 1 :],
                    ]
                    while os.path.exists(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}"
                    ):
                        i += 1
                    with open(
                        f"media/files/{paths_parts[0]}({i}).{paths_parts[1]}", "wb"
                    ) as f:
                        content = file.file.read()
                        f.write(content)
                        file_link = f.name[6:]
                else:
                    with open(f"media/files/{file.filename}", "wb") as f:
                        content = file.file.read()
                        f.write(content)
                        file_link = f.name[6:]
                new_files.append(
                    (file_link, False) if type(data[field_name]) == tuple else file_link
                )
            else:
                if entity_id:
                    db = next(get_db())
                    entity = (
                        db.query(tables_dict[table_name])
                        .filter(tables_dict[table_name].id == entity_id)
                        .first()
                    )
                    new_files.append(entity.__getattribute__(field_name))
                else:
                    new_files.append(None)
        if len(new_files) > 0:
            if not multiple:
                data[field_name] = new_files[0]
                return data
            data[field_name] = new_files
            for i, el in enumerate(data[field_name]):
                if type(el) == list:
                    data[field_name][i] = el[0]
        else:
            data[field_name] = None
    return data


def phone_validator(phone: str) -> bool | str:
    try:
        number = phonenumbers.parse(phone)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    if not phonenumbers.is_valid_number(number):
        return False
    new_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    return new_number
