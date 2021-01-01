import gfl_test


import gfl.io.aspect as aspect


def pre_exec():
    print("PRE")


def post_exec():
    print("POST")


@aspect.Aspect(post_exec, position="after")
@aspect.Aspect(pre_exec, position="before")
def func():
    print("FUNC")


if __name__ == "__main__":
    func()

