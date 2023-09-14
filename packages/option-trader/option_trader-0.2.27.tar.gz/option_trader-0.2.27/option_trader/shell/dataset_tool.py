import sys
import argparse
import warnings
import logging
import logging.config


class dataset_refresh_run:

    def __init__(self, args ):
        print('dataset refresh job run')
        self.args = args

    def main(self):

        from option_trader.jobs import dataset_refresh as df

        refresh_job = df.dataset_refresh_job(args.target_path)
        refresh_job.execute()

class dataset_create_run:

    def __init__(self, 
                 watchlist_path, 
                 target_path,
                 risk_mgr,
                 entry_crit,
                 runtime_config,
                 market_cond):

        self.watchlist_path = watchlist_path
        self.target_path = target_path
        self.risk_mgr = risk_mgr
        self.entry_crit = entry_crit
        self.runtime_config = runtime_config
        self.market_cond = market_cond

    def main(self):

        from option_trader.jobs import dataset_create as ct        
        create_job = ct.dataset_create_job(self.watchlist_path,
                                           self.target_path,
                                           self.entry_crit,
                                           self.runtime_config,
                                           self.market_cond,
                                           self.risk_mgr )
        create_job.execute()


# Call main when run as script
if __name__ == '__main__':

    sys.path.append('../../../src/')       

    warnings.filterwarnings("ignore")
 
    from option_trader.settings.log_config import LOGGING

    logging.config.dictConfig(LOGGING)

    parser=argparse.ArgumentParser(description="Account Methods")
    parser.add_argument("-c", "--create", help="create strategy position DB", action="store_true")    
    parser.add_argument("-t", "--target_path", type=str, help="target dataset file path")
    parser.add_argument("-w", "--watchlist_path", type=str, help="watchlist file path")

    args = parser.parse_args()

    if args.create:

        from option_trader.settings.trade_config import entryCrit, riskManager, marketCondition, runtimeConfig

        risk_mgr = riskManager()
        entr_crit = entryCrit()
        runtime_config = runtimeConfig()
        market_cond = marketCondition()

        risk_mgr.stop_loss_percent = 50
        risk_mgr.stop_gain_percent = 100
        risk_mgr.close_days_before_earning = 1
        risk_mgr.close_days_before_expire = 1
        risk_mgr.open_min_days_to_earning = 4
        risk_mgr.open_min_days_to_expire = 4
        risk_mgr.max_option_positions = 10
        risk_mgr.max_loss_per_position = 1500

        create_thread = dataset_create_run( args.watchlist_path, 
                                            args.target_path,                                            
                                            risk_mgr,
                                            entr_crit,
                                            runtime_config,
                                            market_cond )            
        create_thread.main()
              

    elif args.target_path != None:    
        refresh_thread = dataset_refresh_run(args)
        refresh_thread.main()
