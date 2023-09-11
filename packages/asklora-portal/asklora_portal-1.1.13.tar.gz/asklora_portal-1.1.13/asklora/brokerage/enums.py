from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class ExtendedEnum(BaseEnum):
    @classmethod
    @property
    def choices(cls):
        return tuple(map(lambda c: (c.name, c.value), cls))

    @classmethod
    def to_dict(cls):
        data = {}
        for c in cls:
            data[c.name] = c.value
        return data

    @classmethod
    def to_list(cls):
        return [c.value for c in cls]

    @classmethod
    def equal(cls, value1, value2):
        if isinstance(value1, cls):
            value1 = value1.value
        if isinstance(value2, cls):
            value2 = value2.value
        return value1 == value2

    @classmethod
    def lower(cls, value):
        if isinstance(value, cls):
            value = value.value
        return value.lower()


# +++++++++++++++++++++++++++++ ENUMS START BELOW +++++++++++++++++++++++++++++


class PhoneTypeEnum(str, Enum):
    WORK = "Work"
    HOME = "Home"
    FAX = "Fax"
    MOBILE = "Mobile"
    BUSINESS = "Business"


class MaritalStatusEnum(str, Enum):
    SINGLE = "S"
    MARRIED = "M"
    WIDOWED = "W"
    DIVORCED = "D"
    COMMON_LAW_PARTNER = "C"


class AccountMarginEnum(str, Enum):
    CASH = "Cash"
    MARGIN = "Margin"
    REGT = "RegT"
    PORTFOLIOMARGIN = "PortfolioMargin"


class TINTypeEnum(str, Enum):
    US = "SSN"
    NON_US = "NonUS_NationalId"
    ORG = "EIN"


class W8BenExplanationEnum(str, Enum):
    US_TIN = "US_TIN"
    TIN_NOT_DISCLOSED = "TIN_NOT_DISCLOSED"
    TIN_NOT_REQUIRED = "TIN_NOT_REQUIRED"
    TIN_NOT_ISSUED = "TIN_NOT_ISSUED"


class EmploymentTypeEnum(str, Enum):
    UNEMPLOYED = "UNEMPLOYED"
    EMPLOYED = "EMPLOYED"
    SELFEMPLOYED = "SELFEMPLOYED"
    RETIRED = "RETIRED"
    STUDENT = "STUDENT"
    ATHOMETRADER = "ATHOMETRADER"
    HOMEMAKER = "HOMEMAKER"


class SourceOfWealthEnum(str, Enum):
    ALLOWANCE = "SOW-IND-Allowance"
    DISABILITY = "SOW-IND-Disability"
    INCOME = "SOW-IND-Income"
    INHERITANCE = "SOW-IND-Inheritance"
    INTEREST = "SOW-IND-Interest"
    MARKETPROFIT = "SOW-IND-MarketProfit"
    OTHER = "SOW-IND-Other"
    PENSION = "SOW-IND-Pension"
    PROPERTY = "SOW-IND-Property"


class ProofOfAddressTypeEnum(str, Enum):
    BANK_STATEMENT = "Bank Statement"
    BROKERAGE_STATEMENT = "Brokerage Statement"
    HOMEOWNER_INSURANCE_POLICY_BILL = "Homeowner Insurance Policy Bill"
    HOMEOWNER_INSURANCE_POLICY_DOCUMENT = "Homeowner Insurance Policy Document"
    RENTER_INSURANCE_POLICY_BILL = "Renter Insurance Policy bill"
    RENTER_INSURANCE_POLICY_DOCUMENT = "Renter Insurance Policy Document"
    SECURITY_SYSTEM_BILL = "Security System Bill"
    GOVERNMENT_ISSUED_LETTERS = "Government Issued Letters"
    UTILITY_BILL = "Utility Bill"
    CURRENT_LEASE = "Current Lease"
    EVIDENCE_OF_OWNERSHIP_OF_PROPERTY = "Evidence of Ownership of Property"
    DRIVER_LICENSE = "Driver License"
    OTHER_DOCUMENT = "Other Document"


class DAMEnumerationsTypeEnum(str, Enum):
    FIN_INFO_RANGES = "FIN_INFO_RANGES"
    EMPLOYEE_TRACK = "EMPLOYEE_TRACK"
    BUSINESS_OCCUPATION = "BUSINESS_OCCUPATION"
    EXCHANGE_BUNDLES = "EXCHANGE_BUNDLES"
    ACATS = "ACATS"
    MARKET_DATA = "MARKET_DATA"
    PROHIBITED_COUNTRY = "PROHIBITED_COUNTRY"
    EDD_AVT = "EDD_AVT"


class AssetTypeEnum(str, Enum):
    BILL = "BILL"
    BOND = "BOND"
    CASH = "CASH"
    FUND = "FUND"
    OPT = "OPT"
    STK = "STK"
    WAR = "WAR"


class DAMAllowedCurrenciesEnum(ExtendedEnum):
    AUD = "AUD"
    GBP = "GBP"
    KRW = "KRW"
    PLN = "PLN"
    USD = "USD"
    CAD = "CAD"
    HKD = "HKD"
    MXN = "MXN"
    RUB = "RUB"
    CHF = "CHF"
    ILS = "ILS"
    SEK = "SEK"
    SGD = "SGD"
    EUR = "EUR"
    JPY = "JPY"
    NZD = "NZD"
    TRY = "TRY"


class DAMFBCurrencyEnum(str, Enum, metaclass=MetaEnum):
    USD = "USD"
    HUF = "HUF"
    EUR = "EUR"
    CZK = "CZK"
    GBP = "GBP"
    CNH = "CNH"
    CAD = "CAD"
    DKK = "DKK"
    JPY = "JPY"
    RUB = "RUB"
    HKD = "HKD"
    ILS = "ILS"
    AUD = "AUD"
    NOK = "NOK"
    CHF = "CHF"
    SGD = "SGD"
    MXN = "MXN"
    PLN = "PLN"
    SEK = "SEK"
    ZAR = "ZAR"
    NZD = "NZD"


class TransactionMethodEnum(str, Enum):
    ACHUS = "ACHUS"
    ACHCA = "ACHCA"
    WIRE = "WIRE"


class CorpActionType(str, Enum):
    MANDATORY = "MANDATORY"
    VOLUNTARY = "VOLUNTARY"
    ALL = "ALL"


class SubAccuntsChoice(str, Enum):
    NONE = "NONE"
    INCLUDE_SUBS = "INCLUDE_SUBS"
    SPECIFIED = "SPECIFIED"


class AccountStatusType(str, Enum):
    ABANDONED = "A"
    NEW = "N"
    OPEN = "O"
    CLOSED = "C"
    PENDING = "P"
    REJECTED = "R"
