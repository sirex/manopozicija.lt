from django.contrib.auth.decorators import user_passes_test


def superuser_required(func):
    decorator = user_passes_test(lambda u: (u.is_authenticated() and u.is_superuser))
    return decorator(func)
