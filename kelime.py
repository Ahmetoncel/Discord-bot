import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from datetime import datetime
from discord.ui import Button, View
from coin_config import coin_behaviors

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'data.json'

# Dosya işlemleri
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_bakiye(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get('bakiye', 0)

def update_bakiye(user_id, amount):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"bakiye": 10000, "won": 0, "lost": 0}
    data[uid]['bakiye'] += amount
    save_data(data)

def update_stats(user_id, won=False, lost=False):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {"bakiye": 10000, "won": 0, "lost": 0}

    if "won" not in data[uid]:
        data[uid]["won"] = 0
    if "lost" not in data[uid]:
        data[uid]["lost"] = 0

    if won:
        data[uid]["won"] += 1
    if lost:
        data[uid]["lost"] += 1

    save_data(data)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Günlük ödül
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    today = datetime.now().strftime('%Y-%m-%d')

    if user_id not in data:
        data[user_id] = {"bakiye": 10000, "last_daily": "1900-01-01", "won": 0, "lost": 0}

    last_claim = data[user_id].get("last_daily", "1900-01-01")

    if last_claim == today:
        return await ctx.send(f"{ctx.author.mention}, bugün zaten günlük ödülünü aldın! Aç köpek 🕒")

    data[user_id]["bakiye"] += 10000
    data[user_id]["last_daily"] = today
    save_data(data)

    await ctx.send(f"{ctx.author.mention}, günlük 10.000 TL hesabına yatırıldı! 💸")

# Bakiye kontrol
@bot.command()
async def bakiye(ctx):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {"bakiye": 0, "coins": {}, "transfer_history": []}

    # Eksik alan varsa tamamla
    if "bakiye" not in data[user_id]:
        data[user_id]["bakiye"] = 0

    miktar = data[user_id]["bakiye"]
    await ctx.send(f"💰 Bakiyen: {miktar} TL")

# Kelime oyunu
@bot.command()
async def kelime(ctx, *args):
    if len(args) < 1:
        return await ctx.send("Lütfen bir miktar belirt! Örnek: `!kelime 2000` veya `!kelime @kisi1 @kisi2 2000`")

    try:
        miktar = int(args[-1])
    except ValueError:
        return await ctx.send("Miktar sayı olmalı. Örnek: `!kelime 2000`")

    mention_ids = [user.id for user in ctx.message.mentions]
    players = [ctx.author]

    kelimeler = [
    "kitap", "kalem", "masa", "bilgisayar", "klavye", "fare", "monitor", "program", "internet", "sunucu",
    "ağaç", "çiçek", "bulut", "güneş", "yağmur", "kar", "fırtına", "deniz", "okyanus", "ırmak",
    "gözlük", "saat", "telefon", "televizyon", "konsol", "oyun", "fare", "kasa", "hoparlör", "kulaklık",
    "yazılım", "donanım", "kod", "script", "algoritma", "veri", "hacker", "sunucu", "host", "domain",
    "balık", "kedi", "köpek", "kuş", "tavşan", "inek", "aslan", "kaplan", "zebra", "fil",
    "savaş", "barış", "güç", "düşman", "müttefik", "kalkan", "silah", "mühimmat", "patlama", "kalkan",
    "robot", "android", "yapayzeka", "otomasyon", "drone", "mekanik", "çip", "biyonik", "uydu", "simülasyon",
    "hayal", "gerçek", "rüya", "zihin", "beyin", "zeka", "düşünce", "his", "duygu", "ahlak",
    "kalp", "ruh", "akıl", "bilinç", "vicdan", "empati", "etik", "mantık", "sezgi", "karar",
    "sistem", "işlemci", "ram", "anakart", "disk", "ssd", "nvme", "soğutucu", "fan", "kas",
    "oyuncu", "yayıncı", "stream", "discord", "mikrofon", "kamera", "ayar", "mod", "admin", "yetkili",
    "polis", "asker", "doktor", "öğretmen", "avukat", "mühendis", "pilot", "astronot", "yazar", "ressam",
    "sokak", "cadde", "köy", "şehir", "kasaba", "ilçe", "mahalle", "ev", "apartman", "bina",
    "bardak", "çatal", "kaşık", "tabak", "tencere", "ocak", "buzdolabı", "fırın", "mikrodalga", "bıçak",
    "renk", "kırmızı", "mavi", "yeşil", "sarı", "turuncu", "mor", "beyaz", "siyah", "pembe",
    "duvar", "tavan", "halı", "perde", "koltuk", "sandalye", "lamba", "ayna", "sehpa", "çekyat",
    "oyuncak", "bebek", "araba", "tren", "uçak", "helikopter", "gemi", "denizaltı", "bisiklet", "motor",
    "çalışma", "dinlenme", "uyku", "uyanma", "koşu", "yüzme", "zıplama", "yürüyüş", "egzersiz", "antrenman",
    "muz", "elma", "armut", "çilek", "karpuz", "kavun", "üzüm", "ananas", "portakal", "mandalina",
    "sınav", "ödev", "ders", "kitaplık", "not", "defter", "kalemlik", "silgi", "cetvel", "bilgi",
    "zeka", "deney", "laboratuvar", "formül", "madde", "atom", "molekül", "element", "reaksiyon", "ısı"
]
    orijinal = random.choice(kelimeler)
    karisik = ''.join(random.sample(orijinal, len(orijinal)))

    komik_cevaplar = [
        "Uyyy canım o ne öyle, yanlış tabii ki 😏",
        "Aşkım biraz daha zorla ya, olmadı bu 🤭",
        "Bu kelimeyle ancak kalp kırarsın, doğru değil 🪣",
        "Yalnız değilsin... yanlışsın 💔",
        "Tatlım, bu cevapla beni etkileyemedin 😘"
    ]

    if mention_ids:
        for user in ctx.message.mentions:
            await ctx.send(f"{user.mention}, {ctx.author.mention} seni düelloya çağırdı! Katılmak için `evet` yaz!")

        async def check_join(m):
            return m.author.id in mention_ids and m.channel == ctx.channel and m.content.lower() == "evet"

        onaylananlar = []
        try:
            while len(onaylananlar) < len(mention_ids):
                msg = await bot.wait_for('message', timeout=15.0, check=check_join)
                if msg.author not in onaylananlar:
                    onaylananlar.append(msg.author)
        except asyncio.TimeoutError:
            pass

        players.extend(onaylananlar)

        if len(players) < 2:
            return await ctx.send("Yeterli katılım olmadı. Oyun iptal edildi.")

        for player in players:
            if get_bakiye(player.id) < miktar:
                return await ctx.send(f"{player.mention}, bakiyen yetersiz. Oyun iptal.")

        for player in players:
            update_bakiye(player.id, -miktar)

        await ctx.send(f"🧠 Kelime oyunu başladı! Kelime: **{karisik}**")

        def check_answer(m):
            return m.author in players and m.channel == ctx.channel

        try:
            while True:
                cevap = await bot.wait_for("message", timeout=20.0, check=check_answer)
                if cevap.content.lower() == orijinal:
                    kazanan = cevap.author
                    toplam = miktar * len(players)
                    update_bakiye(kazanan.id, toplam)
                    await ctx.send(f"🎉 {kazanan.mention} kazandı ve {toplam} TL aldı! Doğru kelime: **{orijinal}**")
                    for player in players:
                        if player == kazanan:
                            update_stats(player.id, won=True)
                        else:
                            update_stats(player.id, lost=True)
                    return
                else:
                    await ctx.send(f"{cevap.author.mention} {random.choice(komik_cevaplar)}")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Süre doldu! Doğru kelime: **{orijinal}**")
    else:
        if get_bakiye(ctx.author.id) < miktar:
            return await ctx.send("Yetersiz bakiye!")

        update_bakiye(ctx.author.id, -miktar)
        await ctx.send(f"🧠 Kelime: **{karisik}** (Doğru kelimeyi 20 saniyede bul!)")

        def check_single(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            while True:
                cevap = await bot.wait_for("message", timeout=20.0, check=check_single)
                if cevap.content.lower() == orijinal:
                    update_bakiye(ctx.author.id, miktar * 2)
                    await ctx.send(f"🎉 Doğru bildin {ctx.author.mention}, {miktar * 2} TL kazandın!")
                    update_stats(ctx.author.id, won=True)
                    return
                else:
                    await ctx.send(f"{ctx.author.mention} {random.choice(komik_cevaplar)}")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Süre doldu! Doğru kelime: **{orijinal}**")
            update_stats(ctx.author.id, lost=True)

# Slot oyunu
@bot.command()
async def slot(ctx, miktar: int):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data or data[user_id]["bakiye"] < miktar:
        return await ctx.send("💸 Yetersiz bakiye dostum. Parayı düzgün ayarla 😅")

    if miktar <= 0:
        return await ctx.send("📉 0 TL ile şans mı denenir ya?")

    semboller = ["💩"] * 40 + ["💰"] * 30 + ["🔔"] * 15 + ["7️⃣"] * 5
    sonuç = [random.choice(semboller) for _ in range(3)]

    # İlk gönderilen mesaj (boş slotlar gibi)
    mesaj = await ctx.send("🎰 | 🔄 | 🔄 | 🔄 | 🎰")

    # Animasyon: sırayla aç
    gösterilen = ["🔄", "🔄", "🔄"]
    for i in range(3):
        await asyncio.sleep(1)  # 1 saniye bekle
        gösterilen[i] = sonuç[i]
        await mesaj.edit(content=f"🎰 | {' | '.join(gösterilen)} | 🎰")

    # 1 saniye sonra sonucu gönder
    await asyncio.sleep(1)

    if sonuç.count(sonuç[0]) == 3:
        sembol = sonuç[0]
        if sembol == "💩":
            await ctx.send("💩 Üç tane bok! En azından kaybetmedin... Neyse ki 😅")
            return  # Para değişmez
        elif sembol == "💰":
            kazanç = miktar * 2
            data[user_id]["bakiye"] += kazanç
            save_data(data)
            return await ctx.send(f"💰 Üç para! {kazanç} TL senin oldu! 🤑")
        elif sembol == "🔔":
            kazanç = miktar * 3
            data[user_id]["bakiye"] += kazanç
            save_data(data)
            return await ctx.send(f"🔔 Ziller çaldı! {kazanç} TL kazandın! 🔥")
        elif sembol == "7️⃣":
            kazanç = miktar * 5
            data[user_id]["bakiye"] += kazanç
            save_data(data)
            return await ctx.send(f"7️⃣ JACKPOT! {kazanç} TL senin! 👑")
    elif sonuç.count("💩") == 3:
        return await ctx.send("💩 Üç bok geldi ama para gitmedi. Şanssız ama zararsız...")

    # Kaybettiyse
    data[user_id]["bakiye"] -= miktar
    save_data(data)
    await ctx.send(f"🙃 Şansını başkası kullandı gibi... {miktar} TL uçtu gitti.")






def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

# Mayın Tarlası Oyunu
aktif_oyunlar = {}

@bot.command()
async def mayin(ctx, miktar: int):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data or data[user_id].get("bakiye", 0) < miktar:
        return await ctx.send("💸 Yetersiz bakiye.")

    if user_id in aktif_oyunlar:
        return await ctx.send("❗ Zaten aktif bir oyunun var.")

    data[user_id]["bakiye"] -= miktar
    save_data(data)

    oyun = {
        "kullanici": ctx.author,
        "kanal": ctx.channel,
        "miktar": miktar,
        "tur": 1,
        "kazanc": miktar,
    }

    aktif_oyunlar[user_id] = oyun
    await yeni_tur(user_id)

def mayin_sayisi(tur):
    if tur <= 5:
        return 1
    elif tur <= 7:
        return 2
    else:
        return 3

async def yeni_tur(user_id, interaction=None):
    oyun = aktif_oyunlar[user_id]
    kanal = oyun["kanal"]
    tur = oyun["tur"]
    oyun["mayinlar"] = random.sample(range(5), mayin_sayisi(tur))  # ❗ Mayınlar her turda burada güncelleniyor

    class Kutu(discord.ui.Button):
        def __init__(self, index):
            super().__init__(
                label=" ",
                emoji="⬛",
                style=discord.ButtonStyle.secondary,
                row=index // 3,
                custom_id=f"{index}"
            )
            self.index = index

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != oyun["kullanici"]:
                return await interaction.response.send_message("❌ Bu oyun sana ait değil.", ephemeral=True)

            secilen = self.index
            mayinlar = oyun["mayinlar"]

            # Kutuların tümünü göster (💩 veya 💰)
            acik_view = discord.ui.View()
            for i in range(5):
                acik_view.add_item(discord.ui.Button(
                    label="💩" if i in mayinlar else "💰",
                    style=discord.ButtonStyle.danger if i in mayinlar else discord.ButtonStyle.success,
                    disabled=True,
                    row=i // 3
                ))

            await interaction.response.edit_message(
                content=f"🎯 Tur {tur}: Seçim yapıldı, kutular açılıyor...",
                view=acik_view
            )
            await asyncio.sleep(2)

            if secilen in mayinlar:
                await interaction.edit_original_response(
                    content=f"💥 Mayına bastın! {oyun['kazanc']} TL yandı.",
                    view=None
                )
                del aktif_oyunlar[user_id]
                return
            else:
                oyun["kazanc"] *= 2
                oyun["tur"] += 1

                if oyun["tur"] > 10:
                    data = load_data()
                    data[user_id]["bakiye"] += oyun["kazanc"]
                    save_data(data)
                    await interaction.edit_original_response(
                        content=f"🏆 Oyunu tamamladın! {oyun['kazanc']} TL kazandın.",
                        view=None
                    )
                    del aktif_oyunlar[user_id]
                    return

                # Yeni tur başlat (aynı mesajı güncelleyerek)
                await yeni_tur(user_id, interaction)

    class Cekil(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="🏃 Parayı Al ve Çık",
                style=discord.ButtonStyle.primary,
                row=2
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != oyun["kullanici"]:
                return await interaction.response.send_message("❌ Bu oyun sana ait değil.", ephemeral=True)

            data = load_data()
            data[user_id]["bakiye"] += oyun["kazanc"]
            save_data(data)

            await interaction.response.edit_message(
                content=f"💰 {oyun['kazanc']} TL'yi aldın ve oyundan çıktın.",
                view=None
            )
            del aktif_oyunlar[user_id]

    # Yeni kutular ve butonlar
    view = discord.ui.View()
    for i in range(5):
        view.add_item(Kutu(i))
    view.add_item(Cekil())

    mesaj_yazisi = f"✅ Doğru seçim yaptın! Yeni kazanç: {oyun['kazanc']} TL\n🎯 Tur {oyun['tur']}: Bir kutu seç! Mayın sayısı: {mayin_sayisi(oyun['tur'])}"

    if interaction is None:
        mesaj = await kanal.send(mesaj_yazisi, view=view)
        oyun["mesaj"] = mesaj
    else:
        await interaction.edit_original_response(content=mesaj_yazisi, view=view)






#takas komutu
@bot.command()
async def takas(ctx, kullanıcı: discord.Member, miktar: int):
    gönderen_id = str(ctx.author.id)
    alıcı_id = str(kullanıcı.id)
    data = load_data()

    if ctx.author.id == kullanıcı.id:
        return await ctx.send("🫵 Kendine para mı yolluyorsun? Cidden mi? 😅")

    if miktar <= 0:
        return await ctx.send("💸 Pozitif bir miktar girmen lazım...")

    if gönderen_id not in data or data[gönderen_id]["bakiye"] < miktar:
        return await ctx.send("💔 Bu kadar paran yok dostum...")

    # Alıcı hesabı yoksa oluştur
    if alıcı_id not in data:
        data[alıcı_id] = {
            "bakiye": 0,
            "daily_claimed": False,
            "wins": 0,
            "losses": 0,
            "transfer_history": [],
            "received_history": []
        }

    # Gönderenin hesabında transfer geçmişi yoksa ekle
    data[gönderen_id].setdefault("transfer_history", [])
    data[alıcı_id].setdefault("received_history", [])

    # Para aktar
    data[gönderen_id]["bakiye"] -= miktar
    data[alıcı_id]["bakiye"] += miktar

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Gönderim geçmişi
    data[gönderen_id]["transfer_history"].append({
        "to": alıcı_id,
        "amount": miktar,
        "timestamp": now
    })

    # Alım geçmişi
    data[alıcı_id]["received_history"].append({
        "from": gönderen_id,
        "amount": miktar,
        "timestamp": now
    })

    save_data(data)

    await ctx.send(f"✅ {ctx.author.mention}, {kullanıcı.mention} kişisine {miktar} TL gönderdi. Cömertliğine sağlık! 💸")
    
#Geçmiş komutu
@bot.command()
async def history(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data or not data[user_id].get("transfer_history"):
        return await ctx.send("📭 Hiç transfer geçmişin yok, kimseye para yollamamışsın gibi görünüyor...")

    geçmiş = data[user_id]["transfer_history"][-10:]  # son 10 kayıt
    mesaj = "**📜 Son Gönderdiğin Transferler:**\n"

    for i, kayit in enumerate(reversed(geçmiş), 1):  # en yeniyi en üste alır
        try:
            alici = await bot.fetch_user(int(kayit["to"]))
            isim = alici.name
        except:
            isim = "Bilinmeyen Kullanıcı"
        zaman = kayit.get("timestamp", "Tarih yok")
        miktar = kayit.get("amount", 0)
        mesaj += f"**{i}.** {isim} → {miktar} TL ({zaman})\n"

    await ctx.send(mesaj)

#son alınan para
@bot.command()
async def son(ctx):
    kullanıcı_id = str(ctx.author.id)
    data = load_data()

    if kullanıcı_id not in data or "received_history" not in data[kullanıcı_id] or not data[kullanıcı_id]["received_history"]:
        return await ctx.send("📭 Hiç para almadın... Yalnızsın galiba. 😢")

    geçmiş = data[kullanıcı_id]["received_history"][-5:]  # son 5 işlemi al
    mesaj = "**📥 Son Alınan Paralar:**\n"
    for işlem in reversed(geçmiş):
        gönderen = await bot.fetch_user(int(işlem["from"]))
        mesaj += f"• {işlem['timestamp']} - {gönderen.name} → {işlem['amount']} TL\n"

    await ctx.send(mesaj)

#para isteme
@bot.command()
async def istiyorum(ctx, kullanıcı: discord.Member, miktar: int):
    if ctx.author.id == kullanıcı.id:
        return await ctx.send("🫵 Kendinden para isteme, trajikomik...")

    if miktar <= 0:
        return await ctx.send("😅 Pozitif bir miktar girmelisin.")

    class ParaIstekView(View):
        def __init__(self):
            super().__init__(timeout=30)

        @discord.ui.button(label="✅ Kabul Et", style=discord.ButtonStyle.green)
        async def kabul_et(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != kullanıcı.id:
                return await interaction.response.send_message("⛔ Bu buton sana ait değil!", ephemeral=True)

            data = load_data()

            gönderen_id = str(kullanıcı.id)
            alan_id = str(ctx.author.id)

            if gönderen_id not in data or data[gönderen_id]["bakiye"] < miktar:
                return await interaction.response.send_message("💸 Yeterli paran yokmuş dostum!", ephemeral=True)

            data[gönderen_id]["bakiye"] -= miktar
            data.setdefault(alan_id, {
                "bakiye": 0,
                "daily_claimed": False,
                "wins": 0,
                "losses": 0,
                "received_history": []
            })
            data[alan_id]["bakiye"] += miktar
            data[alan_id].setdefault("received_history", []).append({
                "from": gönderen_id,
                "amount": miktar,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            save_data(data)
            await interaction.response.edit_message(content=f"💸 {kullanıcı.mention}, {ctx.author.mention} kişisine {miktar} TL gönderdi!", view=None)

        @discord.ui.button(label="❌ Reddet", style=discord.ButtonStyle.red)
        async def reddet(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != kullanıcı.id:
                return await interaction.response.send_message("⛔ Bu buton sana ait değil!", ephemeral=True)

            await interaction.response.edit_message(content="❌ İstek reddedildi.", view=None)

    view = ParaIstekView()
    await ctx.send(f"{kullanıcı.mention}, {ctx.author.mention} senden {miktar} TL istiyor. Kabul ediyor musun?", view=view)
    
#geliştiricinin para yükleyebilmesi    
@bot.command()
async def yükle(ctx, miktar: int):
    if ctx.author.id != 960954961552871514:  # ← Sadece bot sahibi için
        return await ctx.send("❌ Bu komutu sadece bot sahibi kullanabilir.")

    import os
    import json

    user_id = str(ctx.author.id)

    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:
            json.dump({}, f)

    with open("data.json", "r") as f:
        data = json.load(f)

    if user_id not in data:
        data[user_id] = {"bakiye": 0, "yatirimlar": {}}

    # Eksik alan varsa tamamla
    if "bakiye" not in data[user_id]:
        data[user_id]["bakiye"] = 0
    if "yatirimlar" not in data[user_id]:
        data[user_id]["yatirimlar"] = {}

    data[user_id]["bakiye"] += miktar

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    await ctx.send(f"✅ {miktar} TL başarıyla eklendi. Yeni bakiyen: {data[user_id]['bakiye']} TL")
    
# İstatistikler
@bot.command()
async def istatistikler(ctx, üye: discord.Member = None):
    if üye is None:
        üye = ctx.author

    data = load_data()
    uid = str(üye.id)
    if uid not in data:
        return await ctx.send(f"{üye.mention} hakkında istatistik bulunamadı.")

    kazanma = data[uid].get("won", 0)
    kaybetme = data[uid].get("lost", 0)

    await ctx.send(f"📊 {üye.mention} istatistikleri:\n🏆 Kazanılan oyun: `{kazanma}`\n💔 Kaybedilen oyun: `{kaybetme}`")

# Lider tablosu
@bot.command()
async def lider(ctx):
    data = load_data()

    if not data:
        return await ctx.send("Henüz kimsenin parası yok. İlk sen olabilirsin! 💸")

    sıralama = sorted(data.items(), key=lambda x: x[1].get("bakiye", 0), reverse=True)

    mesaj = "**💰 En Zenginler Listesi 💰**\n"
    for i, (uid, bilgi) in enumerate(sıralama[:5], start=1):
        try:
            kullanıcı = await bot.fetch_user(int(uid))
            mesaj += f"**{i}.** {kullanıcı.name}: {bilgi.get('bakiye', 0)} TL\n"
        except:
            continue

    await ctx.send(mesaj)

#coin al
@bot.command()
async def coinal(ctx, coin_adi: str, miktar: int):
    user_id = str(ctx.author.id)
    coin_adi = coin_adi.upper()

    with open("coins.json", "r") as f:
        coins = json.load(f)

    if coin_adi not in coins:
        await ctx.send("❌ Böyle bir coin bulunamadı.")
        return

    fiyat = coins[coin_adi]
    toplam = fiyat * miktar

    with open("data.json", "r") as f:
        data = json.load(f)

    # Kullanıcı verisi yoksa oluştur
    if user_id not in data:
        data[user_id] = {
            "bakiye": 0,
            "yatirimlar": {}
        }

    # Yatırımlar alanı yoksa ekle
    if "yatirimlar" not in data[user_id]:
        data[user_id]["yatirimlar"] = {}

    if data[user_id]["bakiye"] < toplam:
        await ctx.send("❌ Yetersiz bakiye.")
        return

    data[user_id]["bakiye"] -= toplam
    data[user_id]["yatirimlar"][coin_adi] = data[user_id]["yatirimlar"].get(coin_adi, 0) + miktar

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    await ctx.send(f"✅ {miktar} adet {coin_adi} satın aldınız!")

#coin sat
@bot.command()
async def coinsat(ctx, coin_adi: str, miktar: float):
    user_id = str(ctx.author.id)
    coin_adi = coin_adi.upper()

    with open("coins.json", "r") as f:
        coins = json.load(f)

    if coin_adi not in coins:
        return await ctx.send("❌ Böyle bir coin bulunamadı.")

    data = load_data()
    if user_id not in data or "yatirimlar" not in data[user_id] or data[user_id]["yatirimlar"].get(coin_adi, 0) < miktar:
        return await ctx.send("🚫 Bu kadar coin'e sahip değilsin.")

    fiyat = coins[coin_adi]
    toplam_tutar = fiyat * miktar

    data[user_id]["yatirimlar"][coin_adi] -= miktar
    if data[user_id]["yatirimlar"][coin_adi] <= 0:
        del data[user_id]["yatirimlar"][coin_adi]

    data[user_id]["bakiye"] += toplam_tutar

    save_data(data)
    await ctx.send(f"✅ {miktar} adet **{coin_adi.upper()}** sattın. Toplam: {round(toplam_tutar, 2)} TL.")

#cüzdan 
@bot.command(aliases=["cüzdan"])
async def portföy(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data or "yatirimlar" not in data[user_id] or not data[user_id]["yatirimlar"]:
        return await ctx.send("💼 Hiç yatırımın yok.")

    with open("coins.json", "r") as f:
        coins = json.load(f)

    mesaj = f"**📊 {ctx.author.display_name}'in Portföyü:**\n"
    toplam_deger = 0

    for coin, miktar in data[user_id]["yatirimlar"].items():
        fiyat = coins.get(coin, 0)
        deger = round(miktar * fiyat, 2)
        toplam_deger += deger
        mesaj += f"> 💰 **{coin.upper()}**: {miktar} adet | Değeri: {deger} TL\n"

    mesaj += f"\n**Toplam Portföy Değeri:** {round(toplam_deger, 2)} TL"

    await ctx.send(mesaj)

#coin fiyatları
@bot.command()
async def fiyatlar(ctx):
    try:
        with open("coins.json", "r") as f:
            coins = json.load(f)

        mesaj = "**📈 Güncel Coin Fiyatları:**\n"
        for coin, price in coins.items():
            mesaj += f"> 💰 **{coin.upper()}**: {price} TL\n"

        await ctx.send(mesaj)

    except FileNotFoundError:
        await ctx.send("❌ Coin fiyat dosyası bulunamadı.")
    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")

async def coin_price_updater():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            with open("coins.json", "r") as f:
                coins = json.load(f)

            for coin, price in coins.items():
                if coin in coin_behaviors:
                    min_change = coin_behaviors[coin]["min"]
                    max_change = coin_behaviors[coin]["max"]
                    percent_change = random.uniform(min_change, max_change)
                    new_price = round(price * (1 + percent_change / 100), 2)
                    if new_price < 0.01:
                        new_price = 0.01
                    coins[coin] = new_price

            with open("coins.json", "w") as f:
                json.dump(coins, f, indent=2)

            print("[Coin Güncellemesi] Coin fiyatları güncellendi.")

        except Exception as e:
            print(f"Coin güncelleme hatası: {e}")

        await asyncio.sleep(30)

class MyBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(coin_price_updater())

@bot.event
async def on_ready():
    print(f"{bot.user.name} olarak giriş yapıldı.")
    bot.loop.create_task(coin_price_updater())

# Botu başlat
bot.run("MTI0OTc5NTA0NjQ3MjE1OTM0Mw.Go6geE.RE2xWzg5XsKvC5u2iD7CZ-L-fvGJyiQyt38pgw")
