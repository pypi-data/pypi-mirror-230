from datetime import datetime

from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class RescissionWorkflow:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/rescission-workflow"

    def create(
        self,
        process_code: int = None,
        process_status: int = None,
        start_date: datetime = None,
        completion_date: datetime = None,
        applicant_name: str = None,
        applicant_email: str = None,
        applicant_enrollment: str = None,
        target_company_code: int = None,
        target_enrollment: int = None,
        target_name: str = None,
        effective_position_description: str = None,
        rescission_date: datetime = None,
        notice_date: datetime = None,
        target_admission_date: datetime = None,
        code_reason_rescission: int = None,
        activity_name: str = None,
        rescission_time: str = None,
        face_to_face_communication: str = None,
        email_corp_witness_1: str = None,
        email_corp_witness_2: str = None,
        workplace: str = None,
        zip_code: str = None,
        complete_address: str = None,
        private_email: str = None,
        private_phone: str = None,
        corporate_cell_phone: str = None,
        corporate_email: str = None,
        return_computer: bool = None,
        return_chair: bool = None,
        return_other_items: bool = None,
        access_data_center: bool = None,
        servicenow_sys_id: str = None,
        servicenow_ticket_number: str = None,
    ):
        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/",
            data={
                "process_code": process_code,
                "process_status": process_status,
                "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                "completion_date": completion_date.strftime("%Y-%m-%d")
                if completion_date
                else None,
                "applicant_name": applicant_name,
                "applicant_email": applicant_email,
                "applicant_enrollment": applicant_enrollment,
                "target_company_code": target_company_code,
                "target_enrollment": target_enrollment,
                "target_name": target_name,
                "effective_position_description": effective_position_description,
                "rescission_date": rescission_date.strftime("%Y-%m-%d")
                if rescission_date
                else None,
                "notice_date": notice_date.strftime("%Y-%m-%d")
                if notice_date
                else None,
                "target_admission_date": target_admission_date.strftime("%Y-%m-%d")
                if target_admission_date
                else None,
                "code_reason_rescission": code_reason_rescission,
                "activity_name": activity_name,
                "rescission_time": rescission_time,
                "face_to_face_communication": face_to_face_communication,
                "email_corp_witness_1": email_corp_witness_1,
                "email_corp_witness_2": email_corp_witness_2,
                "workplace": workplace,
                "zip_code": zip_code,
                "complete_address": complete_address,
                "private_email": private_email,
                "private_phone": private_phone,
                "corporate_cell_phone": corporate_cell_phone,
                "corporate_email": corporate_email,
                "return_computer": return_computer,
                "return_chair": return_chair,
                "return_other_items": return_other_items,
                "access_data_center": access_data_center,
                "servicenow_sys_id": servicenow_sys_id,
                "servicenow_ticket_number": servicenow_ticket_number,
            },
        )

    def read(self, rescission_uuid: str):
        return self.http.get(
            url=f"{self.severino_api_url}{self.path}/{rescission_uuid}/"
        )

    def list(self, filters: dict = {}):
        """List

        Args:
            filters (dict, optional): List of filters: private_email, private_phone, corporate_cell_phone, corporate_email, servicenow_sys_id, servicenow_ticket_number. E.g: {"private_email": "severino@gmail.com"}
        """
        return self.http.get(url=f"{self.severino_api_url}{self.path}/", params=filters)

    def update(
        self,
        process_code: int = None,
        process_status: int = None,
        start_date: datetime = None,
        completion_date: datetime = None,
        applicant_name: str = None,
        applicant_email: str = None,
        applicant_enrollment: str = None,
        target_company_code: int = None,
        target_enrollment: int = None,
        target_name: str = None,
        effective_position_description: str = None,
        rescission_date: datetime = None,
        notice_date: datetime = None,
        target_admission_date: datetime = None,
        code_reason_rescission: int = None,
        activity_name: str = None,
        rescission_time: str = None,
        face_to_face_communication: str = None,
        email_corp_witness_1: str = None,
        email_corp_witness_2: str = None,
        workplace: str = None,
        zip_code: str = None,
        complete_address: str = None,
        private_email: str = None,
        private_phone: str = None,
        corporate_cell_phone: str = None,
        corporate_email: str = None,
        return_computer: bool = None,
        return_chair: bool = None,
        return_other_items: bool = None,
        access_data_center: bool = None,
        servicenow_sys_id: str = None,
        servicenow_ticket_number: str = None,
    ):
        return self.http.patch(
            url=f"{self.severino_api_url}{self.path}/{process_code}/",
            data={
                "process_status": process_status,
                "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                "completion_date": completion_date.strftime("%Y-%m-%d")
                if completion_date
                else None,
                "applicant_name": applicant_name,
                "target_company_code": target_company_code,
                "target_enrollment": target_enrollment,
                "target_name": target_name,
                "effective_position_description": effective_position_description,
                "rescission_date": rescission_date.strftime("%Y-%m-%d")
                if rescission_date
                else None,
                "notice_date": notice_date.strftime("%Y-%m-%d")
                if notice_date
                else None,
                "target_admission_date": target_admission_date.strftime("%Y-%m-%d")
                if target_admission_date
                else None,
                "code_reason_rescission": code_reason_rescission,
                "activity_name": activity_name,
                "applicant_email": applicant_email,
                "applicant_enrollment": applicant_enrollment,
                "rescission_time": rescission_time,
                "face_to_face_communication": face_to_face_communication,
                "email_corp_witness_1": email_corp_witness_1,
                "email_corp_witness_2": email_corp_witness_2,
                "workplace": workplace,
                "zip_code": zip_code,
                "complete_address": complete_address,
                "private_email": private_email,
                "private_phone": private_phone,
                "corporate_cell_phone": corporate_cell_phone,
                "corporate_email": corporate_email,
                "return_computer": return_computer,
                "return_chair": return_chair,
                "return_other_items": return_other_items,
                "access_data_center": access_data_center,
                "servicenow_sys_id": servicenow_sys_id,
                "servicenow_ticket_number": servicenow_ticket_number,
            },
        )

    def partial_update(
        self,
        process_code: int,
        data: dict,
    ):
        return self.http.patch(
            url=f"{self.severino_api_url}{self.path}/{process_code}/", data=data
        )

    def delete(self, rescission_uuid):
        return self.http.delete(
            url=f"{self.severino_api_url}{self.path}/{rescission_uuid}/"
        )

    def change_status(self, process_code: str, sys_status: str):
        status_choices = [
            "waiting",
            "future_dismissal",
            "canceled",
            "not_processed",
            "ready",
            "success",
            "retry",
            "error",
            "error_but_finished",
        ]

        if not sys_status in status_choices:
            raise f"Invalid status, options are: {','.join(status_choices)}"

        data = {"sys_status": sys_status}

        return self.http.patch(
            url=f"{self.severino_api_url}{self.path}/{process_code}/",
            data=data,
        )
