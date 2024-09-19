from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.forms import (
    DriverCreationForm,
    CarSearchForm,
    ManufacturerSearchForm,
    DriverSearchForm
)
from taxi.models import Manufacturer, Car, Driver

MANUFACTURER_URL = reverse("taxi:manufacturer-list")
DRIVER_URL = reverse("taxi:driver-list")
CAR_URL = reverse("taxi:car-list")


class DriverFormsTests(TestCase):
    def test_driver_license_number_is_valid(self):
        license_numbers = [
            "ABCD1234",
            "AB123456",
            "ABc12345",
        ]
        form_data = {
            "username": "bob123",
            "password1": "test123test",
            "password2": "test123test",
            "first_name": "Bob",
            "last_name": "James",
            "license_number": "ABC12345",
        }
        form = DriverCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

        for license_number in license_numbers:
            form_data["license_number"] = license_number
            form = DriverCreationForm(data=form_data)
            self.assertFalse(form.is_valid())


class SearchFormsTests(TestCase):
    def setUp(self):
        self.manufacturers = Manufacturer.objects.bulk_create([
            Manufacturer(
                name=f"facture{i}",
                country=f"country{i}"
            )
            for i in range(3)
        ])
        self.drivers = [
            get_user_model().objects.create_user(
                username=f"bob123{i}",
                password="test123",
                first_name="Bob",
                last_name="James",
                license_number=f"ABC1234{i}",
            )
            for i in range(3)
        ]
        self.client.force_login(self.drivers[0])
        self.cars = Car.objects.bulk_create([
            Car(
                model=f"A{i}",
                manufacturer=self.manufacturers[0],
            )
            for i in range(5)
        ])

    def test_car_search_form_is_valid(self):
        form = CarSearchForm(data={"model": "A3"})
        self.assertTrue(form.is_valid())

    def test_manufacturer_search_form_is_valid(self):
        form = ManufacturerSearchForm(data={"name": "facture3"})
        self.assertTrue(form.is_valid())

    def test_driver_search_form_is_valid(self):
        form = DriverSearchForm(data={"username": "bob1233"})
        self.assertTrue(form.is_valid())

    def test_car_search_form_return_right_object(self):
        response = self.client.get(CAR_URL, {"model": "A3"})
        self.assertEqual(list(response.context["car_list"]), [self.cars[3]])

    def test_car_search_form_return_full_list(self):
        response = self.client.get(CAR_URL, {"model": ""})
        self.assertEqual(list(response.context["car_list"]), list(self.cars))

    def test_manufacturer_search_form_return_right_object(self):
        response = self.client.get(MANUFACTURER_URL, {"name": "facture1"})
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            [self.manufacturers[1]]
        )

    def test_manufacturer_search_form_return_full_list(self):
        response = self.client.get(MANUFACTURER_URL, {"name": ""})
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(self.manufacturers)
        )

    def test_driver_search_form_return_right_object(self):
        response = self.client.get(DRIVER_URL, {"username": "bob1231"})
        self.assertEqual(
            list(response.context["driver_list"]),
            [self.drivers[1]]
        )

    def test_driver_search_form_return_full_list(self):
        response = self.client.get(DRIVER_URL, {"username": ""})
        self.assertEqual(
            list(response.context["driver_list"]),
            list(self.drivers)
        )
