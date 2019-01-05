import unittest
from class_registry import ClassRegistry
from class_registry import RegistryKeyError

animal_registry = ClassRegistry()


class Animal(object):

    def speak(self):
        raise NotImplementedError


@animal_registry.register('dog')
class Dog(Animal):

    def __init__(self, param1):
        self.param1 = param1

    def speak(self):
        return 'Bark' + ' ' + self.param1

@animal_registry.register('cat')
class Cat(Animal):

    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def speak(self):
        return 'Meow' + ' ' + self.param1 + ' ' + self.param2


class TestAnimalRegistry(unittest.TestCase):

    def test_create_dog(self):
        dog = animal_registry.get('dog', 'param1')
        actual = dog.speak()
        expected = 'Bark param1'
        self.assertEqual(expected, actual)

    def test_create_cat(self):
        cat = animal_registry.get('cat', 'param1', 'param2')
        actual = cat.speak()
        expected = 'Meow param1 param2'
        self.assertEqual(expected, actual)

    def test_create_unregistered_animal(self):
        with self.assertRaises(RegistryKeyError):
            bird = animal_registry.get('bird')



