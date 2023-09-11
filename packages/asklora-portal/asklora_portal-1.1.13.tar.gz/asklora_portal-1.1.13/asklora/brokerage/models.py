from datetime import date, datetime
from os import PathLike
from pathlib import Path
from typing import Any, List, Literal, Union

from pydantic import BaseModel, constr, root_validator, validator
from pydantic_xml import BaseXmlModel, XmlEncoder, attr, element, wrapped

from ..utils.regexes import RegexPatterns
from . import enums

ECA_NSMAP = {"": "http://www.interactivebrokers.com/schemas/IBCust_import"}
ECA_CA_NSMAP = {"": "http://www.cstools.interactivebrokers.com"}
FB_NSMAP = {
    "": "http://www.interactivebrokers.com/fbfb_instruction_set",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


# ------------------------------- Broker response model ------------------------------ #
class BrokerResponse(BaseModel):
    url: str
    raw_payload: str | dict | None = None
    payload: dict
    raw_response: dict | None = None
    response: dict | None = None


# ------------------------------------ ECA models ------------------------------------ #
class CustomXmlEncoder(XmlEncoder):
    def __init__(self):
        super().__init__(str)

    def encode(self, obj: Any) -> str:
        if isinstance(obj, bool):
            return str(obj).lower()

        return super().encode(obj)


class Name(BaseXmlModel, nsmap=ECA_NSMAP):
    first: constr(max_length=50) = attr()
    last: constr(max_length=50) = attr()
    middle: constr(max_length=18) | None = attr()
    salutation: constr(regex=RegexPatterns.salutation) | None = attr()

    def get_full_name(self, with_initial: bool = False) -> str:
        full_name = self.first

        if self.middle:
            middle_name = f" {self.middle[0]}" if with_initial else f" {self.middle}"
            full_name += middle_name

        if self.last:
            full_name += f" {self.last}"

        return full_name


class Email(BaseXmlModel, nsmap=ECA_NSMAP):
    email: constr(regex=RegexPatterns.email) = attr()


class Phone(BaseXmlModel, nsmap=ECA_NSMAP):
    type: enums.PhoneTypeEnum = attr()
    number: constr(max_length=18) = attr()
    country: constr(min_length=3, max_length=3)

    class Config:
        arbitrary_types_allowed = True


class Residence(BaseXmlModel, nsmap=ECA_NSMAP):
    country: constr(min_length=3, max_length=3) = attr()
    state: str | None = attr()
    city: constr(max_length=100) = attr()
    postal_code: constr(max_length=20) = attr()
    street_1: constr(max_length=200) = attr()
    street_2: constr(max_length=200) | None = attr()


class MailingAddress(BaseXmlModel, nsmap=ECA_NSMAP):
    country: constr(min_length=3, max_length=3) = attr()
    state: str = attr()
    city: constr(max_length=100) = attr()
    postal_code: constr(max_length=20) = attr()
    street_1: constr(max_length=200) = attr()
    street_2: constr(max_length=200) | None = attr()


class Identification(BaseXmlModel, nsmap=ECA_NSMAP):
    citizenship: constr(min_length=3, max_length=3) = attr()
    issuing_country: constr(min_length=3, max_length=3) = attr(name="IssuingCountry")

    # types of ID, need to fill at least one of these
    national_card: str | None = attr(name="NationalCard")
    sin: str | None = attr(name="SIN")
    drivers_license: str | None = attr(name="DriversLicense")

    @root_validator
    def check_identification(cls, values):
        if not any(
            [
                values.get("national_card"),
                values.get("drivers_license"),
                values.get("sin"),
            ]
        ):
            raise ValueError("Need to have at least one identification item")

        return values


class TaxResidency(BaseXmlModel, nsmap=ECA_NSMAP):
    country: constr(min_length=3, max_length=3) = attr()
    tin_type: enums.TINTypeEnum = attr(name="TINType")

    # Required for non-US residents who has a Foreign Tax ID
    tin: str | None = attr(name="TIN")

    class Config:
        arbitrary_types_allowed = True


class EmployerAddress(BaseXmlModel, nsmap=ECA_NSMAP):
    country: str = attr()
    state: str | None = attr()
    city: constr(max_length=100) | None = attr()
    postal_code: constr(max_length=20) | None = attr()
    street_1: constr(max_length=200) | None = attr()


class EmploymentDetails(BaseXmlModel, nsmap=ECA_NSMAP):
    employer: constr(max_length=128) = element()
    occupation: str | None = element()
    employer_business: str | None = element()
    employer_address: EmployerAddress = element()


class W8Ben(BaseXmlModel, nsmap=ECA_NSMAP):
    # whether the applicant accepts the terms (https://www.ibkrguides.com/dameca/Schema/W8Ben.htm#:~:text=Under%20penalties%20of,8BEN%20is%20correct.)
    cert: bool = attr()

    part_2_9a_country: constr(min_length=3, max_length=3) = attr()
    name: str = attr()
    blank_form: bool = attr()
    signature_type: Literal["Electronic"] | None = attr()
    tax_form_file: str = attr()
    foreign_tax_id: str | None = attr()
    proprietary_form_number: str | None = attr()
    explanation: enums.W8BenExplanationEnum | None = attr()

    class Config:
        arbitrary_types_allowed = True


class AccountHolderDetails(BaseXmlModel, nsmap=ECA_NSMAP):
    # attributes
    external_id: str = attr()
    same_mail_address: bool = attr()

    # children
    name: Name = element(tag="Name")
    country_of_birth: constr(min_length=3, max_length=3) = element(tag="CountryOfBirth")
    dob: date = element(tag="DOB")
    email: Email = element(tag="Email")
    num_dependents: int | None = element(tag="NumDependents")
    marital_status: enums.MaritalStatusEnum | None = element(tag="MaritalStatus")
    phone: list[Phone] | None = wrapped("Phones", element(tag="Phone"))
    residence: Residence = element(tag="Residence")
    mailing_address: MailingAddress | None = element(tag="MailingAddress")
    identification: Identification | None = element(tag="Identification")
    tax_residencies: list[TaxResidency] = wrapped(
        "TaxResidencies",
        element(tag="TaxResidency"),
    )
    w8ben: W8Ben | None = element(tag="W8Ben")
    employment_type: enums.EmploymentTypeEnum | None = element(tag="EmploymentType")
    employment_details: EmploymentDetails | None = element(tag="EmploymentDetails")

    class Config:
        arbitrary_types_allowed = True


class SourceOfWealth(BaseXmlModel, nsmap=ECA_NSMAP):
    percentage: int = attr()
    source_type: enums.SourceOfWealthEnum = attr()
    is_used_for_funds: bool = attr()


class FinancialInformation(BaseXmlModel, nsmap=ECA_NSMAP):
    data: str = " "
    # sources_of_wealth: list[SourceOfWealth] | None = wrapped(
    #     "SourcesOfWealth",
    #     element(tag="SourceOfWealth"),
    # )


class AccountHolder(BaseXmlModel, nsmap=ECA_NSMAP):
    details: AccountHolderDetails = element(tag="AccountHolderDetails")
    financial_information: FinancialInformation = element(tag="FinancialInformation")


class Customer(BaseXmlModel, nsmap=ECA_NSMAP):
    # attributes
    email: str = attr()
    external_id: str = attr()
    has_direct_trading_access: bool = attr()
    legal_residence_country: str | None = attr()
    md_status_nonpro: bool = attr()
    meets_aml_standard: bool = attr()
    prefix: str = attr()
    customer_type: str = attr(name="type")

    # children
    account_holder: AccountHolder = element(tag="AccountHolder")


class TradingPermission(BaseXmlModel, nsmap=ECA_NSMAP):
    exchange_group: str | None = attr()
    product: str | None = attr()
    country: str | None = attr()


class Account(BaseXmlModel, nsmap=ECA_NSMAP):
    # attributes
    external_id: str = attr()
    base_currency: str = attr()
    margin: enums.AccountMarginEnum = attr()
    property_profile: str = attr()
    multicurrency: bool = attr()
    drip: bool | None = attr()
    client_active_trading: bool | None = attr()

    # children
    trading_permissions: list[TradingPermission] = wrapped(
        "TradingPermissions",
        element(tag="TradingPermission"),
    )

    class Config:
        arbitrary_types_allowed = True


class User(BaseXmlModel, nsmap=ECA_NSMAP):
    external_individual_id: str = attr()
    external_user_id: str = attr()
    prefix: constr(regex=RegexPatterns.prefix) = attr()


class AttachedFile(BaseXmlModel, nsmap=ECA_NSMAP):
    file_name: str = attr()
    file_length: str = attr()
    sha1_checksum: str = attr()

    @validator("file_name")
    def validate_file_types(cls, value):
        allowed_types = (".jpeg", ".jpg", ".pdf", ".png")

        if not value.endswith(allowed_types):
            raise ValueError("File type is invalid")

        return value


class Document(BaseXmlModel, nsmap=ECA_NSMAP):
    # attributes
    form_no: int = attr()
    exec_ts: int = attr()
    exec_login_ts: int = attr()
    proof_of_identity_type: str | None = attr()
    proof_of_address_type: str | None = attr()
    valid_address: bool | None = attr()
    expiration_date: date | None = attr()

    # children
    signed_by: str = element(tag="SignedBy")
    attached_file: list[AttachedFile] = element(tag="AttachedFile")


class Application(BaseXmlModel, nsmap=ECA_NSMAP):
    customer: Customer = element(tag="Customer", default={})
    accounts: list[Account] = wrapped(
        "Accounts",
        element(
            tag="Account",
            default_factory=list,
        ),
    )
    users: list[User] = wrapped(
        "Users",
        element(
            tag="User",
            default_factory=list,
        ),
    )
    documents: list[Document] = wrapped(
        "Documents",
        element(
            tag="Document",
            default_factory=list,
        ),
    )


class Applications(BaseXmlModel, nsmap=ECA_NSMAP):
    applications: list[Application] = element(tag="Application", default_factory=list)


class DAMApplicationPayload(BaseModel):
    user_id: int | str

    # name information
    first_name: str
    middle_name: str | None
    last_name: str
    salutation: str | None

    # user data
    date_of_birth: date
    country_of_birth: str

    # contact data
    email: str

    # identification
    identification_citizenship: str
    identification_issuing_country: str
    identification_number: str

    # residence information
    country: str
    state: str | None
    postal_code: str
    city: str
    street_name: str
    is_mailing_address: bool = True

    # mailing address (only required if `is_mailing_address` is False)
    mailing_country: str | None
    mailing_state: str | None
    mailing_postal_code: str | None
    mailing_city: str | None
    mailing_street_name: str | None

    # tax info
    tax_country: str
    tin: str

    # documents
    w8ben_file: str | PathLike
    proof_of_identity_type: str = "National ID Card"
    proof_of_identity_files: list[str | PathLike]

    class Config:
        arbitrary_types_allowed = True

    @property
    def attached_files(self):
        files = [self.w8ben_file, *self.proof_of_identity_files]

        return files

    @property
    def email_data(self) -> Email:
        return Email(email=self.email)

    @property
    def name_data(self) -> Name:
        return Name(
            first=self.first_name,
            last=self.last_name,
            middle=self.middle_name,
            salutation=self.salutation,
        )

    @property
    def residence_data(self) -> Residence:
        return Residence(
            country=self.country,
            state=self.state,
            city=self.city,
            postal_code=self.postal_code,
            street_1=self.street_name,
        )

    @property
    def mailing_address_data(self) -> MailingAddress | None:
        if self.is_mailing_address:
            return None

        return MailingAddress(
            country=self.mailing_country,
            state=self.mailing_state,
            city=self.mailing_city,
            postal_code=self.mailing_postal_code,
            street_1=self.mailing_street_name,
        )

    @property
    def identification_data(self) -> Identification:
        id_data = {
            "citizenship": self.identification_citizenship,
            "issuing_country": self.identification_issuing_country,
        }

        match self.identification_issuing_country:
            case "CAN":
                id_data["sin"] = self.identification_number
            case _:
                id_data["national_card"] = self.identification_number

        return Identification(**id_data)

    @property
    def tax_residency_data(self) -> TaxResidency:
        return TaxResidency(
            country=self.tax_country,
            tin_type=enums.TINTypeEnum.NON_US.value,
            tin=self.tin,
        )

    @property
    def account_holder_data(self) -> AccountHolder:
        w8ben = W8Ben(
            cert=True,
            part_2_9a_country="N/A",
            name=self.name_data.get_full_name(),
            proprietary_form_number="5001",
            blank_form=True,
            tax_form_file="Form5001.pdf",
            foreign_tax_id=self.tin,
        )

        return AccountHolder(
            details=AccountHolderDetails(
                external_id=self.user_id,
                same_mail_address=self.is_mailing_address,
                name=self.name_data,
                country_of_birth=self.country_of_birth,
                dob=self.date_of_birth,
                email=self.email_data,
                residence=self.residence_data,
                mailing_address=self.mailing_address_data,
                identification=self.identification_data,
                tax_residencies=[self.tax_residency_data],
                w8ben=w8ben,
            ),
            financial_information=FinancialInformation(),
        )

    @property
    def customer_data(self) -> Customer:
        return Customer(
            email=self.email,
            external_id=self.user_id,
            prefix="lora",
            customer_type="INDIVIDUAL",
            md_status_nonpro=False,
            meets_aml_standard=True,
            has_direct_trading_access=False,
            account_holder=self.account_holder_data,
        )

    @property
    def account_data(self) -> Account:
        return Account(
            external_id=self.user_id,
            base_currency="USD",
            margin=enums.AccountMarginEnum.CASH.value,
            property_profile="CashAccount",
            multicurrency=False,
            drip=False,
            client_active_trading=False,
            trading_permissions=[
                TradingPermission(product="STOCKS", country="UNITED STATES"),
                # TradingPermission(exchange_group="FOREX"),
            ],
        )

    @property
    def user_data(self) -> User:
        return User(
            external_individual_id=self.user_id,
            external_user_id=self.user_id,
            prefix="lora",
        )

    @property
    def documents_data(self) -> list[Document]:
        from asklora.utils import get_file_sha1, get_file_size

        current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        documents = []

        # W8BEN file
        w8ben_file = (
            Path(self.w8ben_file)
            if isinstance(self.w8ben_file, str)
            else self.w8ben_file
        )
        w8ben_document = Document(
            form_no="5001",
            exec_ts=current_timestamp,
            exec_login_ts=current_timestamp,
            signed_by=self.name_data.get_full_name(with_initial=True),
            attached_file=[
                AttachedFile(
                    file_name=w8ben_file.name,
                    file_length=get_file_size(w8ben_file),
                    sha1_checksum=get_file_sha1(w8ben_file),
                ),
            ],
        )
        documents.append(w8ben_document)

        # since identity proofs can be more than one file (front and back of ID card), we need to
        # put all of them in a list
        attached_files = []

        for proof in self.proof_of_identity_files:
            proof = Path(proof) if isinstance(proof, str) else proof
            attached_file = AttachedFile(
                file_name=proof.name,
                file_length=get_file_size(proof),
                sha1_checksum=get_file_sha1(proof),
            )
            attached_files.append(attached_file)

        identification_document = Document(
            form_no="8001",
            exec_ts=current_timestamp,
            exec_login_ts=current_timestamp,
            proof_of_identity_type=self.proof_of_identity_type,
            signed_by=self.name_data.get_full_name(with_initial=True),
            attached_file=attached_files,
        )
        documents.append(identification_document)

        return documents

    def generate_application_xml(self):
        application = Application(
            customer=self.customer_data,
            accounts=[self.account_data],
            users=[self.user_data],
            documents=self.documents_data,
        )

        applications = Applications(applications=[application])

        return applications.to_xml(
            encoder=CustomXmlEncoder(),
            pretty_print=True,
            encoding="UTF-8",
            skip_empty=True,
            standalone=True,
        ).decode()


# --------------------------------- Corporate actions -------------------------------- #
class CASearchRequest(BaseXmlModel, nsmap=ECA_CA_NSMAP):
    corp_action_type: enums.CorpActionType = attr(name="corpActionType")
    account_id: str = attr(name="accountId")
    account_ids: str | None = attr(name="accountIds")
    sub_accounts_choice: enums.SubAccuntsChoice = attr(name="subAccountsChoice")
    from_date: str = attr(name="fromDate")
    to_date: str = attr(name="toDate")

    @root_validator
    def check_account_ids(cls, values):
        sub_accounts_choice = values.get("sub_accounts_choice")
        account_ids = values.get("account_ids")

        if (
            sub_accounts_choice == enums.SubAccuntsChoice.SPECIFIED
            and account_ids is None
        ):
            raise ValueError(
                "account_ids cannot be empty if sub_accounts_choice is set to SPECIFIC"
            )

        return values


class CARequest(BaseXmlModel, nsmap=ECA_CA_NSMAP):
    ca_id: List[str] = element(tag="ibCAId")
    account_id: str = attr(name="accountId")
    sub_accounts_choice: enums.SubAccuntsChoice = attr(name="subAccountsChoice")
    include_details: bool = attr(name="includeDetails")
    include_positions: bool = attr(name="includePositions")


class Election(BaseXmlModel):
    choice_num: int = attr(name="choiceNum")
    # xsd use "long" but in case for fraction shares
    qty: int | float = attr(name="qty")
    bid_price: int | float | None = attr(name="bidPrice")


class CAElection(BaseXmlModel):
    election: List[Election] = element(tag="Election")
    ca_id: str = attr(name="ibCAId")
    account_id: str = attr(name="accountId")


class CAElectRequest(BaseXmlModel, nsmap=ECA_CA_NSMAP):
    ca_election: List[CAElection] = element(tag="CAElection")


# ----------------------------------- ECA responses ---------------------------------- #
class Execution(BaseXmlModel):
    execution_date: str = element(tag="Execution_Date")
    process_file: str = element(tag="Process_File")
    client: str = element(tag="Client")
    client_master_account: str = element(tag="Client_Master_Acct")


class ResponseUser(BaseXmlModel):
    external_id: str = attr()
    user_id: str = attr()
    password: str = attr()

    account: str


class ResponseAccount(BaseXmlModel):
    external_id: str = attr()
    status: str = attr()

    account_id: str


class ResponseEntity(BaseXmlModel):
    external_id: str = attr()

    entity_id: str


class ResponseDocument(BaseXmlModel):
    form_number: str = attr(name="Form_Number")
    file_name: str = attr(name="File_Name")
    status: str = attr(name="Status")


class ResponseTask(BaseXmlModel):
    form_number: str = attr(name="Form_Number")
    form_name: str = attr(name="Form_Name")
    action: str = attr(name="Action")
    required_for_approval: bool = attr(name="Is_Required_For_Approval")
    required_for_trading: bool = attr(name="Is_Required_For_Trading")
    online_task: bool = attr(name="Is_Online_Task")


class ResponseError(BaseXmlModel):
    error: str


class ApplicationResponse(BaseXmlModel):
    external_id: str = attr(name="External_ID")
    status: str = attr(name="Status")

    customer: str = element(tag="Customer")
    users: list[ResponseUser] | None = wrapped(
        "Users",
        element(tag="User"),
    )
    accounts: list[ResponseAccount] | None = wrapped(
        "Accounts",
        element(tag="Account"),
    )
    entities: list[ResponseEntity] | None = wrapped(
        "Entities",
        element(tag="Entity"),
    )
    documents: list[ResponseDocument] | None = wrapped(
        "Documents",
        element(tag="Document"),
    )
    pending_tasks: list[ResponseTask] | None = wrapped(
        "Pending_Tasks",
        element(tag="Task"),
    )
    errors: list[ResponseError] | None = wrapped(
        "Errors",
        element(tag="Error"),
    )


class Process(BaseXmlModel):
    execution: Execution = element(tag="Execution")
    general_failure: str | None = element(tag="General_Failure")
    applications: list[ApplicationResponse] | None = wrapped(
        "Applications",
        element(tag="Application"),
    )


# ----------------------------------- Update Models ---------------------------------- #


class DocumentSubmission(BaseXmlModel, tag="DocumentSubmission", nsmap=ECA_NSMAP):
    reference_account_id: str = attr()
    documents: list[Document] = element()


class TradingPermissions(BaseXmlModel, nsmap=ECA_NSMAP):
    reference_account_id: str = attr()
    permissions: list[TradingPermission] = element(tag="TradingPermission")


class AddTradingPermissions(TradingPermissions, tag="AddTradingPermissions"):
    pass


class RemoveTradingPermissions(TradingPermissions, tag="RemoveTradingPermissions"):
    pass


AccountManagementActions = Union[
    AddTradingPermissions,
    RemoveTradingPermissions,
    DocumentSubmission,
]


class AcctMgmtRequests(BaseXmlModel, nsmap=ECA_NSMAP):
    actions: list[AccountManagementActions] = element()


# ------------------------------------- FB Models ------------------------------------ #
def validate_currency(currency: str) -> str:
    if currency not in enums.DAMFBCurrencyEnum:
        raise ValueError("Invalid currency")

    return currency


class BaseInstruction(BaseXmlModel):
    id: int = attr()


class BaseTransactionInstruction(BaseInstruction):
    account_number: str = element()
    amount: int | float = element()
    method: enums.TransactionMethodEnum = element()
    currency: str = element()
    saved_instruction_name: str | None = element()

    class Config:
        smart_union = True

    # validators
    _validate_currency = validator("currency", allow_reuse=True)(validate_currency)


class WithdrawFunds(
    BaseTransactionInstruction,
    tag="withdraw_funds",
    nsmap=FB_NSMAP,
):
    date_time_to_occur: datetime | None = element()


class DepositFunds(
    BaseTransactionInstruction,
    tag="deposit_funds",
    nsmap=FB_NSMAP,
):
    identifier: str | None = element()
    sending_institution: str | None = element()
    special_instructions: str | None = element()


class InternalCashTransfer(
    BaseInstruction,
    tag="internal_cash_transfer",
    nsmap=FB_NSMAP,
):
    source: str = element(tag="source_ib_acct")
    destination: str = element(tag="destination_ib_acct")
    amount: int | float = element()
    currency: str = element(default="USD")
    date_time_to_occur: datetime | None = element()

    # validators
    _validate_currency = validator("currency", allow_reuse=True)(validate_currency)


class SecurityId(BaseXmlModel, tag="security_id", nsmap=FB_NSMAP):
    type: Literal["CUSIP", "ISIN"] = attr()
    id: str


class TradingProduct(BaseXmlModel, tag="trading_product", nsmap=FB_NSMAP):
    security_id: SecurityId = element()
    asset_type: enums.AssetTypeEnum = element()
    currency: str = element()


class IntPositionTransfer(
    BaseInstruction,
    tag="int_position_transfer",
    nsmap=FB_NSMAP,
):
    source: str = element(tag="source_ib_acct")
    destination: str = element(tag="destination_ib_acct")

    # if using contract id
    contract_id: str | None = element(tag="con_id")
    contract_desc: str | None = element()

    # if using ISIN
    trading_product: TradingProduct | None = element()

    position: int = element()
    quantity: int = element(tag="transfer_quantity")
    currency: str = element(default="USD")

    # validators
    _validate_currency = validator("currency", allow_reuse=True)(validate_currency)


class GetWithdrawableCash(BaseInstruction, tag="get_withdrawable_cash", nsmap=FB_NSMAP):
    account_number: str = element()
    amount: int | float = element()
    currency: str = element()

    # validators
    _validate_currency = validator("currency", allow_reuse=True)(validate_currency)


class CloseAccount(BaseInstruction, tag="close_account", nsmap=FB_NSMAP):
    account_number: str = element(tag="client_ib_acct_id")
    close_reason: str = element()


class CancelTransaction(BaseInstruction, tag="cancel_transaction", nsmap=FB_NSMAP):
    ib_instr_id: str = element()
    reason: str = element()


InstructionType = Union[
    WithdrawFunds,
    DepositFunds,
    InternalCashTransfer,
    IntPositionTransfer,
    GetWithdrawableCash,
    CancelTransaction,
    CloseAccount,
]


class InstructionSet(BaseXmlModel, tag="instruction_set", nsmap=FB_NSMAP):
    schema_location: str = attr(
        name="schemaLocation",
        ns="xsi",
        nsmap=FB_NSMAP,
        default="http://www.interactivebrokers.com/fbfb_instruction_set fbfb_instruction_set.xsd ",
    )
    creation_date: date = attr(default="2019-01-11")
    id: int = attr(default=2)
    version: str = attr(default="1.2")
    instructions: list[InstructionType] = element()
