import pyfiglet
import colorama

class convert:
    def __init__(self, letter):
        self.letter = letter

    def toAcrobatic(self):
        return pyfiglet.figlet_format(self.letter, font='acrobatic')
    
    def toAlphabet(self):
        return pyfiglet.figlet_format(self.letter, 'alphabet')
    
    def toAvatar(self):
        return pyfiglet.figlet_format(self.letter, 'avatar')
    
    def toBlock(self):
        return pyfiglet.figlet_format(self.letter, 'block')
    
    def toCoinstak(self):
        return pyfiglet.figlet_format(self.letter, 'coinstak')
    
    def toBig(self):
        return pyfiglet.figlet_format(self.letter, 'big')
    
    def toFonteBraba(self, password=0):
        if password == 4678:
            return pyfiglet.figlet_format(self.letter, 'colossal')
        else:
            return print('A senha está incorreta meu chefe 😭')
    
    def toCustom(self, font='computer'):
        return pyfiglet.figlet_format(self.letter, font=font)

class syncronize:
    def __init__(self, vars):
        self.len = len(vars)
    
    def stylishM1(self):
        return '='*self.len
    
    def stylishM2(self):
        return '=*'*(self.len//2) + '='* (self.len % 2)
    
    def stylishM3(self):
        return '*'*self.len
    
    def stylishM4(self):
        return '-'*self.len
    
    def stylishM5(self):
        return '$'*self.len
    
    def stylishM6(self):
        return '&'*self.len
    
    def stylishCustom(self, t='Informe o estilo'):
        return t*self.len
    
def ShowAuthors():
    print(colorama.Fore.GREEN + colorama.Back.BLACK + pyfiglet.figlet_format('DesignForPy', 'colossal'))
    print('Criado pelo incrível Gustavo, que fez isso por não ter o que fazer', end='\n|    -> Feito com muito amor ebaaa\n')
    print('|    -> Package com grande compatibilidade com COLORAMA, TIME, DATATIME & Python Classic')
    print('|    -> Testado com Python 3.11.15, WIN11 & 8GBRAM.')