#-*- coding: utf-8 -*-
import os
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd
import config
import pandas
import re
import math
import modules.base as base

from modules.venders.itooza import Itooza
from modules.venders.fnguide_invest import FnguideInvest
from modules.venders.fnguide_ratio import FnguideRatio
from modules.venders.fnguide_finance import FnguideFinance
from modules.venders.sejong import Sejong
from modules.venders.post_cleaning import PostCleaning

from modules.venders import itooza, fnguide_invest
from modules.valuations.valuation import Valuation
from modules.valuations.grade import Grade
from modules.valuations.john_templeton import JohnTempleton
from modules.valuations.dcf import DCF
from modules.valuations.bps import BPS
from modules.valuations.per import PER
from modules.valuations.eps_bps import EPS_BPS
from modules.valuations.rim import RIM
from modules.valuations.yamaguchi_yohei import YamaguchiYohei
from modules.valuations.cantabile import Cantabile
from modules.valuations.peg import PEG
from modules.valuations.psr import PSR
from modules.valuations.graham import Graham
from modules.valuations.john_neff import JohnNeff
from modules.valuations.piotroski import Piotroski
from modules.valuations.de import DE
from modules.valuations.rt import RT
from modules.valuations.brown_stone import BrownStone


def load(code):
  # fnguide_main_data = load_url(FNGUIDE_MAIN_URL, code)
  # # fnguide_invest_data = load_url(FNGUIDE_INVEST_URL, code)

  vender = Itooza(code)
  vender = FnguideInvest(code, vender)
  vender = FnguideRatio(code, vender)
  vender = FnguideFinance(code, vender)

  vender = Sejong(code, vender)
  vender = PostCleaning(code, vender)

  data = vender.get_data()
  json = vender.get_json()

  valuation = Valuation(data, json)
  valuation = Grade(valuation)
  valuation = JohnTempleton(valuation)
  valuation = DCF(valuation)
  valuation = BPS(valuation)
  valuation = PER(valuation)
  valuation = EPS_BPS(valuation)
  valuation = RIM(valuation)
  valuation = YamaguchiYohei(valuation)
  valuation = Cantabile(valuation)
  valuation = PEG(valuation)
  valuation = PSR(valuation)
  valuation = Graham(valuation)
  valuation = JohnNeff(valuation)
  valuation = Piotroski(valuation)
  valuation = DE(valuation)
  valuation = RT(valuation)
  valuation = BrownStone(valuation)

  # print(valuation.get_data())
  # print(valuation.get_json())

  # STOCK_COUNT: 주식수(천주)
  # PRICE: 주가
  # SALES: 매출액 (억)
  # BUSINESS_PROFITS: 영업이익 (억)
  # EPS_IFRS: EPS (연결)
  # EPS: EPS
  # EPS_RATE_OF_INCREASE: EPS증가율
  # ROE: ROE
  # ROA: ROA
  # ROIC: ROIC
  # PER: PER
  # BPS: BPS
  # PBR: PBR
  # DIVIDEND_PRICE: 배당금
  # DIVIDEND_RATE: 시가배당률 (%)
  # ROS: 순이익률
  # OPM: 영업이익률
  # FCFF: FCFF (억)
  # DIVIDEND_PAYOUT_RATIO: 배당성향(연결)
  # NET_INCOME_RATIO: 순이익률(매출/이익)
  # SALES_FCFF: 매출액/현금흐름
  # EV_FCFF: 현금투자수익률
  # DEBT_RATIO: 부채비율
  # CURRENT_RATIO: 유동비율
  # INTEREST_REWARD_POWER: 이자보상배율
  # EV/EBITDA
  # BPS_TIMES_0.5: PBR  0.5
  # BPS_TIMES_2: PBR  2
  # BPS_TIMES_3: PBR 3
  # EV1: EV시가총액(비지배주주지분포함) + 순차입부채
  # EPS_SIMPLE:
  # INVENTORY_ASSETS: 재고자산
  # FLOATING_FINANCE_ASSETS: 유동금융자산
  # SALES_AND_FLOATING_BOND: 매출채권및기타유동채권
  # ETC_FLOATING_ASSETS: 기타유동자산
  # CACHE_ASSETS: 현금및현금성자산
  # RESERVED_SALE_ASSETS: 매각예정비유동자산및처분자산집단
  # FLOATING_DEBT: 유동부채
  # LONG_FINANCE_ASSETS: 장기금융자산
  # IFRS_COMPANY_FINANCE_ASSETS: 관계기업등지분관련투자자산
  # LONG_SALES_AND_NON_FLOATING_BOND: 장기매출채권및기타비유동채권
  # DEFERRED_CORPORATE_TAXES_ASSETS: 이연법인세자산
  # ETC_NON_FLOATING_ASSETS: 기타비유동자산
  # NON_FLOATING_BOND: 비유동부채
  # NET_PROFIT_DURING_A_YEAR: 당기순이익(연율화)
  # TOTAL_CASH_FLOW: 총현금흐름
  # OPERATING_PROFIT_AFTER_TAX: 세후영업이익
  # GROSS_PROFIT_MARGIN: 매출총이익율
  # SALES_GROWTH_RATE: 매출액증가율
  # TOTAL_ASSETS_AVERAGE: 자산총계(평균)

  # PER_5:
  # PBR_5:
  # ROE_5:
  # EPS_5_GROWTH:
  # BPS_5_GROWTH:

  # Valuations
  # VALUATION_GRADE: 등급
  # VALUATION_JOHN_TEMPLETON: 존 템플턴 가치
  # VALUATION_DCF: 현금 흐름법 가치
  # VALUATION_BPS:
  # VALUATION_PER:
  # VALUATION_5_EPS_BPS: 5 EPS/BPS
  # VALUATION_RIM: 올슨 초과이익모형

  return (data, json)


def is_valid(json, columns):
  for column in columns:
    if not (column in json):
      return False

    if json[column] is None:
      return False

    if isinstance(json[column], str):
      return False

  return True


def score(data, json):
  price = data['PRICE'].dropna()[:1][0] if 'PRICE' in data.columns else 0
  scores = []
  criticals = []
  grade = json['VALUATION_GRADE'] if 'VALUATION_GRADE' in json else None

  if is_valid(json, ['VALUATION_PEG']):
    criticals.append(json['VALUATION_PEG'] >= 1)  # 1 이상이면 안됨

  if is_valid(json, ['VALUATION_PSR']):
    criticals.append(json['VALUATION_PSR'] >= 1.5)  # 1.5 이상이면 안됨

  if is_valid(json, ['VALUATION_PIOTROSKI']):
    criticals.append(json['VALUATION_PIOTROSKI'] <= 2)  # 1.5 이상이면 안됨

  if is_valid(json, ['VALUATION_DE']):
    criticals.append(json['VALUATION_DE'] >= 100)  # 무조건 100 이하

  if is_valid(json, ['PER', 'PER_5']):
    scores.append(json['PER'] < json['PER_5'])

  if is_valid(json, ['PBR', 'PBR_5']):
    scores.append(json['PBR'] < json['PBR_5'])

  if is_valid(json, ['ROE', 'ROE_5']):
    scores.append(json['ROE'] < json['ROE_5'])

  if is_valid(json, ['DPS']) and price > 0:
    scores.append((json['DPS'] / price) > 0)  # 배당률

  if is_valid(json, ['DPS', 'EPS']):
    scores.append((json['DPS'] / json['EPS']) > 0)  # 배당성향

  if is_valid(json, ['VALUATION_PEG']):
    scores.append(json['VALUATION_PEG'] < 0.5)

  if is_valid(json, ['VALUATION_PSR']):
    scores.append(json['VALUATION_PSR'] < 0.75)

  if is_valid(json, ['VALUATION_GRAHAM']):
    scores.append(json['VALUATION_GRAHAM'] > 0.2)

  if is_valid(json, ['VALUATION_JOHN_NEFF']):
    scores.append(json['VALUATION_JOHN_NEFF'] > 4)

  if is_valid(json, ['VALUATION_PIOTROSKI']):
    scores.append(json['VALUATION_PIOTROSKI'] > 2)

  if is_valid(json, ['VALUATION_DE']):
    scores.append(json['VALUATION_DE'] <= 100)

  if is_valid(json, ['VALUATION_BROWN_STONE']):
    scores.append(json['VALUATION_BROWN_STONE'] >= 3)

  if is_valid(json, ['VALUATION_DCF']) and price > 0:
    scores.append(json['VALUATION_DCF'] > price)

  if is_valid(json, ['VALUATION_5_EPS_BPS']) and price > 0:
    scores.append(json['VALUATION_5_EPS_BPS'] < price)

  if is_valid(json, ['VALUATION_RIM']) and price > 0:
    scores.append(json['VALUATION_RIM'] < price)

  if is_valid(json, ['VALUATION_YAMAGUCHI_YOHEI']) and price > 0:
    scores.append(json['VALUATION_YAMAGUCHI_YOHEI'] < price)

  if is_valid(json, ['VALUATION_CANTABILE']) and price > 0:
    scores.append(json['VALUATION_CANTABILE'] < price)

  if is_valid(json, ['VALUATION_JOHN_TEMPLETON']) and price > 0:
    scores.append(json['VALUATION_JOHN_TEMPLETON'] < price)

  if is_valid(json, ['VALUATION_PER']) and price > 0:
    scores.append(json['VALUATION_PER'] < price)

  if is_valid(json, ['VALUATION_BPS']) and price > 0:
    scores.append(json['VALUATION_BPS'] < price)

  score = (0 if sum(criticals) > 0 else 1) * sum(scores)
  return {
      'price': str(price),
      'grade': grade,
      'critical': {
          'score': str(sum(criticals)),
          'total': str(len(criticals))
      },
      'score': {
          'score': str(sum(scores)),
          'total': str(len(scores))
      }
  }
