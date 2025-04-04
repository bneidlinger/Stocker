# Retro Trading Console

![Retro Trading Console](./screenshots/main_app.png)

## Listen up, M*BURP*orty!

This isn't your grandpa's boring-ass trading app (unless I'm your grandpa, in which case, it's *exactly* your grandpa's trading app). This is the **Retro Trading Console** - the only stock trading simulator with enough self-respect to look like it was designed in the 80s when people still understood aesthetic *and* the cocaine was pure.

## What is this thing?

It's a *buuurp* backtesting framework, Morty! It lets you test your pathetic trading strategies against historical data to see just how badly you would've lost money if you actually had the balls to trade with real cash. It's like gambling but with extra steps!

The whole interface looks like it was ripped straight out of Fallout meets Miami Vice, because why the hell not? If I'm going to lose money in the market, I might as well do it while staring at neon pink buttons and flickering LEDs.

## Features, or whatever

- **Multiple Trading Strategies**: SMA Crossover, RSI, MACD, Bollinger Bands, Ichimoku Cloud, and more! Some of them actually work! Most don't!
- **Backtesting Engine**: See how your strategy would have performed historically, you know, before you bet your children's college fund on it
- **Vintage UI**: Dot matrix displays, worn LEDs, and that sweet, sweet retro aesthetic that makes you feel like you're hacking the Gibson
- **Technical Analysis**: All those indicators that make you feel smarter than you actually are
- **Custom Symbol Support**: Trade whatever the hell you want, as long as Yahoo Finance has data on it
- **Chart Visualization**: Pretty lines going up and down, mostly down
- **Real Moon Strategy**: Because trading based on lunar phases makes as much sense as any other strategy the "experts" are pushing

## Installation (Pay attention, Morty!)

```bash
# Clone this repo or whatever
git clone https://github.com/your-username/retro-trading-console.git

# Move your ass into the directory
cd retro-trading-console

# Install the dependencies, you'll need TA-Lib C libraries first!
pip install -r requirements.txt
```

## TA-Lib Installation (This is important, Morty!)

This thing depends on TA-Lib, which is a pain in the ass to install because it requires C/C++ compilation. Here's how to get it:

### Windows:
Download the wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) and install it with:
```bash
pip install TA_Lib‑0.4.X‑cpXX‑cpXXm‑win_amd64.whl
```

### macOS:
```bash
brew install ta-lib
pip install TA-Lib
```

### Linux:
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

## Usage (Listen closely, you'll mess this up)

```bash
python main.py
```

Then just select a stock symbol, load some data, pick a strategy that sounds smart, and run your backtest. Marvel at how badly you would have done, or on the rare occasion you find a winning strategy, screenshot it quickly before the market changes and it stops working.

## Dependencies

- customtkinter: For making the UI look less like garbage
- pandas: For data manipulation and all that nerdy stuff
- yfinance: For pulling stock data without paying for an API
- matplotlib: For those fancy charts that make you feel important
- backtesting: For the actual backtesting engine
- TA-Lib: For technical indicators that the "pros" use
- ephem: For that sweet, sweet lunar trading strategy

## Why did I make this?

Because the universe is chaos, Morty! The stock market is just a big Ponzi scheme where the people who got in first are taking money from the people who got in last. Might as well have some fun while we watch it all burn!

Also, I was bored.

## Contributing

Don't.

But if you absolutely must, here's how:

1. Fork the repo
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request and wait while I ignore it

## Easter Eggs

There might be an easter egg if you click on the PWR LED. Not telling you what it is though. Figure it out yourself, you're supposed to be smart.

## License

This project is licensed under the "Do Whatever You Want But Don't Blame Me When You Lose Money" License.

## Disclaimer

This is not financial advice, Morty! Only an idiot would take financial advice from a program that looks like it was designed by a coked-up Wall Street banker in 1987. Never trade with money you can't afford to lose. *Buuurp* In fact, just assume you're going to lose it all and be pleasantly surprised when you don't.

---

Now go make some imaginary money, Morty! And if by some miracle you make real money with this, Grandpa's gonna need his cut! Wubba lubba dub dub!
