from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.forms import inlineformset_factory
from .forms import OrderForm,CreateUserForm,CustomerForm
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users,admin_only
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
# Create your views here.

@unauthenticated_user
def registerPage(request):
	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			group = Group.objects.get(name='customer')
			user.groups.add(group)
			Customer.objects.create(user=user)

			messages.success(request, 'Account was created for ' + username)
			return redirect('login')

			# form.save()
			# user=form.cleaned_data.get('username')
			# messages.success(request,'Account was created for ' + user)
			# return redirect('login')

	context = {'form': form}
	return render(request, 'accounts/register.html', context)

#
# def registerPage(request):
# 	if request.user.is_authenticated:
# 		return redirect('home')
# 	else:
# 		form = CreateUserForm()
# 		if request.method == 'POST':
# 			form = CreateUserForm(request.POST)
# 			if form.is_valid():
# 				form.save()
# 				user = form.cleaned_data.get('username')
# 				messages.success(request, 'Account was created for ' + user)
#
# 				return redirect('login')
#
# 		context = {'form': form}
# 		return render(request, 'accounts/register.html', context)


# def loginPage(request):
	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	# 	if request.method == 'POST':
	# 		username = request.POST.get('username')
	# 		password = request.POST.get('password')
	#
	# 		user = authenticate(request, username=username, password=password)
	#
	# 		if user is not None:
	# 			login(request, user)
	# 			return redirect('home')
	# 		else:
	# 			messages.info(request, 'Username OR password is incorrect')

		# context = {}
		# return render(request, 'accounts/login.html', context)
@unauthenticated_user
def loginPage(request):
	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	if request.method=='POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		user=authenticate(request,username=username,password=password)
		if user is not None:
			login(request,user)
			return redirect('home')
		else:
			messages.info(request,'username or password is incorrect')

	# if request.user.is_authenticated:
	# 	return redirect('home')
	# else:
	# 	if request.method == 'POST':
	# 		username = request.POST.get('username')
	# 		password = request.POST.get('password')
	#
	# 		user = authenticate(request, username=username, password=password)
	#
	# 		if user is not None:
	# 			login(request, user)
	# 			return redirect('home')
	# 		else:
	# 			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'accounts/login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
#@allowed_users(allowed_roles=['adminm'])
@admin_only
def dashboard(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders': total_orders, 'delivered': delivered,
               'pending': pending}

    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['adminm'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products': products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['adminm'])
def customer(request, pk_test):
	customer = Customer.objects.get(id=pk_test)

	orders = customer.order_set.all()
	order_count = orders.count()

	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs

	context = {'customer':customer, 'orders':orders, 'order_count':order_count,
	'myFilter':myFilter}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
def main(request):
    return render(request,'accounts/main.html')

@login_required(login_url='login')
def navbar(request):
    return render(request,'accounts/navbar.html')

@login_required(login_url='login')
def status(request):
    return render(request,'accounts/status.html')


# def createOrder(request,pk):
#     customer=Customer.objects.get(id=pk)
#     form = OrderForm(initial={'customer':customer})
#     if request.method == 'POST':
#        form = OrderForm(request.POST, instance=customer)
#        if form.is_valid():
#            form.save()
#            return redirect('/')
#     context = {'form': form}
#     return render(request, 'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['adminm'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10 )
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'form':formset}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['adminm'])
def updateOrder(request, pk):

	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['adminm'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')

	context = {'item':order}
	return render(request, 'accounts/delete.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()

	context = {'orders': orders,
			   'total_orders': total_orders, 'delivered': delivered,
			   'pending': pending}


	print('ORDERS:',orders)
	#context = {'orders':orders}
	return render(request, 'accounts/user.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()


	context = {'form':form}
	return render(request, 'accounts/account_settings.html', context)