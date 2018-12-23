import unittest


class Animal(object):

    def speak(self):
        raise NotImplementedError


class Dog(Animal):

    def __init__(self, param1):
        self.param1 = param1

    def speak(self):
        return 'Bark' + ' ' + self.param1


class Cat(Animal):

    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def speak(self):
        return 'Meow' + ' ' + self.param1 + ' ' + self.param2


class AnimalFactory(object):

    _animal_classes = {}

    @classmethod
    def register(cls, id, animal_class):
        cls._animal_classes[id] = animal_class

    @classmethod
    def create_animal(cls, id):
        return cls._animal_classes[id]


class TestAnimalFactory(unittest.TestCase):

    def test_create_dog(self):
        AnimalFactory.register('Dog', Dog)
        AnimalFactory.register('Cat', Cat)

        dog = AnimalFactory.create_animal('Dog')('param1')
        actual = dog.speak()
        expected = 'Bark param1'
        self.assertEqual(expected, actual)

    def test_create_cat(self):
        AnimalFactory.register('Dog', Dog)
        AnimalFactory.register('Cat', Cat)

        cat = AnimalFactory.create_animal('Cat')('param1', 'param2')
        actual = cat.speak()
        expected = 'Meow param1 param2'
        self.assertEqual(expected, actual)

    def test_create_unregistered_animal(self):
        AnimalFactory.register('Dog', Dog)
        AnimalFactory.register('Cat', Cat)

        with self.assertRaises(KeyError):
            bird = AnimalFactory.create_animal('Bird')()



