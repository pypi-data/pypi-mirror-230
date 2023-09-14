from datetime import datetime, timezone, timedelta
import os
import queue
import threading
import time
import json
import signal
import sys
import traceback
import argparse
import csv
import pathlib
import shutil
import pandas as pd

from pymongo import MongoClient, ASCENDING, DESCENDING

from ..mongo_client_gateway import MongoClientTradeGateway

from .constants import (GATEWAY_NAME, FILES)
from .utils import (decode_gf_status, side_to_target_type, decode_exchange_id, encode_gf_side,
                   decode_ordtype, encode_gf_market, get_today_date, get_time_from_str, decode_gf_market)



try:
    import thread
except ImportError:
    import _thread as thread

LL9 = 1000000000


class GfServer(MongoClientTradeGateway):
    def __init__(self, config_filename, endtime, gateway_name):
        MongoClientTradeGateway.__init__(self, config_filename, endtime, gateway_name)

        self.load_tg_setting(config_filename)

        self.insert_orders = {}
        self.oid_to_ref = {}
        self.sids = []
        self.oid_to_traded = {}
        self.oid_to_traded_money = {}

        self.sid_to_req = {}
        self.oid_to_req = {}
        self.oid_to_sid = {}
        self.oid_to_acc = {}
        self.db_id_to_oid = {}
        self.ref_to_oid = {}

        self.order_count = 0  # dbf文件当前index
        self.trade_count = 0
        self.oid_to_local_ids = {}
        self.oid_to_instr_ids = {}

    def monitor(self):
        self.thread_pool.submit(self.monitor_algo_order_insert)
        self.thread_pool.submit(self.monitor_cancel_order_insert)
        self.thread_pool.submit(self.monitor_order_update)
        self.thread_pool.submit(self.monitor_trade_update)
        #self.thread_pool.submit(self.update_asset)
        self.thread_pool.submit(self.update_equity_position)
        self.thread_pool.submit(self.date_change)

    def load_tg_setting(self, config_filename):
        try:
            #config_filename = os.path.join(config_path, 'atx_server_config.json')
            f = open(config_filename, encoding='gbk')
            setting = json.load(f)
            #self.insert_order_path = setting['insert_order_path'].replace('/', '\\')
            self.recv_msg_dir = setting['recv_msg_path'].replace('/', '\\')
            self.insert_order_msg_dir = setting['insert_order_msg_path'].replace(
                '/', '\\')
            self.pos_interval = setting['pos_interval']
            self.acc_interval = setting['acc_interval']

        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            print(f"load config failed! (exception){err}")
            exit(0)

    @MongoClientTradeGateway.error_handler
    def req_buy_order_insert(self, obj):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        temp_filename = self.insert_order_msg_dir + \
            '_temp\\' + 'buy' + formatted_time + '.csv'

        header = ['local_group_no', 'local_group_name', 'local_report_no', 'projectid', 'market', 'stkcode',
                  'hedgeflag', 'bsflag', 'price', 'qty', 'price_mode', 'price_type', 'diy1', 'diy2', 'algo']

        with open(temp_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            target_account_name = obj['accountName']
            acc = self.target_account_names_to_acc[target_account_name]
            account_id = self.account_id[acc]

            oid = str(self.gen_order_id())
            sid = str(obj['sid'])

            local_report_no = oid
            project_id = int(account_id)
            stkcode = obj['ticker']
            market = encode_gf_market(stkcode)
            hedgeflag = '0'
            bsflag = '0B'
            finacial_buy_s = obj["financingBuy"]
            if finacial_buy_s == True:
                bsflag = "4B"
            qty = int(obj["volume"])
            algo_type = decode_ordtype(obj['executionPlan']["order_type"])
            start_time = str(obj['executionPlan']
                             ["start_time"]).replace(":", "")
            end_time = str(obj['executionPlan']["end_time"]).replace(":", "")
            algo_price = 0
            limit_action = 0
            after_action = 0
            algo = f"algo_type={algo_type}|start_time={start_time}|end_time={end_time}|algo_price={algo_price}|limit_action={limit_action}|after_action={after_action}"
            row = ['', '', local_report_no, project_id, market, stkcode,
                   hedgeflag, bsflag, '', qty, '', '', '', '', algo]

            writer.writerow(row)

        # Save the workbook
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        final_filename = f"{self.insert_order_msg_dir}\\instr_001.{formatted_time}.csv"
        shutil.move(temp_filename, final_filename)

        self.logger.info(
            f"[req_buy_order] insert_success (oid){oid} (sid){sid} (param){row}")
        db_id = obj['_id']
        order_dict = {
            'oid': oid,
            'sid': sid,
            "db_id": db_id,
            "ticker": obj['ticker'],
            "volume": qty,
            "accountName": target_account_name,
            "order_type": str(obj['executionPlan']["order_type"]),
            "start_time": str(obj['executionPlan']["start_time"]),
            "end_time": str(obj['executionPlan']["end_time"]),
            "order_time" : datetime.utcnow(),
            'side' : 1
        }

        target_collection = self.order_info_db[acc]['target']
        delete_query = {
            '_id': db_id
        }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(f"[on_req_buy_order] delete (target){obj}")

        atx_order_collection = self.order_info_db[acc]['atx_order']
        local_id_list = []
        instr_id_list = []
        db_msg = {
            "oid": oid,
            "sid": sid,
            "traded_vol": 0,
            "traded_amt": 0,
            "local_ids": local_id_list,
            "instr_ids": instr_id_list,
            "order_msg": order_dict
        }
        query = {"oid": oid}
        res = atx_order_collection.replace_one(query, db_msg, True)
        self.logger.info(
            f"[on_req_order_insert] insert_gf_order_info (res){res} (msg){db_msg}")

        self.sids.append(sid)

        self.sid_to_req[sid] = order_dict
        self.oid_to_req[oid] = order_dict
        self.oid_to_sid[oid] = sid
        self.db_id_to_oid[db_id] = oid
        self.oid_to_acc[oid] = acc
        self.oid_to_traded[oid] = 0
        self.oid_to_traded_money[oid] = 0
        self.oid_to_local_ids[oid] = local_id_list
        self.oid_to_instr_ids[oid] = instr_id_list

    @MongoClientTradeGateway.error_handler
    def req_sell_order_insert(self, obj):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        temp_filename = self.insert_order_msg_dir + \
            '_temp\\' + 'sell' + formatted_time + '.csv'

        header = ['local_group_no', 'local_group_name', 'local_report_no', 'projectid', 'market', 'stkcode',
                  'hedgeflag', 'bsflag', 'price', 'qty', 'price_mode', 'price_type', 'diy1', 'diy2', 'algo']

        with open(temp_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            target_account_name = obj['accountName']
            acc = self.target_account_names_to_acc[target_account_name]
            account_id = self.account_id[acc]

            oid = str(self.gen_order_id())
            sid = str(obj['sid'])

            local_report_no = oid
            project_id = int(account_id)
            stkcode = obj['ticker']
            market = encode_gf_market(stkcode)
            hedgeflag = '0'
            bsflag = '0S'
            qty = int(obj["volume"])
            algo_type = decode_ordtype(obj['executionPlan']["order_type"])
            start_time = str(obj['executionPlan']
                             ["start_time"]).replace(":", "")
            end_time = str(obj['executionPlan']["end_time"]).replace(":", "")
            algo_price = 0
            limit_action = 0
            after_action = 0
            algo = f"algo_type={algo_type}|start_time={start_time}|end_time={end_time}|algo_price={algo_price}|limit_action={limit_action}|after_action={after_action}"
            row = ['', '', local_report_no, project_id, market, stkcode,
                   hedgeflag, bsflag, '', qty, '', '', '', '', algo]

            writer.writerow(row)

        # Save the workbook
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        final_filename = f"{self.insert_order_msg_dir}\\instr_001.{formatted_time}.csv"
        shutil.move(temp_filename, final_filename)

        self.logger.info(
            f"[req_sell_order] insert_success (oid){oid} (sid){sid} (param){row}")
        db_id = obj['_id']
        order_dict = {
            'oid': oid,
            'sid': sid,
            "db_id": db_id,
            "ticker": obj['ticker'],
            "volume": qty,
            "accountName": target_account_name,
            "order_type": str(obj['executionPlan']["order_type"]),
            "start_time": str(obj['executionPlan']["start_time"]),
            "end_time": str(obj['executionPlan']["end_time"]),
            "order_time" : datetime.utcnow(),
            "side" : 2
        }

        target_collection = self.order_info_db[acc]['sell_target']
        delete_query = {
                    "_id" : db_id
                }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(f"[on_req_sell_order] delete (target){delete_res}")

        atx_order_collection = self.order_info_db[acc]['atx_order']
        local_id_list = []
        instr_id_list = []
        db_msg = {
            "oid": oid,
            "sid": sid,
            "traded_vol": 0,
            "traded_amt": 0,
            "local_ids": local_id_list,
            "instr_ids": instr_id_list,
            "order_msg": order_dict
        }
        query = {"oid": oid}
        res = atx_order_collection.replace_one(query, db_msg, True)
        self.logger.info(
            f"[on_req_order_insert] insert_gf_order_info (res){res} (msg){db_msg}")

        self.sids.append(sid)

        self.sid_to_req[sid] = order_dict
        self.oid_to_req[oid] = order_dict
        self.oid_to_sid[oid] = sid
        self.db_id_to_oid[db_id] = oid
        self.oid_to_acc[oid] = acc
        self.oid_to_traded[oid] = 0
        self.oid_to_traded_money[oid] = 0
        self.oid_to_local_ids[oid] = local_id_list
        self.oid_to_instr_ids[oid] = instr_id_list


    @MongoClientTradeGateway.error_handler
    def monitor_order_update(self):
        while not self.is_stopped:

            order_filename = self.recv_msg_dir + '\\' + \
                FILES.ORDERS + '.' + get_today_date() + '.csv'
            
            data_list = []

            df = pd.read_csv(order_filename, dtype={'local_report_no':str})

            header = ['filename', 'local_group_no', 'local_group_name', 'local_report_no', 'instr_no', 'instrstk_no',  'projectid', 'market', 'stkcode', 'hedgeflag', 'bsflag', 'orderqty',
                      'orderprice', 'orderstatus', 'matchqty', 'matchamt', 'cancelqty', 'fees', 'accrued_interest', 'clearamt', 'ordertime', 'direct_operid', 'order_operid', 'remark', 'ordersno', 'orderextno']

            data_list = []
            current_len = df.shape[0]
            
            if(current_len > self.order_count):
                for _, row in df.iloc[self.order_count:].iterrows():
                    row_dict = {}
                    for col in header:
                        row_dict[col] = row[col]
                    data_list.append(row_dict)

                for record in data_list:
                    if record['orderstatus'] in ['5', '8']:
                        self.update_order(record)
                    elif record['orderstatus'] in ['9']:
                        self.logger.info(
                            f"[monitor_order_update] order_rejected msg{record}")
                    
                self.order_count = current_len

            time.sleep(self.order_scan_interval)

    @MongoClientTradeGateway.error_handler
    def update_asset(self):
        while not self.is_stopped:
            asset_filename = self.recv_msg_dir + '\\' + \
                FILES.ACCOUNTS + '.' + get_today_date() + '.csv'
            df = pd.read_csv(asset_filename, dtype={'projectid': int})
            for _, row in df.iterrows():
                account_id = row["projectid"]
                instravl = row["instravl"]
                hkinstravl = row["hkinstravl"] #港股可用资金
                netasset = row["netasset"]
                stkasset = row["stkasset"]
                ftmargin = row["ftmargin"] #持仓占用保证金
                creditmargin = row["ftmargin"] #保证金可用
                assurebalance = row["assurebalance"] #担保品可用
                all_asset = row["allasset"]
                acc = ""
                try:
                    acc = self.account_id_to_acc[int(account_id)]
                except:
                    self.logger.warning(f"account {int(account_id)} not using")
                    continue
                tg_name = self.tgnames[acc]
                accountname = self.log_account_names[acc]
                db_msg = {
                    "_id": tg_name,  # 对应之前的 TG 名称
                    "accountName": accountname,  # 产品名称
                    "avail_amt": instravl,
                    "balance": netasset,
                    "holding": stkasset,
                    'guaranty': creditmargin,
                    "all_asset": all_asset,
                    "updated_at": datetime.utcnow()
                }

                update_msg = {"$set" : db_msg}
                asset_collection = self.order_info_db[acc]['TestEquityAccount']
                query = {'_id': tg_name, 'accountName': accountname}
                res = asset_collection.update_one(query, update_msg)
                self.logger.info(f"[rtn_asset] (res){res} (asset_msg){db_msg}")
            
            time.sleep(self.acc_interval)
     
    @MongoClientTradeGateway.error_handler           
    def update_equity_position(self):
        while not self.is_stopped:
            pos_filename = self.recv_msg_dir + '\\' + \
                FILES.POSITIONS + '.' + get_today_date() + '.csv'
            dtypes ={
                'projectid': int,
                'stkcode' : str,
                'market': str,
                'direction' : str
            }
            df = pd.read_csv(pos_filename, dtype=dtypes)
            for acc in self.accounts_run:
                tg_position_collection = self.order_info_db[acc]['tg_equity_position']
                remove = tg_position_collection.delete_many({'account_name': self.log_account_names[acc], 'tg_name': self.target_account_names[acc]})
                self.logger.info(f"[update_equity_position] delete_old_position_info (remove){remove} ")
            for _, row in df.iterrows():
                account_id = row["projectid"]
                market = row["market"]
                exchange = decode_gf_market(market)
                stkcode = int(row["stkcode"])
                ticker = f'{stkcode:06d}'
                direction = row["direction"] # 'B' 多 ‘S’ 空
                out_direction = "long"
                if direction == 'S':
                    out_direction = 'short'
                schemeid = row["schemeid"]
                hedgeflag = row["hedgeflag"]
                stkholdqty = row["stkholdqty"] #
                stkavl = row["stkavl"] #
                costprice = row["costprice"] #
                #ftmargin = row["ftmargin"]

                acc = ""
                try:
                    acc = self.account_id_to_acc[int(account_id)]
                except:
                    self.logger.warning(f"account {int(account_id)} not using")
                    continue
                tg_name = self.target_account_names[acc]
                accountname = self.log_account_names[acc]
                pos_collection = self.order_info_db[acc]['tg_equity_position']
                query = {'tg_name':tg_name, 'accountName': accountname, "ticker":ticker}
                pos_msg = {
                    "account_name": accountname,
                    "tg_name": tg_name,
                    "ticker": ticker,
                    "exchange": exchange,
                    "direction": out_direction, # long/short，没有short部分就只存long部分
                    "avail_pos": stkavl, # 昨仓
                    "total_pos": stkholdqty, # 今仓，TODO 需要统计下不同券商盘中，对于卖出的position 是直接从 yd_pos 上减，还是在 td_pos 增加一个负的值。
                    "cost": costprice, #没有
                    "type": "stock",
                    "updated_at": datetime.utcnow()
                                }
                res = pos_collection.replace_one(pos_msg, pos_msg, True)
                self.logger.info(f"[update_equity_position] (res){res.modified_count} (order_msg){pos_msg}")
            time.sleep(self.pos_interval)

    @MongoClientTradeGateway.error_handler
    def update_order(self, record):
        if record['matchqty'] == 0:
            self.logger.warning(
                f"[update_order] nothing_traded (record){record}")
            return

        oid = str(record['local_report_no'])
        if  len(oid) == 0:
            self.logger.warning(f"[update_order] not use file to trade record:{record}")
            return

        acc = ""
        sid = ""
        order_dict = {}
        mudan_id = str(record['instrstk_no'])
        if not oid in self.oid_to_acc:  # shut_down or other problem
            trade_acc = int(record['projectid'])

            if trade_acc not in self.account_id_to_acc:
                self.logger.error(
                    f"[update_order] can't_parse_trade_acc {trade_acc}")
                return
            acc = self.account_id_to_acc[trade_acc]
            order_info_collection = self.order_info_db[acc]['atx_order']
            query = {'oid': oid}
            order_info_target = order_info_collection.find_one(query)
            if not order_info_target is None:
                order_dict = order_info_target['order_msg']
                sid = order_info_target['sid']
                try:
                    self.oid_to_instr_ids[oid] = order_info_target['instr_ids']
                except:
                    self.oid_to_instr_ids[oid] = []
                self.oid_to_traded_money[oid] = 0
                self.oid_to_traded[oid] = 0
                self.oid_to_sid[oid] = sid
                self.oid_to_req[oid] = order_dict
                self.oid_to_ref[oid] = mudan_id
            else:
                self.logger.error(f"[update_order] can't_find_oid (oid){oid}")
                return
        else:
            acc = self.oid_to_acc[oid]
            order_dict = self.oid_to_req[oid]
            sid = self.oid_to_sid[oid]
            

        instr_id = str(record['instrstk_no'])
        if instr_id in self.oid_to_instr_ids[oid]:
            return
        else:
            self.oid_to_instr_ids[oid].append(instr_id)
        traded_vol = record['matchqty']

        int_stock_code = int(record['stkcode'])
        ticker = f'{int_stock_code:06d}'
        exchange = decode_exchange_id(ticker)
        volume = record['orderqty']
        
        price = 0
        if(traded_vol != 0):
            price = float(record['matchamt'] / traded_vol)

        tg_name = order_dict['accountName'].split('@')[0]
        accountName = order_dict['accountName'].split('@')[1]
        order_type = order_dict['order_type']
        start_time = order_dict['start_time']
        end_time = order_dict['end_time']
        order_time = order_dict['order_time']

        target_type = side_to_target_type(order_dict['side'])
        status = decode_gf_status(record['orderstatus'])
        utc_start_time = get_time_from_str(str(start_time))

        replace_collection = self.tradelog_db[acc]['order']
        query = {'sid': sid, '_id': int(oid)}
        replace_target = replace_collection.find_one(query)
        dbtime = order_time if order_time > utc_start_time else utc_start_time

        if replace_target is None:
            self.oid_to_ref[oid] = mudan_id
            order_msg = {
                "_id": int(oid),
                "tg_name": tg_name,  # 对应 account_info._id
                "exchange": exchange, # 对应 tlclient.trader.constant 包 ExchangeID
                "target_type": target_type,    # 'buy' | 'sell' | 'limit_sell'
                "volume": volume,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": order_type, 
                "ticker": ticker,
                "sid": sid,  # target中对应的 母单sid
                "accountName": accountName,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_type,  # 此柜台不使用下单时要求的算法
                    "start_time": start_time,
                    "end_time": end_time
                },
                "status": status,  # 'active' | 'filled' | 'canceled'
                "filled_vol": traded_vol,  # 实际成交的 volume
                "dbTime": dbtime,
            }

            res = replace_collection.replace_one(query, order_msg, True)
            self.logger.info(f"[rtn_order] (res){res} (order_msg){order_msg}")
        else:
            price = (replace_target['filled_vol'] * replace_target['price'] + price * traded_vol) / (traded_vol + replace_target['filled_vol'])
            volume += replace_target['volume']
            traded_vol += replace_target['filled_vol']
            
            order_msg = {
                "_id": int(oid),
                "tg_name": tg_name,  # 对应 account_info._id
                "exchange": exchange, # 对应 tlclient.trader.constant 包 ExchangeID
                "target_type": target_type,    # 'buy' | 'sell' | 'limit_sell'
                "volume": volume,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": order_type, 
                "ticker": ticker,
                "sid": sid,  # target中对应的 母单sid
                "accountName": accountName,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_type,  # 此柜台不使用下单时要求的算法
                    "start_time": start_time,
                    "end_time": end_time
                },
                "status": status,  # 'active' | 'filled' | 'canceled'
                "filled_vol": traded_vol,  # 实际成交的 volume
                "dbTime": dbtime,
            }

            res = replace_collection.replace_one(query, order_msg, True)
            self.logger.info(f"[rtn_order] (res){res} (order_msg){order_msg}")
            
        atx_order_collection = self.order_info_db[acc]['atx_order']
        atx_order_msg = {
            "instr_ids": self.oid_to_instr_ids[oid],
        }
        update_atx_order_msg = {"$set": atx_order_msg}
        query = {"oid": oid}
        res = atx_order_collection.update_one(query, update_atx_order_msg)
        self.logger.info(
            f"[update_order] update_atx_order_info (res){res} (msg){update_atx_order_msg}")


    @MongoClientTradeGateway.error_handler
    def monitor_algo_order_insert(self):
        while not self.is_stopped:
            print("[monitor_algo_order_insert]")
            for acc in self.accounts_run:
                target_accountname = self.target_account_names[acc]
                buy_query = {"accountName": target_accountname}
                buy_targets = self.order_info_db[acc]["target"].find(buy_query)
                if buy_targets.count() == 0:
                    self.logger.warning(
                        f"[monitor_buy_order] no_buy_target (acc){acc}")
                    continue
                for target in buy_targets:
                    if target['_id'] not in self.order_dbids:
                        self.order_dbids.append(target['_id'])
                        self.req_buy_order_insert(target)
                    else:
                        self.logger.warning(
                            f"[monitor_algo_order_insert] _id_existed (_id){target['_id']}")
            for acc in self.accounts_run:
                target_accountname = self.target_account_names[acc]
                sell_query = {"accountName": target_accountname}
                sell_targets = self.order_info_db[acc]["sell_target"].find(
                    sell_query)
                if sell_targets.count() == 0:
                    self.logger.warning(
                        f"[monitor_sell_order] no_sell_target (acc){acc}")
                    continue
                for sell_target in sell_targets:
                    if sell_target['_id'] not in self.sell_order_dbids:
                        self.sell_order_dbids.append(sell_target['_id'])
                        self.req_sell_order_insert(sell_target)
                    else:
                        self.logger.warning(
                            f"[monitor_algo_order_insert] _id_existed (_id){sell_target['_id']}")
            time.sleep(self.scan_interval)

    @MongoClientTradeGateway.error_handler
    def monitor_cancel_order_insert(self):
        while not self.is_stopped:
            for acc in self.accounts_run:
                print("[monitor_cancel_order_insert]")
                target_accountname = self.target_account_names[acc]
                query = {"accountName": target_accountname}
                with self.cancel_orderlock:
                    cancel_targets = self.order_info_db[acc]["cancel_target"].find(
                        query)
                    if cancel_targets.count() == 0:
                        self.logger.warning(
                            "[monitor_cancel_order] no_cancel_info")
                        continue
                    for cancel_target in cancel_targets:
                        if cancel_target['_id'] not in self.cancel_order_ids:
                            self.cancel_order_ids.append(cancel_target['_id'])
                            self.req_cancel_order(cancel_target, acc)
            time.sleep(self.scan_interval)

    @MongoClientTradeGateway.error_handler
    def req_cancel_order(self, cancel_target, acc):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        temp_filename = f"{self.insert_order_msg_dir}_temp\\cancel_001.{formatted_time}.csv"

        header = ['local_cancel_no', 'group_flag',
                  'local_no', 'projectid', 'diy1', 'diy2']

        with open(temp_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            oid = str(cancel_target['oid'])
            account_id = self.account_id[acc]
            mudan_id = ""
            if oid not in self.oid_to_ref:
                self.logger.error(
                    "[req_cancel_order] can't_find (oid){oid}")
                return
            mudan_id = self.oid_to_ref[oid]
            group_flag = 0
            cancel_id = str(self.gen_order_id())
            row = [cancel_id, group_flag, oid, account_id, '', '']
            writer.writerow(row)

        final_filename = f"{self.insert_order_msg_dir}\\cancel_001.{formatted_time}.csv"
        shutil.move(temp_filename, final_filename)

        origin_req = self.oid_to_req[oid]
        target_account_name = origin_req['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        target_collection = self.order_info_db[acc]['cancel_target']
        delete_query = {
            'accountName': target_account_name,
            'oid': oid
        }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(
            f"[on_req_cancel_order] delete (target){cancel_target}")

    @MongoClientTradeGateway.error_handler
    def monitor_trade_update(self):
        while not self.is_stopped:
            print("[monitor_trade_update]")
            trade_filename = self.recv_msg_dir + '\\' +  FILES.TRADES + '.' + get_today_date() + '.csv'
            data_list = []

            df = pd.read_csv(trade_filename, dtype={'local_report_no':str})

            header = ['filename', 'local_group_no', 'local_group_name', 'local_report_no', 'instr_no', 'instrstk_no', 'match_no', 'projectid', 'stkcode', 'hedgeflag', 'bsflag', 'matchtime',
                      'matchtype', 'matchprice', 'matchqty', 'matchamt', 'direct_operid', 'order_operid', 'remark', 'matchsno', 'orderextno']

            data_list = []
            current_len = df.shape[0]

            if(current_len > self.trade_count):
                for _, row in df.iloc[self.trade_count:].iterrows():
                    row_dict = {}
                    for col in header:
                        row_dict[col] = row[col]
                    data_list.append(row_dict)

                for record in data_list:
                    if int(record['matchtype']) in [0]:
                        self.on_trade_msg(record)
                    else:
                        self.logger.info(
                            f"[monitor_trade_update] trade_not_finished_or_rejected_or_canceled msg{record}")
                self.trade_count = current_len

            time.sleep(self.trade_scan_interval)

    @MongoClientTradeGateway.error_handler
    def on_trade_msg(self, record):
        if record['matchqty'] == 0:
            self.logger.warning(
                f"[on_trade_msg] nothing_traded (record){record}")
            return

        oid = str(record['local_report_no'])
        if  len(oid) == 0:
            self.logger.warning(f"[on_trade_msg] not use file to  trade record:{record}")
            return

        mudan_id = str(record['instrstk_no'])

        acc = ""
        sid = ""
        order_dict = {}
        if not oid in self.oid_to_acc:  # shut_down or other problem
            trade_acc = record['projectid']
            acc = self.account_id_to_acc[trade_acc]
            order_info_collection = self.order_info_db[acc]['atx_order']
            query = {'oid': oid}
            order_info_target = order_info_collection.find_one(query)

            if not order_info_target is None:
                order_dict = order_info_target['order_msg']
                sid = order_info_target['sid']
                self.oid_to_local_ids[oid] = order_info_target['local_ids']
                self.oid_to_traded[oid] = 0
                self.oid_to_traded_money[oid] = 0
                self.oid_to_sid[oid] = sid
                self.oid_to_req[oid] = order_dict
                self.oid_to_ref[oid] = mudan_id
            else:
                self.logger.error(f"[on_trade_msg] can't_find_oid (oid){oid}")
                return
        else:
            acc = self.oid_to_acc[oid]
            order_dict = self.oid_to_req[oid]
            sid = self.oid_to_sid[oid]
        _id = str(int(record['match_no']))
        if _id in self.oid_to_local_ids[oid]:
            #self.logger.warning(f"[on_trade_msg] duplicate_trade_msg (record){record}")
            return
        else:
            self.oid_to_local_ids[oid].append(_id)
            
        int_stock_code = int(record['stkcode'])
        ticker = f'{int_stock_code:06d}'
        exchange = decode_exchange_id(ticker)
        traded_vol = int(record['matchqty'])
        traded_price = float(record['matchprice'])
        trade_amt = record['matchamt']

        target_type = encode_gf_side(record['bsflag'])
        if target_type == 1 or target_type == 3:
            self.oid_to_traded_money[oid] += trade_amt
            self.oid_to_traded[oid] += traded_vol
        elif target_type == 2:
            self.oid_to_traded_money[oid] -= trade_amt
            self.oid_to_traded[oid] -= traded_vol
        entrust_vol = record['matchqty']
        #entrust_price = record.Price
        entrust_price = float(record['matchprice'])
        dbTime = get_time_from_str(str(record['matchtime']))

        commission = 0
        order_type = order_dict['order_type']
        target_account_name = order_dict['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        log_accountname = order_dict['accountName'].split('@')[1]
        tg_name = order_dict['accountName'].split('@')[0]

        side = encode_gf_side(record['bsflag'])

        db_msg = {
            "trade_ref": _id,
            "oid": int(oid),
            "tg_name": tg_name,
            "exchange": exchange,
            "ticker": ticker,
            "traded_vol": traded_vol,
            "traded_price": traded_price,
            "order_type": order_type,
            "side": side,  # 对应 tlclient.trader.constant 包 Side
            "entrust_vol": entrust_vol,
            "entrust_price": entrust_price,  # 没有下单价格，只有成交价
            "dbTime": dbTime,
            "sid": sid,  # 对应订单中的 sid
            "commission": commission,  # 没有
            "trade_time": dbTime,  # 具体交易时间

            "accountName":  log_accountname,  # 对应 account_info.account_name
        }
        trade_collection = self.tradelog_db[acc]['trade']
        replace_trade_query = {"trade_ref": _id, "oid": oid,
                               "sid": sid, "accountName": log_accountname}
        db_res = trade_collection.replace_one(
            replace_trade_query, db_msg, True)
        self.logger.info(
            f"[rtn_trade] (db_res){db_res} (db_msg){db_msg} (traded_vol){traded_vol} (traded_price){traded_price}")
        self.update_position(traded_vol, order_dict, sid,
                             oid, side, trade_amt, exchange)

        atx_order_collection = self.order_info_db[acc]['atx_order']
        atx_order_msg = {
            "local_ids": self.oid_to_local_ids[oid],
        }
        update_atx_order_msg = {"$set": atx_order_msg}
        query = {"oid": oid}
        res = atx_order_collection.update_one(query, update_atx_order_msg)
        self.logger.info(
            f"[on_trade_msg] update_atx_order_info (res){res} (msg){update_atx_order_msg}")

    @MongoClientTradeGateway.error_handler
    def update_position(self, traded_vol, order, sid, oid, side, trade_amt, exchange):
        target_accountname = order['accountName']
        acc = self.target_account_names_to_acc[target_accountname]

        query = {'sid': sid, 'accountName': target_accountname}
        position_collection = self.order_info_db[acc]['EquityPosition']
        position = position_collection.find_one(query)
        if position is None and traded_vol > 0:
            if oid not in self.oid_to_req:
                self.logger.warning(
                    f"[update_position] can't_find_req (sid){sid} (oid){oid}")
                return
            if oid not in self.oid_to_traded:
                self.logger.error(f"[update_position]no trade_vol (sid){sid}")
                return
            td_trade_vol = self.oid_to_traded[oid]

            amt = self.oid_to_traded_money[oid]

            ticker = order['ticker']
            yd_pos = 0
            mkt_value = amt
            cost = 0
            if not td_trade_vol == 0:
                cost = amt / td_trade_vol
            update_time = datetime.now(timezone.utc)

            position_msg = {
                "ticker": ticker,
                "cost": cost,  # 成本价
                "td_pos_long": td_trade_vol,  # 今仓
                "yd_pos_long": yd_pos,  # 昨仓（可卖），挂止盈单后为0
                "td_pos_short": 0,
                "yd_pos_short": 0,
                "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                "actual_yd_pos_long": yd_pos,  # 实际的昨仓
                "enter_date": update_time,
                "holding_days": 0,  # 持仓时间（交易日累计）
                "mkt_value": mkt_value,  # 市值
                "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
                "sid": sid,  # 我们策略生成的id，需要根据实际下单情况维护各sid的持仓。
                # 格式: {account_info.tg_name}@{account_info.account_name}
                "accountName": target_accountname,
                "update_date": update_time,
            }
            query2 = {'sid': sid,
                      'accountName': target_accountname}
            res = position_collection.replace_one(query2, position_msg, True)
            self.logger.info(
                f"[update_position] (res){res} (msg){position_msg}")
        else:
            if oid not in self.oid_to_req:
                self.logger.warning(
                    f"[update_position] can't_find_req (sid){sid}")
                return
            if oid not in self.oid_to_traded:
                self.logger.error(f"[update_position]no trade_vol (sid){sid}")
                return
            actual_yd_pos = position['actual_yd_pos_long']
            amt = trade_amt
            yd_pos = position['yd_pos_long']
            if side == 1 or side == 3:
                td_trade_vol = position['actual_td_pos_long'] + traded_vol
                mkt_value = position['mkt_value'] + amt
            elif side == 2:
                td_trade_vol = position['actual_td_pos_long'] - traded_vol
                mkt_value = position['mkt_value'] - amt
                yd_pos = yd_pos - traded_vol

            ticker = order['ticker']

            cost = 0
            total_vol = td_trade_vol + yd_pos
            if not total_vol == 0:
                cost = mkt_value / total_vol
            update_time = datetime.now(timezone.utc)
            accountName = order['accountName']
            enter_time = position['enter_date']
            holding_days = position['holding_days']
            position_msg = {
                "ticker": ticker,
                "cost": cost,  # 成本价
                "td_pos_long": td_trade_vol,  # 今仓
                "yd_pos_long": yd_pos,  # 昨仓（可卖），挂止盈单后为0
                "td_pos_short": 0,
                "yd_pos_short": 0,
                "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                "actual_yd_pos_long": actual_yd_pos,  # 实际的昨仓
                "enter_date": enter_time,
                "holding_days": holding_days,  # 持仓时间（交易日累计）
                "mkt_value": mkt_value,  # 市值
                "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
                "sid": sid,  # 我们策略生成的id，需要根据实际下单情况维护各sid的持仓。
                # 格式: {account_info.tg_name}@{account_info.account_name}
                "accountName": accountName,
                "update_date": update_time,
            }
            query = {'sid': sid,
                     'accountName': accountName}
            res = position_collection.replace_one(query, position_msg, True)
            self.logger.info(
                f"[update_position] (res){res} (msg){position_msg}")

    def start(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        _msg = f"[login] gf_server_start (time){datetime.now()}"
        self.send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        self.monitor()

    def close(self):
        return super().close()

    def join(self):
        while self.is_stopped == False:
            time.sleep(0.01)
            if self.is_stopped:
                self.logger.info(
                    "[close] main thread is stopped,active_orders message will lose")
                self.close()


if __name__ == "__main__":

    sys.stdout.reconfigure(encoding='utf-8')
    description = "gf_server,get target from mongodb and serve gf"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-e', '--end_time', dest='end_time', default='15:30')
    _config_filename = "C:/Users/Administrator/Desktop/gf_batandconfig/gf_server_config.json"
    parser.add_argument('-p', '--config_filepath',
                        dest='config_filepath', default=_config_filename)

    args = parser.parse_args()
    print(f"(args){args}")

    td = GfServer(args.config_filepath, args.end_time, GATEWAY_NAME)
    td.start()

    td.join()
