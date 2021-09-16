import discord
from discord import client
from discord.ext import commands
from selenium.webdriver.chrome import options
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import time
import os

bot = commands.Bot(command_prefix='.')
client = discord.Client()

user = []                 #노래정보
musictitle = []
song_queue = []
musicnow = []             #현재 출력

def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = load_chrome_driver()
    driver = webdriver.Chrome(chromedriver_dir, options = options)
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()
    
    return music, URL

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

def load_chrome_driver():
      
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)

    else:
        if not vc.is_playing():
            client.loop.create_task(vc.disconnect())

@bot.event
async def on_ready():
    print(bot.user.name)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("김장훈으로 변신"))

    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

@bot.command()       #입장 명령어
async def 김장훈(ctx):
    global vc
    vc = await ctx.message.author.voice.channel.connect()

@bot.command()         #내보내기
async def 꺼져(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("이미 나갔어 병신아")

@bot.command()            #url재생
async def u(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(embed = discord.Embed(title= "숲튽훈의랩소디", description =  "현재재생중인 곡은" + url + ". 입니다", color = 0x00ff00))
    else:
        await ctx.send("숲튽훈은 이미 열창 중입니다!")

@bot.command()               #검색 재생
async def p(ctx, *, msg):

    global vc
    vc = await ctx.message.author.voice.channel.connect()

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        driver = load_chrome_driver()
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl

        driver.quit()

        musicnow.insert(0, entireText)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재재생중인 곡은" + musicnow[0] + ". 입니다", color = 0x00ff00))
        vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        user.append(msg)
        result,URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send(+ result + ".추가 완료")

@bot.command()                    #큐 추가
async def pp(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + ". 노래 예약 완료")

@bot.command()                  #스킵

async def s(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래끄기", description = musicnow[0]  + ". 그만 부를게...", color = 0x00ff00))
    else:
        await ctx.send("숲튽훈은 쉬고있습니다")
    


@bot.command()                    #큐 삭제
async def d(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("예약 노래 삭제 완료")
    except:
        if len(list) == 0:
            await ctx.send("예약된 노래 없음")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            else:
                await ctx.send("숫자를 입력해주세요!")

@bot.command()
async def list(ctx):
    if len(musictitle) == 0:
        await ctx.send("예약된 노래 없음")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
        await ctx.send(embed = discord.Embed(title= "list", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 명령어(ctx):
    await ctx.send(embed = discord.Embed(title='도움말',description="""
\n.김장훈 -> 봇 입장
\n.꺼져 -> 봇 나감
\n.p -> 노래 재생
\n.pp -> 노래 예약
\n.s -> 노래 끄기
\n.list -> 예약 목록
""", color = 0x00ff00))


bot.run('ODg4MDY5NjE5MDY2MjI4Nzc2.YUNVSA.wgqGSC-JghCvzIxuctR4kc54YUo')