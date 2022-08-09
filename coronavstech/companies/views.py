from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import CompanySerializer
from .models import Company


class CompanyViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by("-last_update")
    pagination_class = PageNumberPagination


@api_view(http_method_names=['POST'])
def send_company_email(request: Request) -> Response:
    """Sends email with request payload."""
    send_mail(
        subject=request.data.get('subject'),
        message=request.data.get('message'),
        from_email='test@gmail.com',
        recipient_list=['test@gmail.com']
    )
    return Response({'status': 'success', 'info': 'email sent successfully'}, status=200)


@api_view(http_method_names=['GET'])
def get_the_fibonacci_number(request: Request) -> Response:
    """Gets the n'th fibonacci number."""
    n = int(request.GET.get('n'))

    fib_lst = [0, 1]
    for i in range(1, n + 1):
        fib_lst.append(fib_lst[i] + fib_lst[i - 1])
    return Response({'fibonacci_number': f'{fib_lst[n]}'})



