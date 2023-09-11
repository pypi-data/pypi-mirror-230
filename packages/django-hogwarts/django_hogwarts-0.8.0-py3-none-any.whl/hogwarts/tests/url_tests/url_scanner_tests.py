from hogwarts.magic_urls.gen_urls import gen_path
from hogwarts.magic_urls.utils import extract_paths, append_path_to_urls_code


def test_it_extracts_paths():
    payload = """
urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("create/", PostCreateView.as_view(), name="create"),
    path("comment-confirm/", comment_confirm_view, name="comment_confirm")
]       
    """

    result = extract_paths(payload)

    assert result[0].path_name == "list"
    assert result[0].view == "PostListView"
    assert result[0].path_url == ""


def test_it_appends_paths():
    code = """
urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("create/", PostCreateView.as_view(), name="create"),
]    
    """

    expected = """
urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("create/", PostCreateView.as_view(), name="create"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail")
]"""

    class PostDetailView:
        pass

    path = gen_path(PostDetailView, "post")
    result = append_path_to_urls_code(code, path)

    assert result == expected
