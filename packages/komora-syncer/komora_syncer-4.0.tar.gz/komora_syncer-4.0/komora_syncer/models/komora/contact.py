from typing import List
from datetime import datetime


class ContactType:
    contact_id: int
    contract_id: int
    contact_type_id: int
    contact_type_name: str
    id: int

    def __init__(self, **kwargs) -> None:
        self.contact_id = kwargs.get('contact_id')
        self.contract_id = kwargs.get('contract_id')
        self.contact_type_id = kwargs.get('contact_type_id')
        self.contact_type_name = kwargs.get('contact_type_name')
        self.id = kwargs.get('id')


class Email:
    email_address: str

    def __init__(self, **kwargs) -> None:
        self.email_address = kwargs.get('email_address')


class Organization:
    organization_name: str
    organization_id: int
    isActive: bool

    def __init__(self, **kwargs) -> None:
        self.organization_name = kwargs.get('organization_name')
        self.organization_id = kwargs.get('organization_id')
        self.isActive = kwargs.get('isActive')


class Tag:
    contact_id: int
    tag_id: int
    tag_name: str
    note: str
    id: int

    def __init__(self, **kwargs) -> None:
        self.contact_id = kwargs.get('contact_id')
        self.tag_id = kwargs.get('tag_id')
        self.tag_name = kwargs.get('tag_name')
        self.note = kwargs.get('note')
        self.id = kwargs.get('id')


class Contact:
    firstName: str
    surname: str
    title: str
    suffix: str
    contactTypes: List[ContactType]
    phoneNumber: str
    isActive: bool
    address: str
    phoneNumber2: str
    street: str
    city: str
    postCode: str
    validFrom: datetime
    validTo: datetime
    abraContactId: str
    organizations: List[Organization]
    updatedAt: datetime
    updatedBy: str
    fullName: str
    isEditable: bool
    lastContactedNote: str
    lastContactedBy: str
    lastContactedAt: datetime
    emails: List[Email]
    tags: List[Tag]
    id: int

    def __init__(self, **kwargs) -> None:
        self.firstName = kwargs.get('firstName')
        self.surname = kwargs.get('surname')
        self.title = kwargs.get('title')
        self.suffix = kwargs.get('suffix')
        self.contactTypes = kwargs.get('contactTypes')
        self.phoneNumber = kwargs.get('phoneNumber')
        self.isActive = kwargs.get('isActive')
        self.address = kwargs.get('address')
        self.phoneNumber2 = kwargs.get('phoneNumber2')
        self.street = kwargs.get('street')
        self.city = kwargs.get('city')
        self.postCode = kwargs.get('postCode')
        self.validFrom = kwargs.get('validFrom')
        self.validTo = kwargs.get('validTo')
        self.abraContactId = kwargs.get('abraContactId')
        self.organizations = kwargs.get('organizations')
        self.updatedAt = kwargs.get('updatedAt')
        self.updatedBy = kwargs.get('updatedBy')
        self.fullName = kwargs.get('fullName')
        self.isEditable = kwargs.get('isEditable')
        self.lastContactedNote = kwargs.get('lastContactedNote')
        self.lastContactedBy = kwargs.get('lastContactedBy')
        self.lastContactedAt = kwargs.get('lastContactedAt')
        self.emails = kwargs.get('emails')
        self.tags = kwargs.get('tags')
        self.id = kwargs.get('id')


"""
 "data": [
    {
      "firstName": "string",
      "surname": "string",
      "title": "string",
      "suffix": "string",
      "contactTypes": [
        {
          "contactId": 0,
          "contractId": 0,
          "contactTypeId": 0,
          "contactTypeName": "string",
          "id": 0
        }
      ],
      "phoneNumber": "string",
      "isActive": true,
      "address": "string",
      "phoneNumber2": "string",
      "street": "string",
      "city": "string",
      "postCode": "string",
      "validFrom": "2021-11-08T08:49:44.972Z",
      "validTo": "2021-11-08T08:49:44.972Z",
      "abraContactId": "string",
      "organizations": [
        {
          "organizationName": "string",
          "organizationId": 0,
          "isActive": true
        }
      ],
      "updatedAt": "2021-11-08T08:49:44.972Z",
      "updatedBy": "string",
      "fullName": "string",
      "isEditable": true,
      "lastContactedNote": "string",
      "lastContactedBy": "string",
      "lastContactedAt": "2021-11-08T08:49:44.972Z",
      "emails": [
        {
          "emailAddress": "string"
        }
      ],
      "tags": [
        {
          "contactId": 0,
          "tagId": 0,
          "tagName": "string",
          "note": "string",
          "id": 0
        }
      ],
      "id": 0
    }
  ]
"""
