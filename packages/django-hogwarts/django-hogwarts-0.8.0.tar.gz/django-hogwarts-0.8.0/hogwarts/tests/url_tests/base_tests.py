from hogwarts.magic_urls.base import get_path_url


def test_get_path_url():
    assert get_path_url("list", "none", False) == ""
    assert get_path_url("detail", "none", True) == "<int:pk>/"
    assert get_path_url("like", "none", True) == "<int:pk>/like/"
    assert get_path_url("post_detail", "Post", True) == "posts/<int:pk>/"
    assert get_path_url("post_create", "Post", False) == "posts/create/"
    assert get_path_url("post_remove_likes", "Post", False) == "posts/remove-likes/"
    assert get_path_url("post_like", "Post", True) == "posts/<int:pk>/like/"
    assert get_path_url("post_list", "Post", False) == "posts/"

