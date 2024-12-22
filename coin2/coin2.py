from pwn import *


def recv_game_header(shell):
    game_header_str = str(shell.recvline())
    print("Received game header:", game_header_str)
    return [int(x) for x in re.findall(r"\d+", game_header_str)]


def get_coin_sets(num_coins, num_chances):
    return [[coin for coin in range(num_coins) if coin & (2 ** i)] for i in range(num_chances)]


def get_weights_of_coin_sets(shell, coin_sets):
    guess_query = "-".join(" ".join(str(x) for x in s) for s in coin_sets)
    print("Sending line:", guess_query)
    shell.sendline(guess_query)
    weights = [int(x) for x in shell.recvline().split(b"-")]
    print("Received weights:", weights)
    return weights


def calculate_counterfeit_coin_index(weights):
    return sum(2 ** i for i in range(len(weights)) if weights[i] % 10 > 0)


def send_counterfeit_coin(shell, coin_index):
    print("Sending counterfeit coin:", coin_index)
    shell.sendline(str(coin_index))
    print("Result:", shell.recvline())


def play_single_game(shell):
    num_coins, num_chances = recv_game_header(shell)
    coin_sets = get_coin_sets(num_coins, num_chances)
    weights = get_weights_of_coin_sets(shell, coin_sets)
    coin_index = calculate_counterfeit_coin_index(weights)
    send_counterfeit_coin(shell, coin_index)


def main():
    shell = remote('localhost', 9008)
    shell.recvuntil("... -\n\t\n")
    for _ in range(100):
        play_single_game(shell)

    print(shell.recvline())
    print(shell.recvline())


if __name__ == '__main__':
    main()
