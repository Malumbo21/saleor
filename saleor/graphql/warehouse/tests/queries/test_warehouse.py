import graphene

from ....core.utils import from_global_id_or_error
from ....tests.utils import (
    assert_no_permission,
    get_graphql_content,
    get_graphql_content_from_response,
)

QUERY_WAREHOUSE = """
query warehouse($id: ID!){
    warehouse(id: $id) {
        id
        name
        companyName
        email
        shippingZones(first: 100) {
            edges {
                node {
                    name
                    countries {
                        country
                    }
                }
            }
        }
        stocks(first: 50){
            edges{
                node{
                    id
                }
            }
        }
        address {
            streetAddress1
            streetAddress2
            postalCode
            city
            phone
        }
    }
}
"""


def test_warehouse_query(
    staff_api_client, warehouse_for_cc, permission_manage_products
):
    # given
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse_for_cc.pk)

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE,
        variables={"id": warehouse_id},
        permissions=[permission_manage_products],
    )

    # then
    content = get_graphql_content(response)

    queried_warehouse = content["data"]["warehouse"]
    assert queried_warehouse["name"] == warehouse_for_cc.name
    assert queried_warehouse["email"] == warehouse_for_cc.email

    shipping_zones = queried_warehouse["shippingZones"]["edges"]
    assert len(shipping_zones) == warehouse_for_cc.shipping_zones.count()
    queried_shipping_zone = shipping_zones[0]["node"]
    shipping_zone = warehouse_for_cc.shipping_zones.first()
    assert queried_shipping_zone["name"] == shipping_zone.name
    assert len(queried_shipping_zone["countries"]) == len(shipping_zone.countries)

    stocks = queried_warehouse["stocks"]["edges"]
    assert len(stocks) == warehouse_for_cc.stock_set.count()
    stock_ids = set(warehouse_for_cc.stock_set.values_list("id", flat=True))
    for stock in stocks:
        assert int(from_global_id_or_error(stock["node"]["id"])[1]) in stock_ids

    address = warehouse_for_cc.address
    queried_address = queried_warehouse["address"]
    assert queried_address["streetAddress1"] == address.street_address_1
    assert queried_address["postalCode"] == address.postal_code


def test_warehouse_query_as_staff_with_manage_orders(
    staff_api_client, warehouse_for_cc, permission_manage_orders
):
    # given
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse_for_cc.pk)

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE,
        variables={"id": warehouse_id},
        permissions=[permission_manage_orders],
    )

    # then
    content = get_graphql_content(response)

    queried_warehouse = content["data"]["warehouse"]
    assert queried_warehouse["name"] == warehouse_for_cc.name
    assert queried_warehouse["email"] == warehouse_for_cc.email

    shipping_zones = queried_warehouse["shippingZones"]["edges"]
    assert len(shipping_zones) == warehouse_for_cc.shipping_zones.count()
    queried_shipping_zone = shipping_zones[0]["node"]
    shipping_zone = warehouse_for_cc.shipping_zones.first()
    assert queried_shipping_zone["name"] == shipping_zone.name
    assert len(queried_shipping_zone["countries"]) == len(shipping_zone.countries)

    stocks = queried_warehouse["stocks"]["edges"]
    assert len(stocks) == warehouse_for_cc.stock_set.count()
    stock_ids = set(warehouse_for_cc.stock_set.values_list("id", flat=True))
    for stock in stocks:
        assert int(from_global_id_or_error(stock["node"]["id"])[1]) in stock_ids

    address = warehouse_for_cc.address
    queried_address = queried_warehouse["address"]
    assert queried_address["streetAddress1"] == address.street_address_1
    assert queried_address["postalCode"] == address.postal_code


def test_warehouse_query_as_staff_with_manage_shipping(
    staff_api_client, warehouse_for_cc, permission_manage_shipping
):
    # given
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse_for_cc.pk)

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE,
        variables={"id": warehouse_id},
        permissions=[permission_manage_shipping],
    )

    # then
    content = get_graphql_content(response)

    queried_warehouse = content["data"]["warehouse"]
    assert queried_warehouse["name"] == warehouse_for_cc.name
    assert queried_warehouse["email"] == warehouse_for_cc.email

    shipping_zones = queried_warehouse["shippingZones"]["edges"]
    assert len(shipping_zones) == warehouse_for_cc.shipping_zones.count()
    queried_shipping_zone = shipping_zones[0]["node"]
    shipping_zone = warehouse_for_cc.shipping_zones.first()
    assert queried_shipping_zone["name"] == shipping_zone.name
    assert len(queried_shipping_zone["countries"]) == len(shipping_zone.countries)

    stocks = queried_warehouse["stocks"]["edges"]
    assert len(stocks) == warehouse_for_cc.stock_set.count()
    stock_ids = set(warehouse_for_cc.stock_set.values_list("id", flat=True))
    for stock in stocks:
        assert int(from_global_id_or_error(stock["node"]["id"])[1]) in stock_ids

    address = warehouse_for_cc.address
    queried_address = queried_warehouse["address"]
    assert queried_address["streetAddress1"] == address.street_address_1
    assert queried_address["postalCode"] == address.postal_code


def test_warehouse_query_as_staff_with_manage_apps(
    staff_api_client, warehouse, permission_manage_apps
):
    # given
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE,
        variables={"id": warehouse_id},
        permissions=[permission_manage_apps],
    )

    # then
    assert_no_permission(response)


def test_warehouse_query_as_customer(user_api_client, warehouse):
    # given
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)

    # when
    response = user_api_client.post_graphql(
        QUERY_WAREHOUSE,
        variables={"id": warehouse_id},
    )

    # then
    assert_no_permission(response)


def test_staff_query_warehouse_by_invalid_id(
    staff_api_client, warehouse, permission_manage_shipping
):
    # given
    id = "bh/"
    variables = {"id": id}

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE, variables, permissions=[permission_manage_shipping]
    )

    # then
    content = get_graphql_content_from_response(response)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Invalid ID: {id}. Expected: Warehouse."
    assert content["data"]["warehouse"] is None


def test_staff_query_warehouse_with_invalid_object_type(
    staff_api_client, permission_manage_shipping, warehouse
):
    # given
    variables = {"id": graphene.Node.to_global_id("Order", warehouse.pk)}
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE, variables, permissions=[permission_manage_shipping]
    )

    # then
    content = get_graphql_content(response)
    assert content["data"]["warehouse"] is None


QUERY_WAREHOUSE_BY_EXTERNAL_REFERENCE = """
query warehouse($id: ID, $externalReference: String){
    warehouse(id: $id, externalReference: $externalReference) {
        id
        externalReference
    }
}
"""


def test_warehouse_query_by_external_reference(
    staff_api_client, warehouse, permission_manage_products
):
    # given
    ext_ref = "test-ext-ref"
    warehouse.external_reference = ext_ref
    warehouse.save(update_fields=["external_reference"])
    variables = {"externalReference": ext_ref}

    # when
    response = staff_api_client.post_graphql(
        QUERY_WAREHOUSE_BY_EXTERNAL_REFERENCE,
        variables=variables,
        permissions=[permission_manage_products],
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["warehouse"]
    assert data["externalReference"] == ext_ref
    assert data["id"] == graphene.Node.to_global_id("Warehouse", warehouse.id)
