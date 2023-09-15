from zs_utils.api.shopify.base_api import ShopifyAPI


class GetShopifyFulfillmentAPI(ShopifyAPI):
    """
    https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment#get-orders-order-id-fulfillments-fulfillment-id
    """

    http_method = "GET"
    resource_method = "orders/{order_id}/fulfillments/{fulfillment_id}.json"
    required_params = ["order_id", "fulfillment_id"]


class UpdateShopifyFulfillmentAPI(ShopifyAPI):
    """
    https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment#put-orders-order-id-fulfillments-fulfillment-id
    """

    http_method = "PUT"
    resource_method = "orders/{order_id}/fulfillments/{fulfillment_id}.json"
    payload_key = "fulfillment"
    required_params = ["order_id", "fulfillment_id", "tracking_number"]


class CreateShopifyFulfillmentAPI(ShopifyAPI):
    """
    https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment#post-orders-order-id-fulfillments
    """

    http_method = "POST"
    resource_method = "orders/{order_id}/fulfillments.json"
    payload_key = "fulfillment"
    required_params = [
        "order_id",
        "location_id",
        "line_items",
    ]
    allowed_params = [
        "name",
        "notify_customer",
        "origin_address",
        "receipt",
        "service",
        "shipment_status",
        "status",
        "variant_inventory_management",
        "tracking_company",
        "tracking_numbers",
        "tracking_urls",
    ]


class GetShopifyFulfillmentListAPI(ShopifyAPI):
    """
    https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment#get-orders-order-id-fulfillments
    """

    http_method = "GET"
    resource_method = "orders/{order_id}/fulfillments.json"
    required_params = ["order_id"]
    allowed_params = ["page_info"]
