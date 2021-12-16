from dataclasses import dataclass
from datetime import date as date_
from datetime import timedelta
from math import ceil
from typing import Literal, Optional, TypedDict, Union


class hour_dict(TypedDict):
    date: str
    description: str
    duration: float
    per: float
    num_people: int


class drive_dict(TypedDict):
    date: str
    start: str
    end: str
    distance: float
    per: float


class expense_dict(TypedDict):
    date: str
    description: str
    quantity: float
    per: float


class customer_dict(TypedDict):
    name: str
    co: Optional[str]
    address: dict[str, str]


class invoice_dict(TypedDict):
    customer: customer_dict
    id: int
    date: str
    expiry_offset: int
    payment_account: str
    hours: tuple[hour_dict]
    drives: tuple[drive_dict]
    expenses: tuple[expense_dict]


class org_dict(TypedDict):
    name: str
    id: str
    address: dict[str, str]
    contact_info: dict[str, str]


class desc_dict(TypedDict):
    organization: org_dict
    invoices: tuple[invoice_dict]


@dataclass(init=False)
class chargable:
    date: date_
    per: float

    def __init__(self, date: Union[date_, str], per: float):
        self.per = per
        self.date = date if isinstance(date,
                                       date_) else date_.fromisoformat(date)


@dataclass(init=False)
class hour_(chargable):
    description: str
    duration: timedelta
    num_people: int = 1

    def __init__(
        self,
        date: Union[date_, str],
        description: str,
        duration: Union[timedelta, float],
        per: float,
        num_people: int = 1,
    ):
        super().__init__(date, per)
        self.description = description
        self.num_people = num_people
        self.duration = (duration if isinstance(duration, timedelta) else
                         timedelta(minutes=max(60, 30 * ceil(duration / 0.5))))

    @property
    def per_hour(self):
        return self.per * self.num_people

    @property
    def total(self) -> float:
        return (self.duration.seconds / 60 / 30) * (self.per /
                                                    2) * self.num_people


@dataclass(init=False)
class drive_(chargable):
    start: str
    end: str
    distance: float

    def __init__(self, date: Union[date_, str], start: str, end: str,
                 distance: float, per: float):
        super().__init__(date, per)
        self.start = start
        self.end = end
        self.distance = distance

    @property
    def total(self) -> float:
        return self.distance * self.per


@dataclass(init=False)
class expense_(chargable):
    description: str
    quantity: float

    def __init__(self, date: Union[date_, str], description: str,
                 quantity: float, per: float):
        super().__init__(date, per)
        self.description = description
        self.quantity = quantity

    @property
    def total(self) -> float:
        return self.quantity * self.per


@dataclass
class summary:
    type: Union[Literal["HOUR"], Literal["DRIVE"], Literal["EXPENSE"]]
    description: str
    quantity: Union[float, timedelta]
    unit: str
    total: float


@dataclass
class contact_info_:
    email: str
    phone: str


@dataclass
class address_:
    street: str
    area: str
    country: str


@dataclass(init=False)
class customer_:
    name: str
    address: address_
    co: Optional[str] = None

    def __init__(
        self,
        name: str,
        address: Union[address_, dict[str, str]],
        co: Optional[str] = None,
    ):
        self.name = name
        self.co = co

        self.address = address if isinstance(address, address_) else address_(
            **address)


@dataclass(init=False)
class invoice:
    customer: customer_
    id: int
    date: date_
    expiry_offset: timedelta
    payment_account: str
    hours: tuple[hour_, ...] = tuple()
    drives: tuple[drive_, ...] = tuple()
    expenses: tuple[expense_, ...] = tuple()

    def __init__(
        self,
        customer: Union[customer_, customer_dict],
        id: int,
        date: Union[date_, str],
        expiry_offset: Union[timedelta, int],
        payment_account: str,
        hours: Optional[tuple[Union[hour_, hour_dict], ...]] = None,
        drives: Optional[tuple[Union[drive_, drive_dict], ...]] = None,
        expenses: Optional[tuple[Union[expense_, expense_dict], ...]] = None,
    ):
        if isinstance(customer, customer_):
            self.customer = customer
        else:
            self.customer = customer_(**customer)

        self.id = id
        self.date = date if isinstance(date,
                                       date_) else date_.fromisoformat(date)
        self.expiry_offset = (expiry_offset if isinstance(
            expiry_offset, timedelta) else timedelta(days=expiry_offset))
        self.payment_account = payment_account

        if hours is not None:
            self.hours = tuple(
                sorted(
                    (hour if isinstance(hour, hour_) else hour_(**hour)
                     for hour in hours),
                    key=lambda x: x.date,
                ))

        if drives is not None:
            self.drives = tuple(
                sorted(
                    (drive if isinstance(drive, drive_) else drive_(**drive)
                     for drive in drives),
                    key=lambda x: x.date,
                ))

        if expenses is not None:
            self.expenses = tuple(
                sorted(
                    (expense if isinstance(expense, expense_) else expense_(
                        **expense) for expense in expenses),
                    key=lambda x: x.date,
                ))

    @property
    def summaries(self) -> tuple[summary, ...]:
        out: list[summary] = []
        if self.hours:
            out.append(
                summary(
                    "HOUR",
                    "Arbeidstimer",
                    sum((hour_.duration for hour_ in self.hours), timedelta()),
                    "Timer",
                    sum(hour_.total for hour_ in self.hours),
                ))
        if self.drives:
            out.append(
                summary(
                    "DRIVE",
                    "Kilometergodtgjørelse",
                    sum(drive.distance for drive in self.drives),
                    "Kilometer",
                    sum(drive.total for drive in self.drives),
                ))

        if self.expenses:
            out.append(
                summary(
                    "EXPENSE",
                    "Innkjøp",
                    sum(item.quantity for item in self.expenses),
                    "Artikler",
                    sum(item.total for item in self.expenses),
                ))

        return tuple(out)

    @property
    def total(self) -> float:
        return sum(x.total for x in self.summaries)


@dataclass(init=False)
class organization:
    name: str
    id: str
    address: Union[address_, dict[str, str]]
    contact_info: Union[contact_info_, dict[str, str]]

    def __init__(
        self,
        name: str,
        id: str,
        address: Union[address_, dict[str, str]],
        contact_info: Union[contact_info_, dict[str, str]],
    ):
        self.name = name
        self.id = id
        self.address = address if isinstance(address, address_) else address_(
            **address)
        self.contact_info = (contact_info if isinstance(
            contact_info, contact_info_) else contact_info_(**contact_info))
