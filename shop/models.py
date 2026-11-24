
from django.db import models
from django.conf import settings


# ==================================================
# DANH MỤC SẢN PHẨM
# ==================================================

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tên danh mục"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mô tả danh mục"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"


# ==================================================
# SẢN PHẨM
# ==================================================

class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Tên sản phẩm"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Danh mục"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mô tả chi tiết"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá bán (VNĐ)"
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Ảnh sản phẩm"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày đăng"
    )

    def __str__(self):
        return self.name


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Khách hàng'
    )

    recipient_name = models.CharField(
        max_length=150,
        verbose_name='Tên người nhận'
    )

    phone = models.CharField(
        max_length=15,
        verbose_name='Số điện thoại'
    )

    address = models.TextField(
        verbose_name='Địa chỉ giao hàng'
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ghi chú'
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Tổng tiền'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày đặt hàng'
    )

    def __str__(self):
        return f"Đơn hàng #{self.id}"

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Đơn hàng'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Sản phẩm'
    )

    product_name = models.CharField(
        max_length=200,
        verbose_name='Tên sản phẩm'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Đơn giá tại thời điểm đặt hàng'
    )

    quantity = models.PositiveIntegerField(
        verbose_name='Số lượng'
    )

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'