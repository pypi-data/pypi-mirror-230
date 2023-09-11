import secrets
import string


def gerar_senha(tamanho=6):
    if tamanho < 6:
        print("Tamanho da senha deve ser no mínimo 6.")
        return None

    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    for i in range(tamanho - 4):
        senha.append(secrets.choice(caracteres))

    secrets.SystemRandom().shuffle(senha)
    return ''.join(senha)