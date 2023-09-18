
class Hello:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("file name:", __name__)
        return ("author: " + self.name,
                "age: 30"
                )

