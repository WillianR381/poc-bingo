import random 

maxNumbersBingo = 75
numberCards = 24

def randomNumber():
    return random.randint(1, maxNumbersBingo)


# Gera os numeros das carteals 
def generateNumberCards():
    random_numbers_cards = set()

    while (len(random_numbers_cards) < numberCards):
        _randomNumber = randomNumber()
        random_numbers_cards.add(_randomNumber)
        
    return random_numbers_cards
   

# Função que gera numero aleatorio no bingo
def randomNumberNotInsertedBingo(list_numbers):
    if len(list_numbers) >= maxNumbersBingo:
        return None
    
    while(True):
        random_number = randomNumber()
        if not str(random_number) in list_numbers:
            return random_number


# Verificar se 2 set são iguais 
def isRandomNumbersEqualsCard(randomNumbers1, randomNumbers2):
    return len(randomNumbers1.difference(randomNumbers2)) == 0


# Gera cartela única
# Parameters:
# list_drawn_numbers_sorted (list): Lista com os valores das cartelas sorteados 

def generateUniqueRandomNumbersCards(list_drawn_numbers_sorted):
    numbers_cards = generateNumberCards()
    numbers_cards = [str(item) for  item in numbers_cards ]

    if (not list_drawn_numbers_sorted ):
        return numbers_cards
    
    for drawns_numbers_sorted in list_drawn_numbers_sorted:
        if(isRandomNumbersEqualsCard(drawns_numbers_sorted, numbers_cards)):
            print('Igual')
            return generateUniqueRandomNumbersCards(list_drawn_numbers_sorted)
        
    return numbers_cards


def formatCardsResponse(drawn_numbers_sorted):
    formatted_drawn_numbers = {
        'b' : [],
        'i' : [],
        'n' : [],
        'g' : [],
        'o' : []
    }

    numbers = drawn_numbers_sorted.split(',')
    for number in numbers:
        number = int(number)
        print(number)
        if  number <=15 :
            formatted_drawn_numbers['b'].append(number)
        elif number <= 30:
            formatted_drawn_numbers['i'].append(number)
        elif number <= 45:
            formatted_drawn_numbers['n'].append(number)
        elif number <= 60:
            formatted_drawn_numbers['g'].append(number)
        elif number <= 75:
            formatted_drawn_numbers['o'].append(number)
    
    return formatted_drawn_numbers