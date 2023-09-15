from pyfiglet import Figlet

class Text():
    """Classe para formatar textos com cores e criar titulos com Figlet"""

    def __init__(self, content: str) -> None:
        self.text = content


    def clear() -> None:
        print("\033[H\033[2J\033[3J")


    def title(self, style="rozzo"):
        ascii = Figlet(font=style)
        arte = ascii.renderText(text=self.text)
        return Text(arte).blue()


    def red(self):
        return f"\033[1;31m{self.text}\033[0m"


    def blue(self):
        return f"\033[1;34m{self.text}\033[0m"


    def green(self):
        return f"\033[1;32m{self.text}\033[0m"


    def yellow(self):
        return f"\033[1;33m{self.text}\033[0m"


class Tools:
    def create_menu(lista: list) -> str:
        string = ""
        
        for c, item in enumerate(lista):
            string += f"[{c+1}] - {Text(item).green()}\n"
        
        return string
    
    def cpf_validate(numbers) -> bool:
        cpf = [int(char) for char in numbers if char.isdigit()]

        if len(cpf) != 11:
            return False

        if cpf == cpf[::-1]:
            return False

        for i in range(9, 11):
            value = sum((cpf[num] * ((i+1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != cpf[i]:
                return False
        return True