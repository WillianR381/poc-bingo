import random 

maxNumbersBingo = 75

numberCards = 25
    
def generateNumberCards():
    random_numbers_cards = set()


    while (len(random_numbers_cards) < numberCards):
        randomNumber = randomNumber()
        random_numbers_cards.add(randomNumber)
        
    #isEquals = len(random_numbers_cards.difference(random_numbers_cards)) == 0
    return random_numbers_cards
   

def randomNumber():
    return random.randint(1, maxNumbersBingo)


def randomNumberNotInserted(list_numbers):
    if len(list_numbers) >= maxNumbersBingo:
        return None
    
    print(list_numbers)
    while(True):
        random_number = randomNumber()
        if not str(random_number) in list_numbers:
            return random_number
