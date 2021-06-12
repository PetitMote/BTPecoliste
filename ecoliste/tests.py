import random

from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import validate_material_origin
from BTPecoliste.settings import BTP_ECOLISTE_SETTINGS


class ValidateMaterialOriginTests(TestCase):
    def test_raises_no_error_for_correct_entry(self):
        correct_answers = BTP_ECOLISTE_SETTINGS["material_origins"]
        value = correct_answers[random.randint(0, len(correct_answers) - 1)]
        validate_material_origin(value)

    def test_raises_error_for_invalid_entry(self):
        value = "eknkenglkengz"
        self.assertRaises(
            ValidationError,
            validate_material_origin,
            [
                value,
            ],
        )

    def test_raises_error_for_invalid_case(self):
        correct_answers = BTP_ECOLISTE_SETTINGS["material_origins"]
        value = str(
            correct_answers[random.randint(0, len(correct_answers) - 1)]
        ).upper()
        self.assertRaises(
            ValidationError,
            validate_material_origin,
            [
                value,
            ],
        )
