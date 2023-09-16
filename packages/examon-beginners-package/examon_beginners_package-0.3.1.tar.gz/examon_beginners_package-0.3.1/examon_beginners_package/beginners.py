from examon_core.examon_item import examon_item

REPOSITORY = 'examon_beginners_repo'


@examon_item(choices=[
    'Hello, Bob. How are you?', 'Hello, Jeff. How are you?',
    'Hello, Bob.', 'Hello, Jeff.', '. How are you?'],
    tags=['strings', 'beginner'], repository=REPOSITORY)
def question1():
    name = 'Jeff'
    name = 'Bob'
    greeting = f'Hello, {name}'
    greeting += ". How are you?"
    return greeting


@examon_item(choices=[
    'Hello', 'Hell',
    'Hello,', ['H', 'e', 'l', 'l', 'o']],
    tags=['strings', 'slicing', 'beginner'], repository=REPOSITORY)
def question2():
    greeting = 'Hello, how are you'
    return greeting[0:5]


@examon_item(choices=[
    'j', 'jk', 'ba'],
    tags=['strings', 'slicing', 'beginner'], repository=REPOSITORY)
def question3():
    letters = 'abcdefghijk'
    return letters[-2:]


@examon_item(choices=[
    'Hello, {name} you are {(23)}',
    'Hello, Bob you are (23)',
    'Hello, Bob you are 23'
],
    tags=['strings', 'interpolation', 'beginner'], repository=REPOSITORY)
def question4():
    name = 'Bob'
    return f'Hello, {name} you are {(23)}'


@examon_item(choices=[
    [True, True],
    [False, True],
    [True, False],
    [False, False],
], tags=['equality', 'dict', 'beginner'], repository=REPOSITORY)
def question5():
    my_object = {'name': 'bob'}
    new_ref = my_object
    return [
        my_object is new_ref,
        my_object is {'name': 'bob'}
    ]


@examon_item(choices=[
    ['the', 'cat', 'in', 'the', 'hat'], []
], tags=['array', 'for', 'if', 'beginner'], repository=REPOSITORY)
def question6():
    words = ['the', 'cat', 'in', 'the', 'hat']

    new_words = []
    for w in words:
        if (len(w) > 2):
            new_words.append(w)

    return new_words


@examon_item(choices=['15', '12345', '5'],
             tags=['for', 'range', 'beginner', '__add__'], repository=REPOSITORY)
def question7():
    x = 0
    for i in range(1, 5):
        x += i

    return x


@examon_item(choices=['10', '25', '5'],
             tags=['beginner', '__pow__'], repository=REPOSITORY)
def question8():
    return 5 ** 2


@examon_item(choices=['182.0', '37.0', '117.0', '182', '37', '117'],
             tags=['beginner', '__pow__'], repository=REPOSITORY)
def question9():
    return 36 / 4 * (3 + 2) * 4 + 2


@examon_item(choices=['Jam',
                      'dno',
                      'maJ',
                      'dnoB semaJ'],
             tags=['beginner', 'slicing'], repository=REPOSITORY)
def question10():
    var = "James Bond"
    return var[2::-1]


@examon_item(choices=['10', '20', '30'],
             tags=['beginner', ''], repository=REPOSITORY)
def question():
    p, q, r = 10, 20, 30
    return r


@examon_item(choices=['py', 'yn', 'pyn', 'yna'],
             tags=['beginner', 'slicing'], repository=REPOSITORY)
def question11():
    str = "pynative"
    return str[1:3]


@examon_item(choices=['CatCatCatCatCat', 'CatCatCatCatCatCat'],
             tags=['beginner', 'strings'], repository=REPOSITORY)
def question12():
    return "Cat" * 2 * 3


@examon_item(choices=[
    [False, False],
    [True, False],
    [False, True],
    [True, True],
],
    tags=['beginner', 'list'], repository=REPOSITORY)
def question13():
    list_one = [20, 40, 60, 80]
    list_two = [20, 40, 60, 80]

    return [list_one == list_two, list_one is list_two]


@examon_item(choices=[
    6, 3, 1
],
    tags=['beginner', 'dict'], repository=REPOSITORY)
def question14():
    my_dict = {'a': 1, 'b': 2, 'c': 3}
    return len(my_dict)


@examon_item(choices=[
    0, None
],
    tags=['beginner', 'dict'], repository=REPOSITORY)
def question15():
    my_dict = {'a': 1, 'b': 2, 'c': 3}
    return my_dict.get('d', 0)


@examon_item(choices=[
    [False, False],
    [True, False],
    [False, True],
    [True, True],
],
    tags=['beginner', 'dict'], repository=REPOSITORY)
def question16():
    my_dict = {'a': 1, 'b': 2, 'c': 3}
    items = my_dict.items()
    return [
        ('a', 1) in items,
        ['a', 1] in items
    ]


@examon_item(choices=[
    4, 5, None
],
    tags=['beginner', 'dict'], repository=REPOSITORY)
def question16():
    class Parent:
        def __init__(self):
            self.value = 4

    class Child(Parent):
        def __init__(self):
            self.value = 5

    child = Child()
    return child.value
