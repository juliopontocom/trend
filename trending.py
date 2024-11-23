import requests
from bs4 import BeautifulSoup
import time
import json

# URL da página de criptomoedas em tendência
url = "https://coinmarketcap.com/trending-cryptocurrencies/"

# Cabeçalhos para a requisição
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Webhook do Discord
discord_webhook_url = "https://discord.com/api/webhooks/1309792697472651344/IWLxh0T_ss1ltzzzWiNSwYfaQvcfcOi4OjWx1HDwNggB0K0hb1OBrSs0qycytz8zRYIN"

# Nome do arquivo JSON para armazenamento
json_file = "trending_coins.json"

# Função para enviar mensagens ao Discord
def send_discord_message(message):
    payload = {"content": message}
    response = requests.post(discord_webhook_url, json=payload)
    if response.status_code == 204:
        print(f"Mensagem enviada: {message}")
    else:
        print(f"Erro ao enviar mensagem. Código de status: {response.status_code}")

# Função para buscar as moedas em tendência
def fetch_trending_coins():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", class_="cmc-table")
        if table:
            rows = table.find("tbody").find_all("tr")
            coins = []
            for row in rows:
                columns = row.find_all("td")
                if len(columns) >= 3:
                    name = columns[2].get_text(strip=True)  # Nome da moeda
                    coins.append(name)
            return coins
    return None

# Função para carregar o arquivo JSON
def load_previous_trending():
    try:
        with open(json_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Função para salvar as moedas no JSON
def save_current_trending(coins):
    with open(json_file, "w") as file:
        json.dump(coins, file, indent=4)

# Função principal para repetição e verificação
def main():
    print("Bot iniciado...")
    first_run = True  # Variável para identificar a primeira execução
    while True:
        print("Fazendo a requisição...")
        current_trending = fetch_trending_coins()
        if current_trending:
            # Carregar moedas anteriores do arquivo JSON
            previous_trending = load_previous_trending()

            if first_run:
                # Primeira execução: sempre printar as moedas
                print("Primeira execução. Moedas encontradas:")
                for coin in current_trending:
                    print(f"Moeda encontrada: {coin}")
                    send_discord_message(f"🔔 Primeira execução: Moeda encontrada: {coin}")
                    time.sleep(0.5)  # Delay entre mensagens
                save_current_trending(current_trending)
                first_run = False  # Alterar a flag para indicações subsequentes
            elif current_trending != previous_trending:
                # Detectar moedas novas
                new_coins = [coin for coin in current_trending if coin not in previous_trending]
                if new_coins:
                    print(f"Novas moedas detectadas: {', '.join(new_coins)}")
                    for coin in new_coins:
                        send_discord_message(f"🚀 Nova moeda detectada no Trending: {coin}")
                        time.sleep(0.5)  # Delay entre mensagens
                else:
                    print("Sem moedas novas, mas houve alguma alteração na ordem.")
                save_current_trending(current_trending)
            else:
                print("Nenhuma mudança detectada.")
                send_discord_message("✅ Nenhuma mudança detectada no Trending.")
        else:
            print("Falha ao buscar as moedas.")
            send_discord_message("⚠️ Falha ao buscar as moedas do Trending.")

        # Aguarda 1 minuto antes de verificar novamente
        time.sleep(60)

if __name__ == "__main__":
    main()
