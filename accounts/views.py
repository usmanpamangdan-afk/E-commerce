

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from django.core.paginator import Paginator
from django.db.models import Q


from .models import (
    Address,
    Category,
    Product,
    ProductImage,
    ProductVariant,
    ProductAttribute,
    AttributeValue,
    Inventory,
    StockMovement,
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentTransaction,
    Shipment,
    ShipmentTracking,
    Coupon,
    CouponUsage,
    Review,
    ProductRating,
)

from .serializers import (
    AddressSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    ProductVariantSerializer,
    ProductAttributeSerializer,
    AttributeValueSerializer,
    InventorySerializer,
    StockMovementSerializer,
    CartSerializer,
    CartItemSerializer,
    WishlistSerializer,
    WishlistItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderStatusHistorySerializer,
    PaymentSerializer,
    PaymentTransactionSerializer,
    ShipmentSerializer,
    ShipmentTrackingSerializer,
    CouponSerializer,
    CouponUsageSerializer,
    ReviewSerializer,
    ProductRatingSerializer
)



class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class AddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            address = Address.objects.get(pk=pk, user=request.user)
            serializer = AddressSerializer(address)
            return Response(serializer.data)

        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid():
            address = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        address = Address.objects.get(pk=pk, user=request.user)

        serializer = AddressSerializer(
            address,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = Address.objects.get(pk=pk, user=request.user)
        address.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)

        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        category = Category.objects.get(pk=pk)

        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        category = Category.objects.get(pk=pk)
        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):

        # Get single product
        if pk:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)

        products = Product.objects.all()

        # Search
        search = request.query_params.get("search")

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # Category filter
        category = request.query_params.get("category")

        if category:
            products = products.filter(
                category_id=category
            )

        # Minimum price filter
        min_price = request.query_params.get("min_price")

        if min_price:
            products = products.filter(
                price__gte=min_price
            )

        # Maximum price filter
        max_price = request.query_params.get("max_price")

        if max_price:
            products = products.filter(
                price__lte=max_price
            )

        # Sorting
        ordering = request.query_params.get("ordering")

        if ordering in [
            "price",
            "-price",
            "name",
            "-name"
        ]:
            products = products.order_by(ordering)

        # Pagination
        page = request.query_params.get("page", 1)

        paginator = Paginator(products, 3)

        try:
            page_number = int(page)

            if page_number < 1:
                raise ValueError

        except ValueError:
            return Response(
                {"detail": "Invalid page number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        page_obj = paginator.get_page(page_number)

        serializer = ProductSerializer(
            page_obj.object_list,
            many=True
        )

        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "results": serializer.data
        })

    def post(self, request):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create products."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update products."},
                status=status.HTTP_403_FORBIDDEN
            )

        product = Product.objects.get(pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete products."},
                status=status.HTTP_403_FORBIDDEN
            )

        product = Product.objects.get(pk=pk)

        product.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )



class ProductImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            image = ProductImage.objects.get(pk=pk)
            serializer = ProductImageSerializer(image)
            return Response(serializer.data)

        images = ProductImage.objects.all()
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can add product images."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductImageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update product images."},
                status=status.HTTP_403_FORBIDDEN
            )

        image = ProductImage.objects.get(pk=pk)

        serializer = ProductImageSerializer(
            image,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete product images."},
                status=status.HTTP_403_FORBIDDEN
            )

        image = ProductImage.objects.get(pk=pk)
        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductVariantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            variant = ProductVariant.objects.get(pk=pk)
            serializer = ProductVariantSerializer(variant)
            return Response(serializer.data)

        variants = ProductVariant.objects.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create product variants."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductVariantSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update product variants."},
                status=status.HTTP_403_FORBIDDEN
            )

        variant = ProductVariant.objects.get(pk=pk)

        serializer = ProductVariantSerializer(
            variant,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete product variants."},
                status=status.HTTP_403_FORBIDDEN
            )

        variant = ProductVariant.objects.get(pk=pk)
        variant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class ProductAttributeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            attribute = ProductAttribute.objects.get(pk=pk)
            serializer = ProductAttributeSerializer(attribute)
            return Response(serializer.data)

        attributes = ProductAttribute.objects.all()
        serializer = ProductAttributeSerializer(attributes, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create product attributes."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductAttributeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update product attributes."},
                status=status.HTTP_403_FORBIDDEN
            )

        attribute = ProductAttribute.objects.get(pk=pk)

        serializer = ProductAttributeSerializer(
            attribute,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete product attributes."},
                status=status.HTTP_403_FORBIDDEN
            )

        attribute = ProductAttribute.objects.get(pk=pk)
        attribute.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AttributeValueAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            value = AttributeValue.objects.get(pk=pk)
            serializer = AttributeValueSerializer(value)
            return Response(serializer.data)

        values = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(values, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create attribute values."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AttributeValueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update attribute values."},
                status=status.HTTP_403_FORBIDDEN
            )

        value = AttributeValue.objects.get(pk=pk)

        serializer = AttributeValueSerializer(
            value,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete attribute values."},
                status=status.HTTP_403_FORBIDDEN
            )

        value = AttributeValue.objects.get(pk=pk)
        value.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class InventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            inventory = Inventory.objects.get(pk=pk)
            serializer = InventorySerializer(inventory)
            return Response(serializer.data)

        inventories = Inventory.objects.all()
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create inventory."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InventorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update inventory."},
                status=status.HTTP_403_FORBIDDEN
            )

        inventory = Inventory.objects.get(pk=pk)

        serializer = InventorySerializer(
            inventory,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete inventory."},
                status=status.HTTP_403_FORBIDDEN
            )

        inventory = Inventory.objects.get(pk=pk)
        inventory.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class StockMovementAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            movement = StockMovement.objects.get(pk=pk)
            serializer = StockMovementSerializer(movement)
            return Response(serializer.data)

        movements = StockMovement.objects.all()
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create stock movements."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StockMovementSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update stock movements."},
                status=status.HTTP_403_FORBIDDEN
            )

        movement = StockMovement.objects.get(pk=pk)

        serializer = StockMovementSerializer(
            movement,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete stock movements."},
                status=status.HTTP_403_FORBIDDEN
            )

        movement = StockMovement.objects.get(pk=pk)
        movement.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            cart = Cart.objects.get(pk=pk, user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        carts = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
    def post(self, request):
        cart = Cart.objects.create(user=request.user)

        serializer = CartSerializer(cart)

        return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )

    def patch(self, request, pk):
        cart = Cart.objects.get(pk=pk, user=request.user)

        serializer = CartSerializer(
            cart,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        cart = Cart.objects.get(pk=pk, user=request.user)
        cart.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            item = CartItem.objects.get(pk=pk,cart__user=request.user )
            serializer = CartItemSerializer(item)
            return Response(serializer.data)

        items = CartItem.objects.filter(cart__user=request.user)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            item = serializer.save()

            if item.cart.user != request.user:
                item.delete()
                return Response(
                    {
                        "detail": "You cannot create an item for another user's cart."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        item = CartItem.objects.get(pk=pk,cart__user=request.user)

        serializer = CartItemSerializer(item,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        item = CartItem.objects.get(
            pk=pk,
            cart__user=request.user
        )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            wishlist = Wishlist.objects.get(
                pk=pk,
                user=request.user
            )
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)

        wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        wishlist = Wishlist.objects.create(user=request.user)

        serializer = WishlistSerializer(wishlist)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def patch(self, request, pk):
        wishlist = Wishlist.objects.get(
            pk=pk,
            user=request.user
        )

        serializer = WishlistSerializer(
            wishlist,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        wishlist = Wishlist.objects.get(
            pk=pk,
            user=request.user
        )

        wishlist.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    

class WishlistItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            item = WishlistItem.objects.get(
                pk=pk,
                wishlist__user=request.user
            )
            serializer = WishlistItemSerializer(item)
            return Response(serializer.data)

        items = WishlistItem.objects.filter(
            wishlist__user=request.user
        )
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WishlistItemSerializer(data=request.data)

        if serializer.is_valid():
            item = serializer.save()

            if item.wishlist.user != request.user:
                item.delete()
                return Response(
                    {
                        "detail": "You cannot create an item for another user's wishlist."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        item = WishlistItem.objects.get(
            pk=pk,
            wishlist__user=request.user
        )

        serializer = WishlistItemSerializer(
            item,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        item = WishlistItem.objects.get(
            pk=pk,
            wishlist__user=request.user
        )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)

        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
         return Response(
            {"detail": "Cart not found."},
            status=status.HTTP_400_BAD_REQUEST
        )

        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
         return Response(
            {"detail": "Your cart is empty."},
            status=status.HTTP_400_BAD_REQUEST
        )

        total_amount = 0

        for item in cart_items:
         inventory = Inventory.objects.filter(
            variant=item.variant
        ).first()

        if not inventory:
            return Response(
                {
                    "detail": f"No inventory found for variant {item.variant.id}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if inventory.stock_quantity < item.quantity:
            return Response(
                {
                    "detail": f"Insufficient stock for variant {item.variant.id}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount += (
            item.variant.product.price * item.quantity
        )

    # Coupon
        coupon = None
        coupon_code = request.data.get("coupon_code")

        if coupon_code:
         coupon = Coupon.objects.filter(
            code=coupon_code,
            is_active=True
        ).first()

        if not coupon:
            return Response(
                {"detail": "Invalid or inactive coupon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if coupon.expiry_date < timezone.now():
            return Response(
                {"detail": "Coupon has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if CouponUsage.objects.filter(
            coupon=coupon,
            user=request.user
        ).exists():
            return Response(
                {"detail": "You have already used this coupon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = (
            total_amount * coupon.discount_percentage / 100
        )

        total_amount = total_amount - discount

        with transaction.atomic():

            order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status="pending"
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.product.price
            )

            inventory = Inventory.objects.get(
                variant=item.variant
            )

            inventory.stock_quantity -= item.quantity
            inventory.save()

        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                user=request.user,
                order=order
            )

        cart_items.delete()

        serializer = OrderSerializer(order)

        return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


    
    def patch(self, request, pk):
     order = Order.objects.get(pk=pk)

     if not request.user.is_staff:
        return Response(
            {"detail": "Only admin can update order status."},
            status=status.HTTP_403_FORBIDDEN
        )

     if "status" not in request.data:
        return Response(
            {"detail": "Status is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

     order.status = request.data["status"]
     order.save()

     serializer = OrderSerializer(order)

     return Response(serializer.data)


    def delete(self, request, pk):
        order = Order.objects.get(pk=pk, user=request.user)
        order.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    
class OrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            item = OrderItem.objects.get(
                pk=pk,
                order__user=request.user
            )
            serializer = OrderItemSerializer(item)
            return Response(serializer.data)

        items = OrderItem.objects.filter(
            order__user=request.user
        )
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderItemSerializer(data=request.data)

        if serializer.is_valid():
            item = serializer.save()

            if item.order.user != request.user:
                item.delete()
                return Response(
                    {"detail": "You cannot create an item for another user's order."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        item = OrderItem.objects.get(
            pk=pk,
            order__user=request.user
        )

        serializer = OrderItemSerializer(
            item,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        item = OrderItem.objects.get(
            pk=pk,
            order__user=request.user
        )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class OrderStatusHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            history = OrderStatusHistory.objects.get(
                pk=pk,
                order__user=request.user
            )
            serializer = OrderStatusHistorySerializer(history)
            return Response(serializer.data)

        histories = OrderStatusHistory.objects.filter(
            order__user=request.user
        )
        serializer = OrderStatusHistorySerializer(histories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderStatusHistorySerializer(data=request.data)

        if serializer.is_valid():
            history = serializer.save()

            if history.order.user != request.user:
                history.delete()
                return Response(
                    {
                        "detail": "You cannot create history for another user's order."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        history = OrderStatusHistory.objects.get(
            pk=pk,
            order__user=request.user
        )

        serializer = OrderStatusHistorySerializer(
            history,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        history = OrderStatusHistory.objects.get(
            pk=pk,
            order__user=request.user
        )

        history.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            payment = Payment.objects.get(
                pk=pk,
                order__user=request.user
            )

            serializer = PaymentSerializer(payment)

            return Response(serializer.data)

        payments = Payment.objects.filter(
            order__user=request.user
        )

        serializer = PaymentSerializer(
            payments,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(
            data=request.data
        )

        if serializer.is_valid():
            order = serializer.validated_data["order"]

            if order.user != request.user:
                return Response(
                    {
                        "detail": "You cannot create payment for another user's order."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            payment = serializer.save(
                amount=order.total_amount
            )

            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def patch(self, request, pk):
        payment = Payment.objects.get(pk=pk)

        if not request.user.is_staff:
         return Response(
            {"detail": "Only admin can update payment."},
            status=status.HTTP_403_FORBIDDEN
        )

        if "payment_status" not in request.data:
         return Response(
            {"detail": "Payment status is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

        with transaction.atomic():

         payment.payment_status = request.data["payment_status"]
         payment.save()

        if payment.payment_status == "paid":
            payment.order.status = "confirmed"
            payment.order.save()

            serializer = PaymentSerializer(payment)

        return Response(serializer.data)

    def delete(self, request, pk):
        payment = Payment.objects.get(
            pk=pk,
            order__user=request.user
        )

        payment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class PaymentTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            transaction = PaymentTransaction.objects.filter(
                pk=pk
            ).first()

            if not transaction:
                return Response(
                    {"detail": "Payment transaction not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if (
                transaction.payment.order.user != request.user
                and not request.user.is_staff
            ):
                return Response(
                    {
                        "detail": "You cannot view another user's payment transaction."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = PaymentTransactionSerializer(transaction)
            return Response(serializer.data)

        if request.user.is_staff:
            transactions = PaymentTransaction.objects.all()
        else:
            transactions = PaymentTransaction.objects.filter(
                payment__order__user=request.user
            )

        serializer = PaymentTransactionSerializer(
            transactions,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentTransactionSerializer(
            data=request.data
        )

        if serializer.is_valid():
            payment = serializer.validated_data["payment"]

            if (
                payment.order.user != request.user
                and not request.user.is_staff
            ):
                return Response(
                    {
                        "detail": "You cannot create a transaction for another user's payment."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            transaction = serializer.save(
                amount=payment.amount
            )

            return Response(
                PaymentTransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        transaction = PaymentTransaction.objects.filter(
            pk=pk
        ).first()

        if not transaction:
            return Response(
                {"detail": "Payment transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            transaction.payment.order.user != request.user
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": "You cannot update another user's payment transaction."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaymentTransactionSerializer(
            transaction,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        transaction = PaymentTransaction.objects.filter(
            pk=pk
        ).first()

        if not transaction:
            return Response(
                {"detail": "Payment transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            transaction.payment.order.user != request.user
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": "You cannot delete another user's payment transaction."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        transaction.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    
class ShipmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            shipment = Shipment.objects.get(
                pk=pk,
                order__user=request.user
            )

            serializer = ShipmentSerializer(shipment)

            return Response(serializer.data)

        shipments = Shipment.objects.filter(
            order__user=request.user
        )

        serializer = ShipmentSerializer(
            shipments,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin can create shipment."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ShipmentSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.validated_data["order"]

            if order.status != "confirmed":
                return Response(
                    {
                        "detail": "Shipment can only be created for a confirmed order."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Shipment.objects.filter(order=order).exists():
                return Response(
                    {
                        "detail": "Shipment already exists for this order."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            shipment = serializer.save()

            return Response(
                ShipmentSerializer(shipment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin can update shipment."},
                status=status.HTTP_403_FORBIDDEN
            )

        shipment = Shipment.objects.get(pk=pk)

        if "shipment_status" not in request.data:
            return Response(
                {"detail": "Shipment status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data["shipment_status"]

        if new_status not in ["pending", "shipped", "delivered", "cancelled"]:
            return Response(
                {"detail": "Invalid shipment status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            shipment.shipment_status = new_status

            if new_status == "shipped":
                shipment.shipped_at = timezone.now()

            elif new_status == "delivered":
                shipment.delivered_at = timezone.now()

                shipment.order.status = "delivered"
                shipment.order.save()

            elif new_status == "cancelled":
                shipment.order.status = "cancelled"
                shipment.order.save()

            shipment.save()

        serializer = ShipmentSerializer(shipment)

        return Response(serializer.data)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin can delete shipment."},
                status=status.HTTP_403_FORBIDDEN
            )

        shipment = Shipment.objects.get(pk=pk)
        shipment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShipmentTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            tracking = ShipmentTracking.objects.filter(
                pk=pk
            ).first()

            if not tracking:
                return Response(
                    {"detail": "Shipment tracking not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if tracking.shipment.order.user != request.user and not request.user.is_staff:
                return Response(
                    {
                        "detail": "You cannot view another user's shipment tracking."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ShipmentTrackingSerializer(tracking)
            return Response(serializer.data)

        tracking = ShipmentTracking.objects.filter(
            shipment__order__user=request.user
        )

        if request.user.is_staff:
            tracking = ShipmentTracking.objects.all()

        serializer = ShipmentTrackingSerializer(
            tracking,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = ShipmentTrackingSerializer(
            data=request.data
        )

        if serializer.is_valid():
            shipment = serializer.validated_data["shipment"]

            if shipment.order.user != request.user and not request.user.is_staff:
                return Response(
                    {
                        "detail": "You cannot create tracking for another user's shipment."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            tracking = serializer.save()

            return Response(
                ShipmentTrackingSerializer(tracking).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        tracking = ShipmentTracking.objects.filter(
            pk=pk
        ).first()

        if not tracking:
            return Response(
                {"detail": "Shipment tracking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if tracking.shipment.order.user != request.user and not request.user.is_staff:
            return Response(
                {
                    "detail": "You cannot update another user's shipment tracking."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ShipmentTrackingSerializer(
            tracking,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        tracking = ShipmentTracking.objects.filter(
            pk=pk
        ).first()

        if not tracking:
            return Response(
                {"detail": "Shipment tracking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if tracking.shipment.order.user != request.user and not request.user.is_staff:
            return Response(
                {
                    "detail": "You cannot delete another user's shipment tracking."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        tracking.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class CouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            coupon = Coupon.objects.get(pk=pk)
            serializer = CouponSerializer(coupon)
            return Response(serializer.data)

        coupons = Coupon.objects.all()
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create coupons."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CouponSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update coupons."},
                status=status.HTTP_403_FORBIDDEN
            )

        coupon = Coupon.objects.get(pk=pk)

        serializer = CouponSerializer(
            coupon,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete coupons."},
                status=status.HTTP_403_FORBIDDEN
            )

        coupon = Coupon.objects.get(pk=pk)
        coupon.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class CouponUsageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            usage = CouponUsage.objects.get(
                pk=pk,
                user=request.user
            )
            serializer = CouponUsageSerializer(usage)
            return Response(serializer.data)

        usages = CouponUsage.objects.filter(
            user=request.user
        )
        serializer = CouponUsageSerializer(usages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CouponUsageSerializer(data=request.data)

        if serializer.is_valid():
            usage = serializer.save()

            if usage.user != request.user:
                usage.delete()
                return Response(
                    {
                        "detail": "You cannot create coupon usage for another user."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        usage = CouponUsage.objects.get(
            pk=pk,
            user=request.user
        )

        serializer = CouponUsageSerializer(
            usage,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        usage = CouponUsage.objects.get(
            pk=pk,
            user=request.user
        )

        usage.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    
class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            review = Review.objects.get(pk=pk)

            serializer = ReviewSerializer(review)

            return Response(serializer.data)

        product_id = request.query_params.get("product")

        if product_id:
            reviews = Review.objects.filter(
                product_id=product_id
            )
        else:
            reviews = Review.objects.filter(
                user=request.user
            )

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(
            data=request.data
        )

        if serializer.is_valid():
            product = serializer.validated_data["product"]

            # Check whether user purchased this product
            purchased = OrderItem.objects.filter(
                order__user=request.user,
                variant__product=product
            ).exists()

            if not purchased:
                return Response(
                    {
                        "detail": "You can only review a product you purchased."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prevent duplicate reviews
            if Review.objects.filter(
                user=request.user,
                product=product
            ).exists():
                return Response(
                    {
                        "detail": "You have already reviewed this product."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            review = serializer.save(
                user=request.user
            )

            self.update_product_rating(product)

            return Response(
                ReviewSerializer(review).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        review = Review.objects.get(pk=pk)

        if review.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You cannot update this review."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(
            review,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            review = serializer.save()

            self.update_product_rating(review.product)

            return Response(
                ReviewSerializer(review).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        review = Review.objects.get(pk=pk)

        if review.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You cannot delete this review."},
                status=status.HTTP_403_FORBIDDEN
            )

        product = review.product

        review.delete()

        self.update_product_rating(product)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def update_product_rating(self, product):
        reviews = Review.objects.filter(product=product)

        total_reviews = reviews.count()

        if total_reviews > 0:
            total_rating = sum(
                review.rating for review in reviews
            )

            average_rating = (
                total_rating / total_reviews
            )
        else:
            average_rating = 0

        ProductRating.objects.update_or_create(
            product=product,
            defaults={
                "average_rating": average_rating,
                "total_reviews": total_reviews
            }
        )



class ProductRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            rating = ProductRating.objects.get(pk=pk)
            serializer = ProductRatingSerializer(rating)
            return Response(serializer.data)

        ratings = ProductRating.objects.all()
        serializer = ProductRatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can create product ratings."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductRatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update product ratings."},
                status=status.HTTP_403_FORBIDDEN
            )

        rating = ProductRating.objects.get(pk=pk)

        serializer = ProductRatingSerializer(
            rating,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete product ratings."},
                status=status.HTTP_403_FORBIDDEN
            )

        rating = ProductRating.objects.get(pk=pk)
        rating.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)