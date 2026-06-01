from django.views.generic import TemplateView
urlpatterns += [
    path('verify/', TemplateView.as_view(template_name='verify_code.html'), name='verify'),
]
