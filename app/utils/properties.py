from app.game.models import Character

import math


class Properties:
    def __init__(self, character: Character) -> None:
        self._hunger = character.hunger
        self._fatigue = character.fatigue
        self._health = character.health
        self._happiness = character.happiness

    def hunger(self) -> str:
        if self._hunger < 4:
            return "starving"
        
        if self._hunger < 8:
            return "very hungry"
        
        if self._hunger < 12:
            return "hungry"
        
        if self._hunger < 16:
            return "fed"
        
        if self._hunger <= 28:
            return "well fed"
        
        return "stuffed"
    
    def fatigue(self) -> str:
        if self._fatigue < 3:
            return "severely sleep deprived"

        if self._fatigue < 6:
            return "sleep deprived"
        
        if self._fatigue < 10:
            return "very tired"
        
        if self._fatigue < 14:
            return "tired"
        
        if self._fatigue < 24:
            return "well and alert"
        
        if self._fatigue < 28:
            return "overslept"
        
        return "Very overslept"
    
    def health(self) -> str:
        if self._health < 0:
            return "near death"
        
        if self._health < 25:
            return "other health"
        
        return "healthy"
    
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
    
    def get_hours_of_sleep(self) -> int:
        return ((8 - self._fatigue) + 8) * 2
