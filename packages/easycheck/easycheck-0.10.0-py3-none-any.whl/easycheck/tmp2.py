from functools import singledispatch

class X:
    @singledispatch
    @staticmethod
    def foo(arg) -> None:
        print("Nie pasuje to co dałeś")
    
    @foo.register
    @staticmethod
    def _(arg: str) -> None:
        print("Dałeś stringa")
    
    @foo.register
    @staticmethod
    def _(arg: int) -> None:
        print("Dałeś inta!")


x = X()
x.foo("dupsko")
x.foo(210)
x.foo(1.1)
