from dataclasses import dataclass, field
from faker import Faker
from faker.providers import address, person, phone_number, credit_card, internet
import random
from typing import *


@dataclass
class Email:
    domain: str = field(default=None)
    address: str = field(init=False, default_factory=str)

    _faker: Faker = field(init=False, default_factory=Faker, repr=False)

    def __post_init__(self):
        self._faker.add_provider(internet)
        if self.domain is None:
            self.domain = self._faker.free_email_domain()
        self.address = self._faker.email(domain=self.domain)


@dataclass
class Address:
    street: str = field(init=False, default_factory=str)
    city: str = field(init=False, default_factory=str)
    state: str = field(init=False, default_factory=str)
    zip_code: str = field(init=False, default_factory=str)

    _faker: Faker = field(init=False, default_factory=Faker, repr=False)

    def __post_init__(self):
        self._faker.add_provider(address)
        full_address: List[str] = self._faker.address().split("\n")
        self.street = full_address[0]
        self.city = full_address[1].split(",")[0]
        self.state = full_address[1].split(" ")[1]
        self.zip_code = full_address[1].split(" ")[2]

    def display(self) -> str:
        return f"{self.street}, {self.city} {self.state}, {self.zip_code}"


@dataclass
class Person:
    gender: str | None = field(default=None)
    prefix: str = field(init=False, default_factory=str)
    first_name: str = field(init=False, default_factory=str)
    last_name: str = field(init=False, default_factory=str)

    _faker: Faker = field(init=False, default_factory=Faker, repr=False)

    def __post_init__(self):
        self._faker.add_provider(person)
        if self.gender not in ["male", "female", None]:
            raise ValueError("'gender' must be either 'male' or 'female', or None")
        if self.gender is None:
            self.gender = random.choice(["male", "female"])

        if self.gender == "male":
            full_name = self._faker.name_male()
            self.prefix = self._faker.prefix_male()
        elif self.gender == "female":
            full_name = self._faker.name_female()
            self.prefix = self._faker.prefix_female()
        else:
            raise ValueError("'gender' must be either 'male' or 'female', or None")

        self.first_name = full_name.split(" ")[0]
        self.last_name = full_name.split(" ")[1]


@dataclass
class CreditCard:
    number: str = field(init=False, default_factory=str)
    expires: str = field(init=False, default_factory=str)
    cvc: str = field(init=False, default_factory=str)

    provider: str = field(
        init=False, default=random.choice(["amex", "discover", "mastercard", "visa"])
    )
    owner: Person = field(default_factory=Person)

    _faker: Faker = field(init=False, default_factory=Faker, repr=False)

    def __post_init__(self):
        self._faker.add_provider(credit_card)
        if self.provider not in ["amex", "discover", "mastercard", "visa"]:
            raise ValueError("provider is invalid")

        card = self._faker.credit_card_full(card_type=self.provider).split("\n")
        self.number = card[2].split(" ")[0]
        self.expires = card[2].split(" ")[1]
        self.cvc = card[3].split(" ")[1]


@dataclass
class RandomIdentity:
    person: Person = field(default_factory=Person, init=False)
    credit_card: CreditCard = field(init=False, default_factory=CreditCard)
    email: Email = field(init=False, default_factory=Email)
    address: Address = field(init=False, default_factory=Address)

    def __post_init__(self):
        self.credit_card.owner = self.person

