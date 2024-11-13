from django.urls import reverse_lazy

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('index')