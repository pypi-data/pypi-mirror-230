# 创建策略
# coding=utf-8
import math
import sys
import time

import qmt.env
from qmt import utils, env
from qmt.callback import QmtTraderCallback
from qmt.context import QmtContext
from xtquant import xtconstant
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader


def main() -> any:
    print('初始化...')
    # path为mini qmt客户端安装目录下userdata_mini路径
    # path = r'c:/runtime/gjzqqmt/userdata_mini'
    qmt_userdata_path = qmt.env.get_qmt_exec_path() + '/userdata_mini'
    print(qmt_userdata_path)
    # session_id为会话编号，策略使用方对于不同的Python策略需要使用不同的会话编号
    now = time.time()
    session_id = int(now)
    trader = XtQuantTrader(qmt_userdata_path, session_id)
    # 获取证券账号对象
    qc = QmtContext()
    acc = qc.account()
    # 创建交易回调类对象，并声明接收回调
    callback = QmtTraderCallback()
    trader.register_callback(callback)

    # 启动交易线程
    trader.start()
    print('初始化...OK')
    # 建立交易连接，返回0表示连接成功
    print('连接miniQMT...')
    connect_result = trader.connect()
    if connect_result == 0:
        print('连接miniQMT...OK')
    else:
        print('连接miniQMT...Failed')
        trader.stop()

        return False
    # 判断交易日
    v = utils.today_is_tradeday()
    if not v:
        print('非交易日, 退出')
        return False
    # stock_code = '600577.sh'.upper()
    # subscribe_result = xtdata.subscribe_quote(stock_code, period='tick', callback=None)
    # print("subscribe_quote: %d\n" % (subscribe_result))
    #
    # v = xtdata.get_full_tick([stock_code])
    # print(v[stock_code]['askPrice'][-1])
    # exit(0)

    # # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
    # subscribe_result = trader.subscribe(acc)
    # print(subscribe_result)
    # # stock_code = '600000.SH'
    # stock_code = '600577.SZ'
    # # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
    # print("order using the fix price:")
    # fix_result_order_id = trader.order_stock(acc, stock_code, xtconstant.STOCK_BUY, 1000, xtconstant.LATEST_PRICE, -1,
    #                                          't89k_buy', '测试买入')
    # print(fix_result_order_id)
    # trader.order_stock(acc,)
    #
    # # 使用订单编号撤单
    # print("cancel order:")
    # cancel_order_result = xt_trader.cancel_order_stock(acc, fix_result_order_id)
    # print(cancel_order_result)
    #
    # # 使用异步下单接口，接口返回下单请求序号seq，seq可以和on_order_stock_async_response 的委托反馈response对应起来
    # print("order using async api:")
    # async_seq = xt_trader.order_stock(acc, stock_code, xtconstant.STOCK_BUY,
    #                                   200, xtconstant.FIX_PRICE, 10.5, 'strategy_name', 'remark')
    # print(async_seq)
    #
    # 查询证券资产
    print("查询证券资产:")
    asset = trader.query_stock_asset(acc)
    if asset:
        print("asset:")
        print("total: {0}, cash {1}".format(asset.total_asset, asset.cash))
    # 检测订单是否就绪
    if qc.buy_is_ready():
        df = qc.load_order()
        stock_total = len(df)
        print('订单数量:', stock_total)
        # subscribe_result = xtdata.subscribe_quote(stock_code, period='tick', callback=None)
        # print("subscribe_quote: %d\n" % (subscribe_result))
        # v = xtdata.get_full_tick([stock_code])
        # print(v)
        # 订阅tick数据
        code_list = []
        for idx, stock in df.iterrows():
            code = stock['code']
            security_code = qc.fix_security_code(code)
            code_list.append(security_code)
        subscribe_result = xtdata.subscribe_whole_quote(code_list, callback=None)
        print("subscribe_quote: %d\n" % (subscribe_result))
        ticks = xtdata.get_full_tick(code_list)
        # 遍历订单, 数据文件只需要code和open两个字段
        for idx, stock in df.iterrows():
            # print(stock)
            # 数据日期
            stock_date = stock['date']
            # 证券代码
            code = stock['code']
            print('code:', code)
            # 检查买入成功标识
            if qc.check_buy_order_done_status(code):
                print("stock %s: buy done" % (code))
                continue
            # 计算单一可用资金
            single_funds_available = utils.fix_single_available(asset, stock_total)
            # 扣除可能发生的交易费率
            single_funds_available = single_funds_available * (1 - utils.buy_trade_rete)
            # 09:25 到 09:30 返回的时间信息是 [ 09:30 ], 或者相差小于 10s 检查通过
            security_code = qc.fix_security_code(code)
            # 计算溢价
            # buy_price = stock['open'] * (1 + utils.buy_premium_rate)
            buy_price = ticks[security_code]['askPrice'][-1]
            # 开盘价+0.05
            # buy_price = stock['open'] + 0.05
            buy_price = utils.price_round(buy_price)
            print(security_code, 'buy:', buy_price)
            buy_num = math.floor(single_funds_available / (buy_price * 100)) * 100
            if buy_num == 0:
                print('单一股价过高, 分仓购买力不足1手')
                stock_total = stock_total - 1
                continue
            # 买入操作
            order_id = trader.order_stock(acc, security_code, xtconstant.STOCK_BUY, buy_num, xtconstant.FIX_PRICE,
                                          buy_price,
                                          't89k_buy', '测试买入')
            print('order_id:', order_id)
            # log(ctx, f'{ctx.account_id}: 证券代码={security_code}, 委托价格={buy_price}, 委托数量={buy_num}')
            # 设置执行下单完成状态
            qc.push_buy_order_done_status(code)
        # 设置已完成标志文件
        qc.order_buy_completed()
    # # 根据订单编号查询委托
    # print("query order:")
    # order = xt_trader.query_stock_order(acc, fix_result_order_id)
    # if order:
    #     print("order:")
    #     print("order {0}".format(order.order_id))
    #
    # 查询当日所有的委托
    print("query orders:")
    orders = trader.query_stock_orders(acc)
    print("orders:", len(orders))
    if len(orders) != 0:
        for order in orders:
            order_time = time.strftime(utils.kFormatTimestamp, time.localtime(order.order_time))
            print("order: id=%s, time=%s, code=%s, status=%s" % (
            order.order_id, order_time, order.stock_code, order.order_status))
            # 休市期间撤销未成交的委托订单
            if qc.order_can_cancel() and order.order_status == xtconstant.ORDER_REPORTED:
                cancel_order_result = trader.cancel_order_stock(acc, order.order_id)
                print(cancel_order_result)

    #
    # # 查询当日所有的成交
    # print("query trade:")
    # trades = xt_trader.query_stock_trades(acc)
    # print("trades:", len(trades))
    #
    # if len(trades) != 0:
    #     print("last trade:")
    #     print("{0} {1} {2}".format(trades[-1].stock_code,
    #                                trades[-1].traded_volume, trades[-1].traded_price))
    #

    # 查询当日所有的持仓
    print("查询当日所有的持仓:")
    positions = trader.query_stock_positions(acc)
    print("持仓:", len(positions))
    if qc.sell_is_ready():
        for position in positions:
            # print(repr(dt))
            security_code = position.stock_code
            op_flag = 'Unknown'
            if position.can_use_volume >= 100:
                try:
                    # 卖出操作
                    order_id = trader.order_stock(acc, position.stock_code, xtconstant.STOCK_SELL,
                                                  position.can_use_volume,
                                                  xtconstant.LATEST_PRICE,
                                                  -1, 't89k_sell', '测试卖出')
                except Exception as e:
                    order_id = -1
                print('order_id:', order_id)
                op_flag = 'ASKING'
            else:
                op_flag = 'WAITING'
            # 控制台输出持仓记录
            print("%s stock %s holding: %d can_ask: %d, open_price:%f, market_value: %f" % (op_flag, security_code,
                                                                                            position.volume,
                                                                                            position.can_use_volume,
                                                                                            position.open_price,
                                                                                            position.market_value))
    # # 阻塞线程，接收交易推送
    # xt_trader.run_forever()
    trader.stop()
    print('交易完成')
    return True


if __name__ == '__main__':
    sys.exit(main())
