from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    # из какого класса брать форму
    form_class = CreationForm
    # куда перенаправить пользователя после успешной отправки формы
    success_url = reverse_lazy('posts:index')
    # имя шаблона, куда будет передана переменная form с объектом HTML-формы.
    # Всё это чем-то похоже на вызов функции render() во view-функции.
    template_name = 'users/signup.html'
