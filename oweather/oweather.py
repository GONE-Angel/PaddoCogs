from discord.ext import commands
from .utils.dataIO import fileIO
import aiohttp
import os
from .utils import checks


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/weather/weather.json'

    @commands.command(pass_context=True, name='weather', aliases=['we'])
    async def _weather(self, context, *arguments: str):
        """Get the weather!"""
        settings = fileIO(self.settings_file, "load")
        api_key = settings['WEATHER_API_KEY']
        if api_key != '':
            payload = {'q': " ".join(arguments), 'appid': api_key}
            url = 'http://api.openweathermap.org/data/2.5/weather?'
            headers = {'user-agent': 'Red-cog/1.0'}
            conn = aiohttp.TCPConnector(verify_ssl=False)
            session = aiohttp.ClientSession(connector=conn)
            async with session.get(url, params=payload, headers=headers) as r:
                parse = await r.json()
            session.close()
            celcius = round(int(parse['main']['temp'])-273)+1
            fahrenheit = round(int(parse['main']['temp'])*9/5-459)+2
            temperature = '{0} Celsius / {1} Fahrenheit'.format(celcius, fahrenheit)
            humidity = str(parse['main']['humidity']) + '%'
            pressure = str(parse['main']['pressure']) + ' hPa'
            wind_kmh = str(round(parse['wind']['speed'] * 3.6)) + ' km/h'
            wind_mph = str(round(parse['wind']['speed'] * 2.23694)) + ' mp/h'
            clouds = parse['weather'][0]['description'].title()
            name = parse['name'] + ', ' + parse['sys']['country']
            message = 'Weather in {0}\n{1}, {2}\nWind: {3} / {4}\nPressure: {5}\nHumidity: {6}'.format(name, clouds, temperature, wind_kmh, wind_mph, pressure, humidity)
        else:
            message = 'No API key set. Get one at http://openweathermap.org/'
        await self.bot.say('```{0}```'.format(message))

    @commands.command(pass_context=True, name='weatherkey')
    @checks.is_owner()
    async def _weatherkey(self, context, *arguments: str):
        settings = fileIO(self.settings_file, "load")
        if arguments:
            settings['WEATHER_API_KEY'] = arguments[0]
            fileIO(self.settings_file, "save", settings)


def check_folder():
    if not os.path.exists("data/weather"):
        print("Creating data/weather folder...")
        os.makedirs("data/weather")


def check_file():
    weather = {}
    weather['WEATHER_API_KEY'] = ''

    f = "data/weather/weather.json"
    if not fileIO(f, "check"):
        print("Creating default weather.json...")
        fileIO(f, "save", weather)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Weather(bot))