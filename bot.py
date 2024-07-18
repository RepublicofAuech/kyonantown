import discord
from discord.ext import commands
import requests
import re
import os
import random
from discord import app_commands
from PIL import Image
from io import BytesIO
import time

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

#起動時に送信されるメッセージ
@bot.event
async def on_ready():
    print("起動完了")
    await bot.tree.sync()

#/avatar
@bot.tree.command(name="avatar", description="このBOTのアバターを貼ります。")
async def avatar(interaction: discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/1250198739872776254/1259624992753057792/6ce16e7b820c7557.png?ex=668c5cb0&is=668b0b30&hm=342176d809170afe96f86deb21f922df08e40a614b4d5f02c00cd2eb48eb68f1&=&format=webp&quality=lossless&width=671&height=671")

#/kyonan_town
@bot.tree.command(name="kyonan_town", description="鋸南町の詳細を説明します。")
async def kyonan_town(interaction: discord.Interaction):
    await interaction.response.send_message("# 鋸南町（きょなんまち）\n人口：6,757人（2024年7月）\n面積：45.17km2\n昼夜間人口比率：86.9%（2020年）\nGDP：152億円（2018年）\nGDP PC：約201万円（2018年）\n財政力指数：0.30（県内最下位）\nhttps://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Kyonan%2C_Chiba.svg/1280px-Flag_of_Kyonan%2C_Chiba.svg.png")

#/support
@bot.tree.command(name="support", description="このBOTのサポートサーバーを貼ります。")
async def support(interaction: discord.Interaction):
    await interaction.response.send_message("https://discord.gg/V632ebfd9Q")

#/pb_toto
@bot.tree.command(name="pb_toto", description="鳥取県信者ボールのチャンネルを貼ります。")
async def pb_toto(interaction: discord.Interaction):
    await interaction.response.send_message("https://youtube.com/@pb_toto")

#/always_on
@bot.tree.command(name="always_on", description="DiscloudでBOTを常時起動する方法を貼ります。（vscodeのみ）")
async def always_on(interaction: discord.Interaction):
    await interaction.response.send_message("①\n「discloud.config」という名前のファイルを作る\n\n②\n`NAME=bot名\nAVATAR=https://i.imgur.com/bWhx7OT.png\nTYPE=bot\nMAIN=コードが組まれているファイル名\nRAM=100\nAUTORESTART=false\nVERSION=latest\nAPT=tools`\nを「discloud.config」に貼り付ける\n\n③\n`pip freeze > requirements.txt`をターミナルで実行する\n\n④\n`discord.py==2.4.0`以外を消し、3つのファイルをCtrl+Sで保存\n\n⑤\nそれらをZipで圧縮し、下のURL先のサイトへ飛ぶ\nhttps://discloud.com/\n# ※（2024年7月8日時点）")

#/overlay_base
@bot.tree.command(name="overlay_base", description="「/overlay」の元画像を貼ります。")
async def overlay_base(interaction: discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/1247288750879281262/1262961206101020724/HNI_0028.JPG?ex=66992888&is=6697d708&hm=a6c0fb2601f5cb56d0e9897a745166ee766173382c57c4555a092007d69981c3&=&format=webp")

class VerifyButton(discord.ui.Button):
    def __init__(self, role_id: int):
        super().__init__(label="認証", style=discord.ButtonStyle.primary)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # 初期レスポンスをすぐに送信
        role = interaction.guild.get_role(self.role_id)
        if role:
            if role in interaction.user.roles:
                await interaction.followup.send("既に認証済みです", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.followup.send("認証が完了しました", ephemeral=True)
        else:
            await interaction.followup.send("ロールが見つかりませんでした", ephemeral=True)

class RoleView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.add_item(VerifyButton(role_id))

# 管理者権限を持つユーザーのみがコマンドを使用できるようにする
@bot.tree.command(name="ninsho", description="指定されたロールIDのロールを付与する認証ボタンを表示します。（管理者限定）")
@discord.app_commands.checks.has_permissions(administrator=True)
@discord.app_commands.describe(role_id="付与するロールのID")
async def ninsho(interaction: discord.Interaction, role_id: str):
    try:
        role_id_int = int(role_id)
    except ValueError:
        await interaction.response.send_message("有効な整数のロールIDを入力してください。", ephemeral=True)
        return

    embed = discord.Embed(title="認証システム", description="以下のボタンを押して認証を完了してください。")
    await interaction.response.send_message(embed=embed, view=RoleView(role_id_int), ephemeral=False)

# エラーハンドリング：ユーザーに管理者権限がない場合s
@ninsho.error
async def ninsho_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("このコマンドを使用するには管理者権限が必要です。", ephemeral=True)

# おみくじ機能の追加
@bot.tree.command(name="omikuji", description="おみくじを引きます。")
async def omikuji(interaction: discord.Interaction):
    results = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
    result = random.choice(results)
    await interaction.response.send_message(f"あなたのおみくじの結果は、「{result}」です！", ephemeral=False)

@bot.tree.command(name='thumbnail', description='YouTube動画のサムネイル画像を保存します。（ロング動画限定）')
async def thumbnail(interaction: discord.Interaction, url: str):
    video_id = get_youtube_video_id(url)

    if video_id:
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

        try:
            response = requests.get(thumbnail_url)
            response.raise_for_status()

            file_name = f'thumbnail_{video_id}.jpg'
            file_path = os.path.join(os.getcwd(), file_name)

            with open(file_path, 'wb') as file:
                file.write(response.content)

            await interaction.response.send_message(content=f'下のサムネイルを保存しました\nファイル名：{file_name}', file=discord.File(file_path))

            # Optionally, delete the file after sending it
            os.remove(file_path)

        except requests.exceptions.RequestException as error:
            print(error)
            await interaction.response.send_message('サムネイルの保存に失敗しました\nhttps://media.discordapp.net/attachments/1250065175663349760/1261656589765709824/quote_1261656563060314132.png?ex=6693c0c3&is=66926f43&hm=cfd2c2925aa7240491b71b1bb9fb4ff101075a8d0dedb5bf0bab043899461397&=&format=webp&quality=lossless', ephemeral=True)
    else:
        await interaction.response.send_message('無効なURLです\nhttps://media.discordapp.net/attachments/1250065175663349760/1261657030419157042/quote_1261657004590497853.png?ex=6693c12c&is=66926fac&hm=75c9020827e61664ec1cd60a347162c5d67eefba28788d5f3861c19f9f21c7ed&=&format=webp&quality=lossless', ephemeral=True)

def get_youtube_video_id(url):
    match = re.match(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

# じゃんけんのオプション
choices = ["グー", "チョキ", "パー"]

def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "# 引き分けです！"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        return "# あなたの勝ちです！"
    else:
        return "# あなたの負けです！"

@bot.tree.command(name="janken", description="一発勝負のじゃんけんをします。グー、チョキ、パーのいずれかを選んでください。")
@app_commands.describe(user_choice="グー、チョキ、パーのいずれかを選んでください")
async def janken(interaction: discord.Interaction, user_choice: str):
    if user_choice not in choices:
        await interaction.response.send_message("有効な選択肢はグー、チョキ、パーです。もう一度入力してください。", ephemeral=True)
        return

    bot_choice = random.choice(choices)
    result = determine_winner(user_choice, bot_choice)

    await interaction.response.send_message(f"あなたの選択: {user_choice}\nBOTの選択: {bot_choice}\n{result}", ephemeral=False)

def fetch_image(url, retries=3, delay=10):
    """画像を取得するためのリトライ機能を持つ関数"""
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーが発生した場合例外を投げる
            return Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f'Retrying... ({attempt + 1}/{retries}) after {delay} seconds')
                time.sleep(delay)
            else:
                raise e

# 固定位置の設定
FIXED_X = 263  # オーバーレイ画像のX座標
FIXED_Y = 70  # オーバーレイ画像のY座標

BASE_IMAGE_URL = 'https://cdn.discordapp.com/attachments/1239347707546439774/1263075159351361657/kyonantown.JPG?ex=6698e9e8&is=66979868&hm=75e1695d4cbed45bc7f87eab8c8561466c11c9399cfaec4f37425e674396f851&'  # ベース画像のURL

@bot.tree.command(name="overlay", description="ユーザーのアイコンと合成してちょっとしたコラ画像を作成します。（透過されているアイコンには不向きです。）")
@app_commands.describe(target="ユーザーを選択してください")
async def overlay(interaction: discord.Interaction, target: discord.User):
    try:
        # インタラクションを遅延応答に設定
        await interaction.response.defer()

        # ベース画像を取得
        base_image = fetch_image(BASE_IMAGE_URL)
        base_image = base_image.convert("RGBA")  # 画像をRGBAに変換

        # ユーザーのアバター画像を取得
        avatar_url = target.display_avatar.url
        overlay_image = fetch_image(avatar_url)
        overlay_image = overlay_image.convert("RGBA")  # 画像をRGBAに変換

        # オーバーレイ画像をベース画像のサイズにリサイズ
        overlay_image = overlay_image.resize((90, 90), Image.LANCZOS)  # サイズは例として100x100に設定

        # 固定位置を設定
        position = (FIXED_X, FIXED_Y)

        # ベース画像にオーバーレイ画像を指定位置に貼り付け
        base_image.paste(overlay_image, position, overlay_image)
        base_image.save('overlayed_image.png')

        # 画像を送信
        await interaction.followup.send(file=discord.File('overlayed_image.png'))

        # 一時ファイルを削除
        os.remove('overlayed_image.png')

    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f'画像を取得中にエラーが発生しました。詳細: {e}', ephemeral=False)
        print(f'Error fetching image: {e}', ephemeral=False)
    except IOError as e:
        await interaction.followup.send(f'画像の処理中にエラーが発生しました。詳細: {e}', ephemeral=False)
        print(f'Error processing image: {e}', ephemeral=False)
    except Exception as e:
        await interaction.followup.send(f'エラーが発生しました。詳細: {e}', ephemeral=False)
        print(f'Unexpected error: {e}', ephemeral=False)

bot.run(os.getenv("TOKEN"))
