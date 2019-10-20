from django.conf.urls import url
from products.views import UserProductHistoryView, UserProductHistoryView2
from .views import (
        AccountHomeView, 
        AccountEmailActivateView,
        UserDetailUpdateView
        )

app_name = 'accounts'

urlpatterns = [
    url(r'^$', AccountHomeView.as_view(), name='home'),
    url(r'^details/$', UserDetailUpdateView.as_view(), name='user-update'),
    url(r'history/products/$', UserProductHistoryView.as_view(), name='user-product-history'),
    url(r'history/products2/$', UserProductHistoryView2.as_view(), name='user-product-history2'),
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', 
            AccountEmailActivateView.as_view(), 
            name='email-activate'),
    url(r'^email/resend-activation/$', 
            AccountEmailActivateView.as_view(), 
            name='resend-activation'),
]

# account/email/confirm/asdfads/ -> activation view