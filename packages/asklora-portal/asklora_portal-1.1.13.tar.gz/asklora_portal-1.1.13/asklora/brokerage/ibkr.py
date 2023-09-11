import binascii
from base64 import b64decode
from copy import deepcopy
from datetime import date, datetime
from os import PathLike
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

from pydantic_xml import BaseXmlModel

from asklora.brokerage.client import BaseRestClient
from asklora.brokerage.enums import (
    AccountStatusType,
    DAMAllowedCurrenciesEnum,
    DAMEnumerationsTypeEnum,
)
from asklora.brokerage.models import (
    AcctMgmtRequests,
    AddTradingPermissions,
    AttachedFile,
    BrokerResponse,
    CAElection,
    CAElectRequest,
    CARequest,
    CASearchRequest,
    CustomXmlEncoder,
    DAMApplicationPayload,
    Document,
    DocumentSubmission,
    Election,
    InstructionSet,
    RemoveTradingPermissions,
    TradingPermission,
)
from asklora.brokerage.vars import DAMSettings
from asklora.dam import DAM
from asklora.logger import logger
from asklora.pgp import PGPHelper
from asklora.utils.file import get_file_sha1, get_file_size


class DAMECAClient(BaseRestClient):
    def __init__(self):
        # check environment variables
        dam_settings = DAMSettings()

        # assign attributes
        self.base_payload = dict(CSID=dam_settings.DAM_CSID)

        super().__init__(base_url=dam_settings.DAM_ECA_URL)

    # ------------------------------ Schema and Healthcheck ------------------------------ #

    def check_api(self) -> dict:
        return self.post("healthcheck", self.base_payload)

    def get_enumerations(
        self,
        enum_type: DAMEnumerationsTypeEnum,
        currency: Optional[str] = None,
        form_number: Optional[str] = None,
    ) -> str:
        if enum_type == DAMEnumerationsTypeEnum.EDD_AVT and form_number is None:
            raise ValueError("Need form number data for this enum type")

        if enum_type == DAMEnumerationsTypeEnum.FIN_INFO_RANGES and currency is None:
            raise ValueError("Need currency data for this enum type")

        payload = self.base_payload
        payload["type"] = enum_type.value

        if currency:
            if currency not in DAMAllowedCurrenciesEnum:
                raise ValueError("Invalid currency code")

            payload["currency"] = currency

        if form_number:
            payload["formNumber"] = form_number

        response = self.post("getEnumerations", self.base_payload, raw_response=True)
        decoded_response = b64decode(response).decode("utf-8")

        return decoded_response

    # ----------------- Create Accounts and Updating Account Information ----------------- #

    def create_account(
        self,
        applicant_data: DAMApplicationPayload,
        pgp_helper: PGPHelper,
    ) -> BrokerResponse:
        logger.info("Sending account creation payload to ECA endpoint")

        path = "create"
        payload = self.base_payload
        payload["payload"] = DAM.generate_application_payload(
            applicant_data,
            pgp_helper=pgp_helper,
        )

        # send the response
        response: dict = self.post(path, data=payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=urljoin(self.base_url, path),
            raw_payload=applicant_data.generate_application_xml(),
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        try:
            response_data.response = DAM.handle_eca_response(
                response,
                pgp_helper=pgp_helper,
            )
            logger.debug(f"Response:\n{response_data.response}")
        except (AttributeError, binascii.Error):
            pass

        return response_data

    # ------------------ View Account Information and Registration Tasks ----------------- #

    def get_pending_tasks(
        self,
        account_ids: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        payload = self.base_payload

        if account_ids:
            payload["accountIds"] = account_ids

        if start_date and end_date:
            payload["startDate"] = start_date
            payload["endDate"] = end_date

        return self.post("getPendingTasks", payload)

    def get_registration_tasks(
        self,
        account_ids: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        get_docs: Optional[bool] = None,
    ) -> dict:
        logger.info("Checking registration tasks")

        payload = self.base_payload

        if account_ids:
            payload["accountIds"] = account_ids

        if get_docs is not None:
            payload["getDocs"] = "T" if get_docs else "F"

        if get_docs is None and (start_date and end_date):
            payload["startDate"] = start_date
            payload["endDate"] = end_date

        response = self.post("getRegistrationTasks", payload)
        logger.info(f"Response:\n{response}")

        return response

    def get_account_details(self, account_ids: list[str]) -> dict:
        payload = self.base_payload
        payload["accountIds"] = account_ids

        return self.post("getAccountDetails", payload)

    def get_account_status(
        self,
        account_ids: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        status: AccountStatusType | str | None = None,
    ) -> dict:
        payload = self.base_payload

        if account_ids:
            payload["accountIds"] = account_ids
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        if status:
            if isinstance(status, AccountStatusType):
                status = status.value
            payload["status"] = status

        return self.post("getAccountStatus", payload)

    # ---------------------------------- Account update ---------------------------------- #

    def update_account(
        self,
        request_xml: str,
        pgp_helper: PGPHelper,
        attached_files: list[str | PathLike] | None = None,
    ) -> dict:
        path = "update"
        payload = self.base_payload
        payload["payload"] = DAM.encode_file_payload(
            request_xml,
            file_name="update.xml",
            pgp_helper=pgp_helper,
            archived=True,
            attached_files=attached_files,
        )

        # send the request
        response: dict = self.post(path, data=payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=urljoin(self.base_url, path),
            raw_payload=request_xml,
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        try:
            response_data.response = DAM.handle_eca_response(
                response,
                pgp_helper=pgp_helper,
            )
            logger.debug(f"Response:\n{response_data.response}")
        except (AttributeError, binascii.Error):
            pass

        return response_data

    # ----------------------------------- Upload files ----------------------------------- #

    def upload_identity_documents(
        self,
        account_id: str,
        full_name: str,
        pgp_helper: PGPHelper,
        proof_of_identity_type: str = "National ID Card",
        proof_of_identity_files: list[str | PathLike] | None = None,
    ) -> dict:
        current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        attached_files = []

        for proof in proof_of_identity_files:
            proof = Path(proof) if isinstance(proof, str) else proof
            attached_file = AttachedFile(
                file_name=proof.name,
                file_length=get_file_size(proof),
                sha1_checksum=get_file_sha1(proof),
            )
            attached_files.append(attached_file)

        document = Document(
            form_no="8001",
            exec_ts=current_timestamp,
            exec_login_ts=current_timestamp,
            proof_of_identity_type=proof_of_identity_type,
            signed_by=full_name,
            attached_file=attached_files,
        )
        request = AcctMgmtRequests(
            actions=[
                DocumentSubmission(
                    reference_account_id=account_id,
                    documents=[document],
                )
            ]
        )

        return self.update_account(
            request.to_xml(
                encoder=CustomXmlEncoder(),
                pretty_print=True,
                encoding="US-ASCII",
                skip_empty=True,
                standalone=True,
            ).decode(),
            pgp_helper,
            attached_files=proof_of_identity_files,
        )

    # ----------------------------- Close and suspend account ---------------------------- #

    def suspend_account(self, account_id: str, pgp_helper: PGPHelper) -> dict:
        request = AcctMgmtRequests(
            actions=[
                RemoveTradingPermissions(
                    reference_account_id=account_id,
                    permissions=[
                        TradingPermission(product="STOCKS", country="UNITED STATES"),
                    ],
                )
            ]
        )

        xml_payload = request.to_xml(
            encoder=CustomXmlEncoder(),
            pretty_print=True,
            encoding="UTF-8",
            skip_empty=True,
            standalone=True,
        ).decode()

        # hacky way, but well
        xml_payload = xml_payload.replace(
            "AddTradingPermissions",
            "RemoveTradingPermissions",
        )

        return self.update_account(xml_payload, pgp_helper)

    def unsuspend_account(self, account_id: str, pgp_helper: PGPHelper) -> dict:
        request = AcctMgmtRequests(
            actions=[
                AddTradingPermissions(
                    reference_account_id=account_id,
                    permissions=[
                        TradingPermission(product="STOCKS", country="UNITED STATES"),
                    ],
                )
            ]
        )

        xml_payload = request.to_xml(
            encoder=CustomXmlEncoder(),
            pretty_print=True,
            encoding="UTF-8",
            skip_empty=True,
            standalone=True,
        ).decode()

        return self.update_account(xml_payload, pgp_helper)


class DAMCAClient(BaseRestClient):
    """
    Client class for IBKR's Corporate Actions endpoint
    (https://www.ibkrguides.com/dameca/CorpAction/submit.htm)
    """

    def __init__(self):
        # check environment variables
        dam_settings = DAMSettings()

        # assign attributes
        self.base_payload = dict(CSID=dam_settings.DAM_CSID)

        super().__init__(base_url=dam_settings.DAM_CA_URL)

    def _base_request(
        self,
        request: BaseXmlModel,
        username: str,
        pgp_helper: PGPHelper,
    ):
        """
        Basic function to decode / encode requests / reponses to DAM CA

        Args:
            request (BaseXmlModel):
                Pydantic XML model define elements / attributes as input;
            username (str):
                username used for TWS login, e.g. asklo2340;
            pgp_helper (PGPHelper):
                PGPHelper object to encode / decode XML.

        Returns:
            Dictionary with base64Payload contains XML format response.
        """
        request_xml = request.to_xml(
            pretty_print=True,
            encoding="UTF-8",
            skip_empty=True,
            xml_declaration=True,
        ).decode()

        encoded_payload = DAM.encode_file_payload(
            request_xml,
            file_name="search.txt",
            pgp_helper=pgp_helper,
        )

        payload = self.base_payload
        payload["base64Payload"] = encoded_payload
        payload["username"] = username

        response = self.post("", payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=self.base_url,
            raw_payload=request_xml,
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        if "base64Payload" in response:
            response["base64Payload"] = DAM.decode_response(
                response.get("base64Payload"),
                pgp_helper=pgp_helper,
            )
            response_data.response = response

        return response_data

    # --------------------------- Corporate actions ------------------------ #
    def ca_search_request(
        self,
        action_type: str,
        account_id: str,
        username: str,
        sub_accounts: str,
        from_date: str,
        to_date: str,
        pgp_helper: PGPHelper,
    ) -> BrokerResponse:
        """
        Filter CA within date range to get CAId used for further CARequest.
        *This results will contain no position details.

        Args:
            action_type (str):
                e.g. ALL to get all types of CA;
            account_id (str):
                account_id with CA related positions, e.g. DI6777442;
            username (str):
                username used for TWS login, e.g. asklo2340;
            sub_accounts (SubAccuntsChoice):
                Whether to get events from all subaccounts, e.g. INCLUDE_SUBS;
            from_date (str):
                start date to search IBKR events in %Y%m%d format;
            to_date (str):
                end date to search IBKR events in %Y%m%d format;
            pgp_helper (PGPHelper):
                PGPHelper object to encode / decode XML.
        """
        request = CASearchRequest(
            corp_action_type=action_type,
            account_id=account_id,
            sub_accounts_choice=sub_accounts,
            from_date=from_date,
            to_date=to_date,
        )
        return self._base_request(request, username=username, pgp_helper=pgp_helper)

    def ca_request(
        self,
        ca_id: List[str],
        account_id: str,
        username: str,
        sub_accounts: str,
        pgp_helper: PGPHelper,
    ) -> BrokerResponse:
        """
        Get details & positions for certain CA event.

        Args:
            ca_id (List[str]):
                List of corporate action ID to get details (max=100);
            account_id (str):
                account_id with CA related positions, e.g. DI6777442;
            username (str):
                username used for TWS login, e.g. asklo2340;
            sub_accounts (SubAccuntsChoice):
                Whether to get events from all subaccounts, e.g. INCLUDE_SUBS;
            pgp_helper (PGPHelper):
                PGPHelper object to encode / decode XML.
        """
        request = CARequest(
            ca_id=ca_id,
            account_id=account_id,
            sub_accounts_choice=sub_accounts,
            include_details=True,
            include_positions=True,
        )
        return self._base_request(request, username=username, pgp_helper=pgp_helper)

    def ca_elect_request_single(
        self,
        ca_id: str,
        account_id: str,
        choice_num: int,
        qty: int | float,
        username: str,
        pgp_helper: PGPHelper,
        bid_price: int | float = None,
    ) -> BrokerResponse:
        """
        Make single election of voluntary CA events in request.
        # TODO: make multiple elections with 1 request

        Args:
            ca_id (str):
                Corporate action ID to make election;
            account_id (str):
                account_id to make election, must be subAccount;
            choice_num (int):
                option to elect, e.g.
                {"@number": "1", "@isDefault": "false",
                "description": "Submit ADR shares for conversion (FEES APPLY)"}
                If choose to convert, choice_num = 1;
            qty (int | float):
                amount of shares making this election,
                each election should have qty <= position assigned for CA,
                and Sum(qty) of all election = position assigned;
            bid_price (int | float, optional):
                Certain CA may require bid price for the election;
            username (str):
                username used for TWS login, e.g. asklo2340;
            pgp_helper (PGPHelper):
                PGPHelper object to encode / decode XML.
        """
        election = Election(
            choice_num=choice_num,
            qty=qty,
            bid_price=bid_price,
        )
        ca_election = CAElection(
            election=[election],
            ca_id=ca_id,
            account_id=account_id,
        )
        request = CAElectRequest(ca_election=[ca_election])
        return self._base_request(request, username=username, pgp_helper=pgp_helper)


class DAMFBClient(BaseRestClient):
    def __init__(self):
        # check environment variables
        dam_settings = DAMSettings()

        # assign attributes
        self.base_payload = dict(CSID=dam_settings.DAM_CSID)

        super().__init__(base_url=dam_settings.DAM_FB_URL)

    def create_instruction(
        self,
        instruction: InstructionSet | str,
        pgp_helper: PGPHelper,
    ) -> BrokerResponse:
        if isinstance(instruction, InstructionSet):
            instruction = instruction.to_xml(
                pretty_print=True,
                encoding="UTF-8",
                skip_empty=True,
                xml_declaration=True,
            ).decode()

        encoded_instruction = DAM.encode_file_payload(
            instruction,
            file_name="instructions.xml",
            pgp_helper=pgp_helper,
        )

        path = "new-request"
        payload = self.base_payload
        payload["request"] = encoded_instruction

        # send the request
        response = self.post(path, payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=urljoin(self.base_url, path),
            raw_payload=instruction,
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        if "details" in response:
            response["details"] = DAM.decode_response(
                response.get("details"),
                pgp_helper=pgp_helper,
            )
            response_data.response = response

        return response_data

    def get_status(self, instruction_id: int, pgp_helper: PGPHelper) -> BrokerResponse:
        encoded_instruction_ids = DAM.encode_file_payload(
            str(instruction_id),
            file_name="instruction_ids.txt",
            pgp_helper=pgp_helper,
        )

        path = "get-status"
        payload = self.base_payload
        payload["instruction_set_id"] = encoded_instruction_ids

        response = self.post(path, payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=urljoin(self.base_url, path),
            raw_payload=instruction_id,
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        if "details" in response:
            response["details"] = DAM.decode_response(
                response.get("details"),
                pgp_helper=pgp_helper,
            )
            response_data.response = response

        return response_data

    def get_updates(self, since: date | str, pgp_helper: PGPHelper) -> BrokerResponse:
        since = since if isinstance(since, str) else since.strftime("%Y-%m-%d")

        encoded_date = DAM.encode_file_payload(
            since,
            file_name="instruction_ids.txt",
            pgp_helper=pgp_helper,
        )

        path = "get_updated_upload_ids"
        payload = self.base_payload
        payload["since_yyyy-mm-dd"] = encoded_date

        response = self.post(path, payload)

        # add more context to the response
        response_data = BrokerResponse(
            url=urljoin(self.base_url, path),
            raw_payload=since,
            payload=payload,
            raw_response=deepcopy(response),
            response=response,
        )

        if "details" in response:
            response["details"] = DAM.decode_response(
                response.get("details"),
                pgp_helper=pgp_helper,
            )
            response_data.response = response

        return response_data
