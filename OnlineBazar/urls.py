from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_title="Online Bazar"
admin.site.site_header="Online Bazar"
# admin.site.site_url="Online Bazar"
from mainApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homePage),
    path('shop/<str:mc>/<str:sc>/<str:br>/',views.shopPage),
    path('login/',views.login),
    path('logout/',views.logout),
    path('signup/',views.signup),
    path('profile/',views.profilePage),
    path('updateProfile/',views.updateProfilePage),
    path('add-product/',views.addProduct),
    path('delete-product/<int:num>/',views.deleteProduct),
    path('edit-product/<int:num>/',views.editProduct),
    path('single-product-page/<int:num>/',views.singleProductPage),
    path('add-to-wishlist/<int:num>/',views.addToWishlist),
    path('delete-wishlist/<int:num>/',views.deleteWishlist),
    path('add-to-cart/',views.addTOCart),
    path('cart/',views.cartPage),
    path('update-cart/<str:id>/<str:num>/',views.updateCart),
    path('delete-cart/<str:id>/',views.deleteCart),
    path('checkout/',views.checkoutPage),
    path('confirmation/',views.confirmationPage),
    path('paymentSuccess/<str:rppid>/<str:rpoid>/<str:rpsid>/',views.paymentSuccess),
    path('paynow/<int:num>/',views.paynow),
    path('contact/',views.contactPage),
    path('forget-username/',views.forgetUsername),
    path('forget-otp/',views.forgetOTP),
    path('forget-password/',views.forgetPassword),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
