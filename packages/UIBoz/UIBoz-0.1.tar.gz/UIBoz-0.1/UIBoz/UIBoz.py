import sys
import os

Running = True


# This is justa 
class InputFunctions:
    def __init__(self):
        pass
    
    def _update(self):
        pass

    def _ready(self):
        pass

class Frames:
    def __init__(self):
        self.Dictionary = {}
    
    def AddFrame(self, FrameName: list,  Frame: list) -> None:
        self.Dictionary[FrameName] = Frame
        
    @staticmethod
    def cls() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def DeleteFrame(self, FrameName: list) -> None:
        del self.Dictionary[FrameName]
    


class LifeTime:
    def __init__(self, Functions):
        # LOL, I used that not thingy that all vids say you should do
        
        if getattr(Functions, '_update', None) is None or getattr(Functions, '_ready', None) is None and not issubclass(Functions, InputFunctions):
            print("The Class Provided is not a valid Input Class")
            sys.exit(1)

        self.Functions = Functions()
    def Run(self):
        self.Functions._ready()

        while Running:
            self.Functions._update()
            
            