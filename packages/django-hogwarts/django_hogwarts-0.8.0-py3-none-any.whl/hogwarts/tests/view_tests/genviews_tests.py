from hogwarts.magic_views import ViewGenerator

from hogwarts.models import Article
from hogwarts.utils import code_strip


generator = ViewGenerator(Article)

def test_it_generates_detail_view():
    code = generator.detail()
    expected_code = """
    class ArticleDetailView(DetailView):
        model = Article
        context_object_name = "article"
        template_name = "articles/article_detail.html"
    """

    assert code_strip(code) == code_strip(expected_code)


def test_it_generates_list_view():
    code = generator.list()
    expected_code = """
    class ArticleListView(ListView):
        model = Article
        context_object_name = "articles"
        template_name = "articles/article_list.html"
    """

    assert code_strip(code) == code_strip(expected_code)


def test_it_generated_create_view():
    code = generator.create()
    expected_code = """
    class ArticleCreateView(CreateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_create.html"
        success_url = "/"
    """

    assert code_strip(code) == code_strip(expected_code)


def test_it_generated_update_view():
    code = generator.update()
    expected_code = """
    class ArticleUpdateView(UpdateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_update.html"
        success_url = "/"
    """

    assert code_strip(code) == code_strip(expected_code)


smart_generator = ViewGenerator(Article, smart_mode=True)


def test_smart_mode_create_view():
    code = smart_generator.create()
    expected_code = """
    class ArticleCreateView(LoginRequiredMixin, CreateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_create.html"
        success_url = "/"
        
        def form_valid(self, form):
            form.instance.author = self.request.user
            return super().form_valid(form)
    """

    assert code_strip(code) == code_strip(expected_code)


def test_smart_mode_update_view():
    code = smart_generator.update()
    expected_code = """
    class ArticleUpdateView(UserPassesTestMixin, UpdateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_update.html"
        success_url = "/"
        
        def test_func(self):
            return self.get_object() == self.request.user
    """

    assert code_strip(code) == code_strip(expected_code)


namespace_generator = ViewGenerator(Article, model_is_namespace=True)


def test_namespace_create_view():
    code = namespace_generator.create()
    expected_code = """
    class ArticleCreateView(CreateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_create.html"
    
        def get_success_url(self):
            return reverse("articles:detail", args=[self.object.id])
    """

    assert code_strip(code) == code_strip(expected_code)


def test_namespace_update_view():
    code = namespace_generator.update()
    expected_code = """
    class ArticleUpdateView(UpdateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_update.html"
        
        def get_success_url(self):
            return reverse("articles:detail", args=[self.get_object().id])
    """

    assert code_strip(code) == code_strip(expected_code)


def test_smart_mode_and_namespace_does_not_conflict():
    universal_generator = ViewGenerator(Article, smart_mode=True, model_is_namespace=True)
    code = universal_generator.create()

    expected_code = """
    class ArticleCreateView(LoginRequiredMixin, CreateView):
        model = Article
        fields = ["id", "title", "description", "beta"]
        template_name = "articles/article_create.html"
        
        def form_valid(self, form):
            form.instance.author = self.request.user
            return super().form_valid(form)

        def get_success_url(self):
            return reverse("articles:detail", args=[self.object.id])
    """

    assert code_strip(code) == code_strip(expected_code)
    assert "LoginRequiredMixin" in universal_generator.imports_generator.gen()

