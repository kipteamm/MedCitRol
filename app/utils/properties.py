from app.game.models import Character

import random
import math


class Properties:
    def __init__(self, character: Character) -> None:
        self._hunger = character.hunger
        self._fatigue = character.fatigue
        self._health = character.health
        self._happiness = character.happiness

    def hunger(self) -> str:
        if self._hunger < 1:
            return "starving"
        
        if self._hunger < 4:
            return "very hungry"
        
        if self._hunger < 8:
            return "hungry"
        
        if self._hunger < 12:
            return "little hungry"
        
        if self._hunger < 16:
            return "fed"
        
        if self._hunger <= 28:
            return "well fed"
        
        return "stuffed"
    
    def fatigue(self) -> str:
        if self._fatigue < 3:
            return "sleep deprived"

        if self._fatigue < 5:
            return "very tired"
        
        if self._fatigue < 7:
            return "tired"
        
        if self._fatigue < 12:
            return "little tired"
        
        if self._fatigue < 26:
            return "well and alert"
        
        if self._fatigue < 30:
            return "overslept"
        
        return "very overslept"
    
    def health(self) -> str:
        if self._health < 1:
            return "dead"

        if self._health < 3:
            return "near death"

        if self._health < 6:
            return "very ill"

        if self._health < 12:
            return "ill"

        if self._health < 15:
            return "little unwell"
        
        if self._health < 18:
            return "healthy"

        return "fit and healthy"
    
    def happiness(self) -> str:
        if self._happiness < 5:
            return "depressed"
        
        if self._happiness < 10:
            return "unhappy"
        
        if self._happiness < 15:
            return "dissatisfied"
        
        if self._happiness < 20:
            return "satisfied"
        
        if self._happiness < 25:
            return "happy"
        
        return "really happy"
    