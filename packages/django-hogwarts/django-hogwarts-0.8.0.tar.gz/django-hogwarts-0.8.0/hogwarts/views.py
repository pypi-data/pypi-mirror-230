from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Example


class ExampleListView(ListView):
    model = Example
    template_name = "list.html"
    context_object_name = "examples"


class ExampleCreateView(CreateView):
    model = Example
    fields = ["message"]
    template_name = "create.html"
    success_url = reverse_lazy("example:list")


class ExampleDetailView(DetailView):
    model = Example
    template_name = "detail.html"


class AddEqualSignView(UpdateView):
    model = Example
    fields = ["message"]

    def post(self, request, *args, **kwargs):
        obj: Example = self.get_object()
        obj.message = obj.message + "="
        obj.save()

        return redirect("example:list")
