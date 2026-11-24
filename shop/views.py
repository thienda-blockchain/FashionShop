# shop/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Order, OrderItem
from django.contrib.auth import login
from .forms import CustomerRegistrationForm
from functools import wraps
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# ==================================================
# PHÂN QUYỀN QUẢN TRỊ
# ==================================================

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # Nếu chưa đăng nhập, chuyển đến trang đăng nhập
        if not request.user.is_authenticated:
            return redirect('login')

        # Nếu đã đăng nhập nhưng không có quyền quản trị
        if not request.user.is_staff:
            return redirect('product_list')

        # Nếu có quyền quản trị, cho phép truy cập
        return view_func(request, *args, **kwargs)

    return wrapper



# ==================================================
# PHÂN HỆ KHÁCH HÀNG
# ==================================================

def product_list(request):
    categories = Category.objects.all().order_by('name')

    products = Product.objects.all().order_by('-created_at')

    category_id = request.GET.get('category')
    selected_category = None

    if category_id:
        selected_category = get_object_or_404(
            Category,
            id=category_id
        )
        products = products.filter(category=selected_category)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }

    return render(
        request,
        'shop/customer/index.html',
        context
    )


# ==================================================
# PHÂN HỆ QUẢN LÝ SẢN PHẨM
# ==================================================

@staff_required
def manager_product_list(request):
    products = Product.objects.all().order_by('-created_at')

    return render(
        request,
        'shop/manager/product_manage.html',
        {'products': products}
    )



@staff_required
def manager_add_product(request):

    # Lấy danh sách danh mục từ database
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':

        # Nhận dữ liệu từ form
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        category_id = request.POST.get('category')

        # Tìm danh mục được chọn
        category = get_object_or_404(Category, id=category_id)

        # Tạo sản phẩm mới
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            image=image,
            category=category
        )

        return redirect('manager_products')

    # Hiển thị form và danh sách danh mục
    return render(
        request,
        'shop/manager/product_add.html',
        {'categories': categories}
    )



@staff_required
def manager_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')

        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, id=category_id)

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        return redirect('manager_products')

    return render(request, 'shop/manager/product_edit.html', {
        'product': product,
        'categories': categories
    })

# ==================================================
# ĐĂNG KÝ TÀI KHOẢN KHÁCH HÀNG
# ==================================================

def register(request):

    # Nếu đã đăng nhập thì quay về trang chủ
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':

        # Nhận dữ liệu từ form
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():

            # Lưu tài khoản mới vào database
            user = form.save()

            # Tự động đăng nhập tài khoản vừa đăng ký
            login(request, user)

            # Chuyển về trang chủ
            return redirect('product_list')

    else:
        # Hiển thị form trống khi mới truy cập
        form = CustomerRegistrationForm()

    return render(
        request,
        'shop/customer/register.html',
        {'form': form}
    )

# ==================================================
# XÓA SẢN PHẨM
# ==================================================

@staff_required
def manager_delete_product(request, product_id):

    # Chỉ chấp nhận phương thức POST
    if request.method == 'POST':

        # Tìm sản phẩm theo ID
        product = get_object_or_404(Product, id=product_id)

        # Xóa sản phẩm
        product.delete()

        # Chuyển về danh sách sản phẩm
        return redirect('manager_products')

    # Nếu không phải POST thì quay lại danh sách
    return redirect('manager_products')



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        'shop/customer/product_detail.html',
        {'product': product}
    )


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # Lấy giỏ hàng từ Session
        cart = request.session.get('cart', {})

        # Lấy và kiểm tra số lượng
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        # Chuyển ID sản phẩm thành chuỗi
        product_id_str = str(product_id)

        # Cộng số lượng nếu sản phẩm đã có trong giỏ
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity

        # Lưu giỏ hàng vào Session
        request.session['cart'] = cart

        return redirect('product_detail', product_id=product_id)

    return redirect('product_list')


def view_cart(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    # Lưu lại các sản phẩm còn tồn tại
    valid_cart = {}

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        # Bỏ qua sản phẩm đã bị xóa
        if product is None:
            continue

        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

        valid_cart[str(product_id)] = quantity

    # Cập nhật lại giỏ hàng trong Session
    request.session['cart'] = valid_cart

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(
        request,
        'shop/customer/cart.html',
        context
    )


def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            try:
                quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                quantity = 1

            if quantity >= 1:
                cart[product_id_str] = quantity
            else:
                cart.pop(product_id_str)

            request.session['cart'] = cart

    return redirect('view_cart')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            del cart[product_id_str]

        request.session['cart'] = cart

    return redirect('view_cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    # Không cho thanh toán khi giỏ hàng trống
    if not cart:
        messages.warning(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('view_cart')

    # Lấy sản phẩm từ database
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        # Bỏ qua sản phẩm không còn tồn tại
        if product is None:
            continue

        quantity = int(quantity)

        if quantity < 1:
            continue

        subtotal = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

        total_price += subtotal

    if not cart_items:
        request.session['cart'] = {}
        messages.warning(request, 'Các sản phẩm trong giỏ hàng không còn tồn tại.')
        return redirect('view_cart')

    # Hiển thị giao diện thanh toán
    if request.method == 'GET':
        return render(request, 'shop/customer/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price
        })

    # Xử lý khi khách hàng xác nhận đặt hàng
    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        note = request.POST.get('note', '').strip()

        if not recipient_name or not phone or not address:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin nhận hàng.')
            return redirect('checkout')

        if len(phone) > 15:
            messages.error(request, 'Số điện thoại không hợp lệ.')
            return redirect('checkout')

        with transaction.atomic():

            # Tạo đơn hàng
            order = Order.objects.create(
                customer=request.user,
                recipient_name=recipient_name,
                phone=phone,
                address=address,
                note=note,
                total_price=total_price
            )

            # Tạo các chi tiết đơn hàng
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['product'].price,
                    quantity=item['quantity']
                )

        # Xóa giỏ hàng sau khi đặt hàng thành công
        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(
        request,
        'shop/customer/order_success.html',
        {'order': order}
    )



@login_required
def customer_order_list(request):
    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')

    return render(
        request,
        'shop/customer/order_list.html',
        {'orders': orders}
    )


@login_required
def customer_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        customer=request.user
    )

    order_items = order.items.all()

    return render(
        request,
        'shop/customer/order_detail.html',
        {
            'order': order,
            'order_items': order_items
        }
    )


@staff_required
def manager_order_list(request):

    orders = Order.objects.all().order_by('-created_at')

    return render(
        request,
        'shop/manager/order_list.html',
        {'orders': orders}
    )

@staff_required
def manager_order_detail(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    order_items = order.items.all()

    return render(
        request,
        'shop/manager/order_detail.html',
        {
            'order': order,
            'order_items': order_items
        }
    )


@staff_required
def update_order_status(request, order_id):

    if request.method != 'POST':
        return redirect('manager_order_detail', order_id=order_id)

    new_status = request.POST.get('status')

    # Chỉ cho phép xác nhận hoặc hủy đơn hàng
    if new_status not in ['confirmed', 'cancelled']:
        messages.error(request, 'Trạng thái đơn hàng không hợp lệ.')
        return redirect('manager_order_detail', order_id=order_id)

    with transaction.atomic():

        # Khóa bản ghi trong quá trình xử lý
        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id
        )

        # Chỉ xử lý đơn đang chờ xác nhận
        if order.status != 'pending':

            messages.error(
                request,
                'Đơn hàng này đã được xử lý, không thể thay đổi trạng thái.'
            )

        else:

            order.status = new_status
            order.save(update_fields=['status'])

            messages.success(
                request,
                f'Đã cập nhật trạng thái đơn hàng #{order.id}.'
            )

    return redirect('manager_order_detail', order_id=order_id)