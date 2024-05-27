from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from model_bakery import baker
import pytest

from store.models import Collection, Product, ProductImage


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post("/store/products/", product)

    return do_create_product


@pytest.fixture
def product_data():
    collection = baker.make(Collection)
    product = baker.make(Product)
    product_data = {
        "id": product.id,
        "title": product.title,
        "slug": product.slug,
        "unit_price": product.unit_price,
        "inventory": product.inventory,
        "last_update": product.last_update,
        "collection": collection.id,
    }

    return product_data


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))

    return do_authenticate


@pytest.mark.django_db
class TestCreateProduct:

    def test_if_user_is_anonymous_return_401(self, create_product, product_data):
        response = create_product(product_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_return_403(
        self, authenticate, create_product, product_data
    ):
        authenticate()
        response = create_product(product_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_return_400(self, authenticate, create_product):
        authenticate(is_staff=True)
        response = create_product(
            {
                "title": "",
                "slug": "",
                "unit_price": "",
                "inventory": "",
                "last_update": "",
                "collection": "",
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_return_201(self, authenticate, create_product):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        product = {
            "title": "a",
            "slug": "a",
            "unit_price": 1.0,
            "inventory": 1,
            "collection": collection.id,
        }
        response = create_product(product)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetriveProduct:

    def test_if_product_exists_return_200(self, api_client, product_data):
        product = baker.make(Product)
        price_with_tax = product.unit_price * Decimal(1.1)
        response = api_client.get(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': product.id,
            "title": product.title,
            "slug": product.slug,
            "description": product.description,
            "unit_price": product.unit_price,
            "inventory": product.inventory,
            "collection": product.collection.id,
            'price_with_tax': price_with_tax,
            'images': []
        }
