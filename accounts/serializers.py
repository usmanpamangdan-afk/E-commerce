from rest_framework import serializers
from .models import Address, Category,  Product,ProductImage,ProductVariant,ProductAttribute
from.models import AttributeValue,Inventory,StockMovement,Cart,CartItem
from .models import Wishlist, WishlistItem, Order, OrderItem, OrderStatusHistory
from .models import Payment, PaymentTransaction, Shipment, ShipmentTracking
from .models import Coupon, CouponUsage, Review, ProductRating


from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["id", "user"]
            



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    class Meta:
        model = Product
        fields = "__all__"
      


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"
        
class ProductVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = "__all__"
        read_only_fields = ["id", "product_name"]



class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = "__all__"
      

class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = "__all__"
       
class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="variant.product.name",
        read_only=True
    )

    class Meta:
        model = Inventory
        fields = "__all__"
        read_only_fields = ["id", "product_name"]
      

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = "__all__"
      
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ["id", "user"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"



class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        
class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = "__all__"
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "order_date",
            "total_amount",
            "status"
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10,decimal_places=2,min_value=0)

    class Meta:
        model = OrderItem
        fields = "__all__"
        


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"
        read_only_fields = [
            "id",
            "changed_at"
        ]

class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "id",
            "amount",
            "paid_at",
            "payment_status"
        ]
class PaymentTransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True
    )

    class Meta:
        model = PaymentTransaction
        fields = "__all__"
        read_only_fields = [
            "id",
            "amount",
            "created_at"
        ]

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = ["id","shipped_at", "delivered_at"]

class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = "__all__"
        read_only_fields = ["id","updated_at"]

        
class CouponSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.DecimalField( max_digits=5,decimal_places=2,min_value=0,max_value=100 )

    class Meta:
        model = Coupon
        fields = "__all__"


class CouponUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponUsage
        fields = "__all__"
        read_only_fields = ["used_at"]

class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5
    )

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "created_at"
        ]

class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = "__all__"
        read_only_fields = [
            "id",
            "average_rating",
            "total_reviews"
        ]