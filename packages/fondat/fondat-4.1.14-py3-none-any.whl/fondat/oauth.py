"""Fondat OAuth module."""


class OAuthScheme(Scheme):
    """
    ...

    Parameters:
    • scopes: all scopes that scheme supports
    """

    def __init__(self, scopes: set[str]):
        self.scope = scopes


class AuthorizationCodeOAuthScheme(OAuthScheme):
    def __init__(self, scopes: set[str]):
        super().__init__(scopes)
        self.flow = "implicit"


class ImplicitOAuthScheme(OAuthScheme):
    def __init__(self, scopes: set[str]):
        super().__init__(scopes)
        self.flow = "implicit"
