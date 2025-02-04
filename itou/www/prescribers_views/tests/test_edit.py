from unittest import mock

from django.test import TestCase
from django.urls import reverse

from itou.prescribers.factories import (
    AuthorizedPrescriberOrganizationWithMembershipFactory,
    PrescriberOrganizationFactory,
    PrescriberOrganizationWithMembershipFactory,
)
from itou.prescribers.models import PrescriberOrganization
from itou.users.factories import DEFAULT_PASSWORD
from itou.utils.mocks.geocoding import BAN_GEOCODING_API_RESULT_MOCK


class CardViewTest(TestCase):
    def test_card(self):
        prescriber_org = PrescriberOrganizationFactory(is_authorized=True)
        url = reverse("prescribers_views:card", kwargs={"org_id": prescriber_org.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prescriber_org"], prescriber_org)


class EditOrganizationTest(TestCase):
    @mock.patch("itou.utils.apis.geocoding.call_ban_geocoding_api", return_value=BAN_GEOCODING_API_RESULT_MOCK)
    def test_edit(self, mock_call_ban_geocoding_api):
        """Edit a prescriber organization."""

        organization = AuthorizedPrescriberOrganizationWithMembershipFactory(
            kind=PrescriberOrganization.Kind.CAP_EMPLOI
        )
        user = organization.members.first()

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("prescribers_views:edit_organization")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "name": "foo",
            "siret": organization.siret,
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "address_line_1": "2 Rue de Soufflenheim",
            "address_line_2": "",
            "city": "Betschdorf",
            "post_code": "67660",
            "department": "67",
            "email": "",
            "phone": "0610203050",
            "website": "https://famous-siae.com",
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        mock_call_ban_geocoding_api.assert_called_once()

        organization = PrescriberOrganization.objects.get(siret=organization.siret)

        self.assertEqual(organization.name, post_data["name"])
        self.assertEqual(organization.description, post_data["description"])
        self.assertEqual(organization.address_line_1, post_data["address_line_1"])
        self.assertEqual(organization.address_line_2, post_data["address_line_2"])
        self.assertEqual(organization.city, post_data["city"])
        self.assertEqual(organization.post_code, post_data["post_code"])
        self.assertEqual(organization.department, post_data["department"])
        self.assertEqual(organization.email, post_data["email"])
        self.assertEqual(organization.phone, post_data["phone"])
        self.assertEqual(organization.website, post_data["website"])

        # This data comes from BAN_GEOCODING_API_RESULT_MOCK.
        self.assertEqual(organization.coords, "SRID=4326;POINT (2.316754 48.838411)")
        self.assertEqual(organization.latitude, 48.838411)
        self.assertEqual(organization.longitude, 2.316754)
        self.assertEqual(organization.geocoding_score, 0.587663373207207)

        # Only admins should be able to edit organization details
        membership = organization.prescribermembership_set.first()
        membership.is_admin = False
        membership.save()
        url = reverse("prescribers_views:edit_organization")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    @mock.patch("itou.utils.apis.geocoding.call_ban_geocoding_api", return_value=BAN_GEOCODING_API_RESULT_MOCK)
    def test_edit_with_multiple_memberships_and_same_siret(self, mock_call_ban_geocoding_api):
        """
        Updating information of the prescriber organization must be possible
        when user is member of multiple orgs with the same SIRET (and different types)
        (was a regression)
        """
        organization = PrescriberOrganizationWithMembershipFactory(kind=PrescriberOrganization.Kind.ML)
        siret = organization.siret
        user = organization.members.first()

        org2 = PrescriberOrganizationWithMembershipFactory(kind=PrescriberOrganization.Kind.PLIE, siret=siret)
        org2.members.add(user)
        org2.save()

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("prescribers_views:edit_organization")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "siret": siret,
            "name": "foo",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "address_line_1": "2 Rue de Soufflenheim",
            "address_line_2": "",
            "city": "Betschdorf",
            "post_code": "67660",
            "department": "67",
            "email": "",
            "phone": "0610203050",
            "website": "https://famous-siae.com",
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        url = reverse("dashboard:index")
        self.assertEqual(url, response.url)
