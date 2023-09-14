class TestReadMe:
    def test_example(self):
        from tradingenv import TradingEnv
        from tradingenv.contracts import ETF
        from tradingenv.spaces import BoxPortfolio
        from tradingenv.state import IState
        from tradingenv.rewards import RewardLogReturn
        from tradingenv.broker.fees import BrokerFees
        from tradingenv.policy import AbstractPolicy
        import yfinance

        # Load prices of SPY ETF and TLT ETF from Yahoo Finance as pandas.DataFrame.
        prices = yfinance.Tickers(['SPY', 'TLT', 'TBIL']).history(period="12mo", progress=False)['Close'].tz_localize(None)

        # Specify contract type.
        prices.columns = [ETF('SPY'), ETF('TLT'), ETF('TBIL')]

        # Instance the trading environment.
        env = TradingEnv(
            action_space=BoxPortfolio([ETF('SPY'), ETF('TLT')], low=-1, high=+1,
                                      as_weights=True),
            state=IState(),
            reward=RewardLogReturn(),
            prices=prices,
            initial_cash=1_000_000,
            latency=0,  # seconds
            steps_delay=1,  # trades are implemented with a delay on one step
            broker_fees=BrokerFees(
                markup=0.005,  # 0.5% broker markup on deposit rate
                proportional=0.0001,  # 0.01% fee of traded notional
                fixed=1,  # $1 per trade
            ),
        )

        # OpenAI/gym protocol. Run an episode in the environment.
        # env can be passed to RL agents of ray/rllib or stable-baselines3.
        obs = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)

        class Portfolio6040(AbstractPolicy):
            """Implement logic of your investment strategy or RL agent here."""

            def act(self, state):
                """Invest 60% of the portfolio in SPY ETF and 40% in TLT ETF."""
                return [0.6, 0.4]

        # Run the backtest.
        track_record = env.backtest(
            policy=Portfolio6040(),
            risk_free=prices['TBIL'],
            benchmark=prices['SPY'],
            progress_bar=False,
        )

        # The track_record object stores the results of your backtest.
        track_record.fig_net_liquidation_value()
        track_record.tearsheet()
        track_record.weights_target()
        track_record.fig_transaction_costs()
