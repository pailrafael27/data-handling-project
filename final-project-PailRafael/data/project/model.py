from __future__ import annotations

from dataclasses import field, dataclass
import random
from typing import Type, cast

import faker
from faker_music import MusicProvider
from faker import Faker
from data.project.base import Dataset, Entity


# TODO replace this module with your own types

@dataclass
class RentalDataset(Dataset):
    people: list[Person]
    credit_cards: list[Credit_Card]
    instruments: list[Instrument]

    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Person, Credit_Card, Instrument]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return RentalDataset(
            cast(list[Person], entities[0]),
            cast(list[Credit_Card], entities[1]),
            cast(list[Instrument], entities[2]),
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Person] = self.people
        res[Credit_Card] = self.credit_cards
        res[Instrument] = self.instruments

        return res

    @staticmethod
    def generate(
            count_of_customers: int,
            count_of_credit_cards: int,
            count_of_instrument: int
            ):

        def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                            unique: bool = False, min_age: int = 14, max_age: int = 100) -> list[Person]:
            assert n > 0
            assert 0 <= male_ratio <= 1
            assert 0 <= min_age <= max_age

            fake = Faker(locale)
            people = []
            for i in range(n):
                male = random.random() < male_ratio
                generator = fake if not unique else fake.unique
                people.append(Person(
                    "P-" + (str(i).zfill(6)),
                    generator.name_male() if male else generator.name_female(),
                    random.randint(min_age, max_age),
                    male))

            return people

        def generate_credit_cards(n: int, unique: bool = False) -> list[Credit_Card]:
            assert n > 0

            fake = Faker()
            fake.add_provider(faker.providers.credit_card)
            fake = fake if not unique else fake.unique

            credit_cards = []
            for i in range(n):
                credit_cards.append(Credit_Card(
                    fake.credit_card_number(),
                    fake.credit_card_provider(),
                    fake.credit_card_expire(),
                    fake.credit_card_security_code()))

            return credit_cards

        def generate_instruments(n: int, unique: bool = False) -> list[Instrument]:
            assert n > 0

            fake = Faker()
            fake.add_provider(MusicProvider)
            fake.add_provider(faker.providers.company)
            fake = fake if not unique else fake.unique

            instruments = []
            for i in range(n):
                instrument = Instrument(
                    fake.music_instrument(),
                    fake.company()
                )

                instruments.append(instrument)

            return instruments


        people = generate_people(count_of_customers)
        credit_cards = generate_credit_cards(count_of_credit_cards)
        instruments = generate_instruments(count_of_instrument)
        for i in range(len(people)):
            person = people[i]
            person.instrument_name = instruments[random.randint(0,len(instruments)-1)].instrument_name
            person.credit_card_number = credit_cards[i].credit_card_number
        return RentalDataset(people, credit_cards, instruments)

    @staticmethod
    def field_names() -> list[str]:
        return ["people", "credit_cards", "instruments"]



@dataclass
class Instrument(Entity):
    instrument_name: str = field(hash=True)
    manufacturer: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Instrument:
        return Instrument(seq[0], seq[1])

    def to_sequence(self) -> list[str]:
        return [self.instrument_name, self.manufacturer]

    @staticmethod
    def field_names() -> list[str]:
        return ["instrument_name", "manufacturer"]

    @staticmethod
    def collection_name() -> str:
        return "instruments"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Instrument.collection_name()} (
            instrument_name VARCHAR(100) NOT NULL PRIMARY KEY,
            manufacturer Varchar(100)
        );
        """


@dataclass
class Credit_Card(Entity):
    credit_card_number: str = field(hash=True)
    provider: str = field(repr=True, compare=False)
    expire: str = field(repr=True, compare=False)
    ccv: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Credit_Card:
        return Credit_Card(seq[0], seq[1], seq[2], seq[3])

    def to_sequence(self) -> list[str]:
        return [self.credit_card_number, self.provider, self.expire, self.ccv]

    @staticmethod
    def field_names() -> list[str]:
        return ["credit_card_number", "provider", "expire", "ccv"]

    @staticmethod
    def collection_name() -> str:
        return "credit_cards"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Credit_Card.collection_name()} (
            credit_card_number VARCHAR(50) NOT NULL PRIMARY KEY,
            provider VARCHAR(50),
            expire SMALLINT,
            ccv BOOLEAN
        );
        """


@dataclass
class Person(Entity):
    id: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)
    male: bool = field(default=True, repr=True, compare=False)
    credit_card_number: str = field(default=" ",repr=True, compare=False)
    instrument_name: str = field(default=" ",repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Person:
        return Person(seq[0], seq[1], int(seq[2]), bool(seq[3]), seq[4], seq[5])

    def to_sequence(self) -> list[str]:
        return [self.id, self.name, str(self.age), str(int(self.male)), self.credit_card_number, self.instrument_name]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "name", "age", "male", "credit_card_number", "instrument_name"]

    @staticmethod
    def collection_name() -> str:
        return "people"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Person.collection_name()} (
            id VARCHAR(8) NOT NULL PRIMARY KEY,
            name VARCHAR(50),
            age TINYINT,
            male BOOLEAN,
            credit_card_number VARCHAR(50),
            instrument_name VARCHAR(100),
            
            FOREIGN KEY (credit_card_number) REFERENCES {Credit_Card.collection_name()}(credit_card_number),
            FOREIGN KEY (instrument_name) REFERENCES {Instrument.collection_name()}(instrument_name)
        );
        """