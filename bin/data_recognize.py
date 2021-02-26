#!/usr/bin/python
# -*-coding:utf-8 -*-
#  ------------------------------------------------------
# @File    : data_recognize.py
# @Date    : 2020-12-21 09:24
# @Author  : Jupiter
# @Function Description: 
#  ------------------------------------------------------


import io
import re


def domain_chk(it, ofdic, kvdic, label):
    tmp_label = label
    if tmp_label == "ReYY":
        label = "ReY"
    ol = 'offset_' + label
    if it is not None:
        for i in it:   #
            if sum([len(i) for i in kvdic.values()]) < 10:
                if tmp_label == "ReYY":
                    value = i.group(2)
                    offset = i.span(2)
                # elif label == "UppW":
                #     value = i.group(2)
                else:
                    value = i.group()
                    offset = i.span()
                if value[-1] == " ":
                    value = value[:-1]  # 说明这个词汇末尾多标了空格或者英文句号，需要修复
                    offset = (offset[0], offset[1]-1)
                if value[0] == " ":
                    value = value[1:]  # 说明这个词汇开头多标了空格或者英文句号，需要修复
                    offset = (offset[0]+1, offset[1])
                # print(value)
                judge = 0  # 0就是字典中没有，1就是有
                temp = {}
                for dk, dl in ofdic.items():
                    if dl is None:
                        break
                    for d in dl:
                        # 后来词区间大于之前区间的情况，直接删除包含在这个区间中的值
                        # 但还是有可能会出现[2,5][5,8]->[4,9]的情况——直接不标，因为judge=1
                        if offset[0] < d[0] and offset[1] > d[1]:
                            temp.setdefault(dk, []).append(d)
                        elif offset[0] <= d[0] and offset[1] > d[1]:
                            temp.setdefault(dk, []).append(d)
                        elif offset[0] < d[0] and offset[1] >= d[1]:
                            temp.setdefault(dk, []).append(d)
                        elif offset[0] in range(d[0], d[1]):
                            judge = 1
                            break
                        elif (offset[1] - 1) in range(d[0], d[1]):
                            judge = 1
                            break
                    if judge == 1:
                        break  # 这一步判断操作从总体上来说是降低时间复杂度的
                if judge == 0:
                    for tk, tv in temp.items():
                        for v in tv:
                            seq = ofdic[tk].index(v)
                            tkl = tk.lstrip('offset_')
                            del ofdic[tk][seq]
                            del kvdic[tkl][seq]
                    ofdic.setdefault(ol, []).append(offset)
                    kvdic.setdefault(label, []).append(value)
        return ofdic, kvdic


class Mark(object):
    def __init__(self):
        months = "January|Jan\.|Jan|February|Feb\.|Feb|March|Mar\.|Mar|April|Apr\.|Apr|May|May\.|June|June\.|July|July\.|August|Aug\.|Aug|September|Sept\.|Sep\.|Sep|Sept|October|Oct\.|Oct|November|Nov\.|Nov|December|Dec\.|Dec"
        # 日月年-日月年
        self.patterndate1 = re.compile(
            r"(from|between)*[ ]*\d{1,2}(th|st|nd|rd)?[, ]*(%s)[, ]*(20\d{2}|1\d{3})[ ]*(\~|\-|to|and)[ ]*\d{1,2}(th|st|nd|rd)?[, ]*(%s)[, ]*(20\d{2}|1\d{3})" % (
                months, months), re.I)  # 月日年-月日年

        # 月日年-月日年
        self.patterndate2 = re.compile(
            r"(from|between)*[ ]*(%s.)[, ]*\d{1,2}(th|st|nd|rd)?[, ]*(20\d{2}|1\d{3})[ ]*(\~|\-|to|and)[ ]*(%s)[, ]*\d{1,2}(th|st|nd|rd)?[, ]*(20\d{2}|1\d{3})" % (
                months, months), re.I)

        # 月日-日,年
        self.patterndate14 = re.compile(
            r"(\A| |[\.\,\?])(%s)[, ]*\d{1,2}(th|st|nd|rd)?[ ]*(\~|\-|to|and)[ ]*\d{1,2}(th|st|nd|rd)?[, ]*(20\d{2}|1\d{3})" % months,
            re.I)

        # 日-日,月年
        self.patterndate15 = re.compile(
            r"\d{1,2}[ ]*(\~|\-|to|and)[ ]*\d{1,2}[, ]*(%s)[, ]*(20\d{2}|1\d{3})" % months, re.I)

        # 2008-08-08 - 2009.09.09
        self.patterndate3 = re.compile(
            r"(from|between)*[ ]*(20\d{2}|1\d{3})(\-|\.)(1[0-2]|[0]?[1-9])(\-|\.)([1-3]\d|[0]?[1-9])[ ]*(\~|\-|to|and)[ ]*(20\d{2}|1\d{3})(\-|\.)(1[0-2]|[0]?[1-9])(\-|\.)([1-3]\d|[0]?[1-9])",
            re.I)
        # \d{1,2}--> (\d|[0-1]\d)
        # 月年-月年
        self.patterndate4 = re.compile(
            r"(from|between)*[ ]*(%s)[, ]*(20\d{2}|1\d{3})[ ]*(\~|\-|to|and)[ ]*(%s)[, ]*(20\d{2}|1\d{3})" % (
                months, months), re.I)

        # 2008-08 ~ 2009-09
        self.patterndate5 = re.compile(
            r"(from|between)*[ ]*(20\d{2}|1\d{3})(\-|\.)(1[0-2]|[0]?[1-9])(th|st|nd|rd)?[ ]*(\~|\-|to|and)[ ]*(20\d{2}|1\d{3})(\-|\.)(1[0-2]|[0]?[1-9])(th|st|nd|rd)?",
            re.I)

        # 年-年
        self.patterndate6 = re.compile(
            r"(from|between)*[ ]*(20\d{2}|1\d{2,3})[ ]*(\~|\-|to|and|\/|\\)[ ]*((20\d{2})|(1\d{3})|9\d)",
            re.I)  # 扩展了1992/93

        # 2008-00-09
        self.patterndate7 = re.compile(r"(20\d{2}|1\d{3})(\-|\.)(1[0-2]|[0]?[1-9])(\-|\.)([1-3]\d|[0]?[1-9])",
                                       re.I)

        # 月日年
        self.patterndate8 = re.compile(r"(\A| |[\.\,\?])(%s)[, ]*\d{1,2}(th|st|nd|rd)?[, ]*(20\d{2}|1\d{3})" % months, re.I)

        # 日月年
        self.patterndate9 = re.compile(r"\d{1,2}(th|st|nd|rd)?[, ]*(%s)[, ]*(20\d{2}|1\d{3})" % months, re.I)

        # 2009-09
        self.patterndate10 = re.compile(r"(20\d{2}|1\d{3})(\-|\.|\\)(1[0-2]|[0]?[1-9] )(th|st|nd|rd)?", re.I)

        # 月年
        self.patterndate11 = re.compile(r"(\A| |[\.\,\?])(%s)[, ]*(20\d{2}|1\d{3})" % months, re.I)

        # 1990s年代   group(2)
        self.patterndate12 = re.compile(
            r"(During| for|For| in|In|By| by| since|Since| to| until|Until| the|year| least| late| on|On| after|After| of| and|To)[ ]?((20\d{2}|1\d{3})s)")

        # 年  group(2)
        self.patterndate13 = re.compile(
            r"(the|During| for|For| in|In|By| by| since|Since| to| until|Until| the|year| least| late| on|On| after|After| of| and|To)[ ]?((20\d{2}|1\d{3}))")

        # 月日    月日-月日 月日-日
        #  self.patterndate16 = re.compile(r"((\d{1,2}[ ]*)?(January|Jan\.|February|Feb\.|March|Mar\.|April|Apr\.|May|May\.|June|June\.|July|July\.|August|Aug\.|September|Sept\.|Sep\.|October|Oct\.|November|Nov\.|December|Dec\.)[ ]?\d{1,2}([ ]?(\-|\~|to)[ ]?\d{1,2})?[ ]*(January|Jan\.|February|Feb\.|March|Mar\.|April|Apr\.|May|May\.|June|June\.|July|July\.|August|Aug\.|September|Sept\.|Sep\.|October|Oct\.|November|Nov\.|December|Dec\.))|(\d{1,2}([ ]?(\-|\~)[ ]?\d{1,2})?[ ]?(January|Jan\.|February|Feb\.|March|Mar\.|April|Apr\.|May|May|June|June\.|July|July\.|August|Aug\.|September|Sept\.|Sep\.|October|Oct\.|November|Nov\.|December|Dec\.))|(\d{1,2}([ ]?(\-|\~)[ ]?\d{1,2})?[ ]?(January|Jan\.|February|Feb\.|March|Mar\.|April|Apr\.|May|May|June|June\.|July|July\.|August|Aug\.|September|Sept\.|Sep\.|October|Oct\.|November|Nov\.|December|Dec\.)[ ]*\d{1,2}([ ]?(\-|\~)[ ]?\d{1,2})?)", re.I)
        # v1的为  r"(\d|st|rd|th|nd)*( |,|，| ,|, )(January|February|March|April|May|June|July|August|September|October|November|December| Sept.)( |,|，| ,|, )*[\d|st|rd|th|nd| ]*( |,|，| ,|, )*[\d]*"
        # v3在v1的基础上改进:  1.避免了只标一个月份单词的形式

        #  日月-日月
        self.patterndate16 = re.compile(
            r"(\A| |[\.\,\?])([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]*(%s)[ ]?(\-|\~|to)[ ]?([0-3]\d|[1-9])(th|st|nd|rd)?[ ]*(%s)(\Z|[ ,.;。，])" % (months, months),
            re.I)
        #  月日-月日
        self.patterndate17 = re.compile(
            r"(\A| |[\.\,\?])(%s)[ ]*([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]*(\-|\~|to)[ ]*(%s)[ ]*([1-9]|[0-3]\d)(th|st|nd|rd)?(\Z|[ ,.;。，])" % (months, months),
            re.I)
        #  日-日 月
        self.patterndate18 = re.compile(
            r"(\A| |[\.\,\?])([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]?(\-|\~|to)[ ]?([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]*(%s)(\Z|[ ,.;。，])" % months, re.I)
        #  月 日-日
        self.patterndate19 = re.compile(
            r"(\A| |[\.\,\?])(%s)[ ]*([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]?(\-|\~|to)[ ]?([1-9]|[0-3]\d)(th|st|nd|rd)?(\Z|[ ,.;。，])" % months, re.I)
        #  月日
        self.patterndate20 = re.compile(r"(\A| |[\.\,\?])((%s)[ ]*([1-9]|[0-3]\d)(th|st|nd|rd)?)(\Z|[ ,.;。，])" % months, re.I)
        #  日月
        self.patterndate21 = re.compile(r"(([1-9]|[0-3]\d)(th|st|nd|rd)?[ ]*(%s))(\Z|[ ,.;。，])" % months, re.I)

        self.patterntime = re.compile(
            r"[ \,\.\?]*(\d{1,2}[ ]?((a\.m\.)|(p\.m\.)|(am(\Z|[ ,.;。，]))|(\Z|pm([ ,.;。，]))|(AM(\Z|[ ,.;。，]))|(PM(\Z|[ ,.;。，]))))|(\d{1,2}(\:|\：|\: | \:|\.)\d{2}[ ]?((a\.m\.)|(p\.m\.)|(am(\Z|[ ,.;。，]))|(pm(\Z|[ ,.;。，]))|(AM(\Z|[ ,.;。，]))|(PM(\Z|[ ,.;。，]))))|(\d{2}(\:|\：|\: | \:)\d{2}(\:|\：|\: | \:)\d{2})|(\d{1,2}(\:|\：|\: | \:)\d{2})",
            re.I)
        # v2 为 r"(\d{1,2}[ ]?((a.m.)|(p.m.)|(am)|(pm)))|(\d{1,2}[:：]\d{2}[ ]?((a.m.)|(p.m.)|(am)|(pm)))|(\d{2}[:：]\d{2}[:：]\d{2})"
        # V1 版本 为patterntime = r"((\d{1,2}|:|：| |-|\.)+|\d{1,2}[:： ](a.m.|p.m.|am|pm))|(\d{2}(:|：|\.|-| )\d{2}(:|：| |-|\.)\d{2})"
        # v2在v1基础上改进： 1.am和pm标记问题（was a master-->was<Time_1_ a ma>ster）解决了
        # v3在v2 基础上添加了3：00这类标记，并把：与:做了可能性调整
        self.patterndatezh1 = re.compile(r"\d+年\d+月\d+日")
        self.patterndatezh2 = re.compile(r"\d+年\d+月")
        self.patterndatezh3 = re.compile(r"\d+月\d+日")


    def mark(self, type_name, text):
        if type_name == "Time":
            pattern = self.patterntime
        elif type_name == "Date1":
            pattern = self.patterndate1
        elif type_name == "Date2":
            pattern = self.patterndate2
        elif type_name == "Date14":
            pattern = self.patterndate14
        elif type_name == "Date15":
            pattern = self.patterndate15
        elif type_name == "Date3":
            pattern = self.patterndate3
        elif type_name == "Date4":
            pattern = self.patterndate4
        elif type_name == "Date5":
            pattern = self.patterndate5
        elif type_name == "Date6":
            pattern = self.patterndate6
        elif type_name == "Date7":
            pattern = self.patterndate7
        elif type_name == "Date8":
            pattern = self.patterndate8
        elif type_name == "Date9":
            pattern = self.patterndate9
        elif type_name == "Date10":
            pattern = self.patterndate10
        elif type_name == "Date11":
            pattern = self.patterndate11
        elif type_name == "Date12":
            pattern = self.patterndate12
        elif type_name == "Date13":
            pattern = self.patterndate13
        elif type_name == "Date16":
            pattern = self.patterndate16
        elif type_name == "Date17":
            pattern = self.patterndate17
        elif type_name == "Date18":
            pattern = self.patterndate18
        elif type_name == "Date19":
            pattern = self.patterndate19
        elif type_name == "Date20":
            pattern = self.patterndate20
        elif type_name == "Date21":
            pattern = self.patterndate21
        elif type_name == "Datezh1":
            pattern = self.patterndatezh1
        elif type_name == "Datezh2":
            pattern = self.patterndatezh2
        elif type_name == "Datezh3":
            pattern = self.patterndatezh3
        try:
            for result in re.finditer(pattern, text):
                yield result
        except:
            print("not found {}!".format(type_name))


def total_mark(marker, line):
    ofdic = {}
    kvdic = {}
    mtime = marker.mark("Time", line)
    mdate1 = marker.mark("Date1", line)
    mdate2 = marker.mark("Date2", line)
    mdate14 = marker.mark("Date14", line)
    mdate15 = marker.mark("Date15", line)
    mdate3 = marker.mark("Date3", line)
    mdate4 = marker.mark("Date4", line)
    mdate5 = marker.mark("Date5", line)
    mdate6 = marker.mark("Date6", line)
    mdate7 = marker.mark("Date7", line)
    mdate8 = marker.mark("Date8", line)
    mdate9 = marker.mark("Date9", line)
    mdate10 = marker.mark("Date10", line)
    mdate11 = marker.mark("Date11", line)
    mdate12 = marker.mark("Date12", line)
    mdate13 = marker.mark("Date13", line)
    mdate16 = marker.mark("Date16", line)
    mdate17 = marker.mark("Date17", line)
    mdate18 = marker.mark("Date18", line)
    mdate19 = marker.mark("Date19", line)
    mdate20 = marker.mark("Date20", line)
    mdate21 = marker.mark("Date21", line)
    mdatezh1 = marker.mark("Datezh1", line)
    mdatezh2 = marker.mark("Datezh2", line)
    mdatezh3 = marker.mark("Datezh3", line)
    domain_chk(mtime, ofdic, kvdic, label="Time") # 对应原来的time
    domain_chk(mdate1, ofdic, kvdic, label="ReY")
    domain_chk(mdate2, ofdic, kvdic, label="ReY")
    domain_chk(mdate14, ofdic, kvdic, label="ReY")
    domain_chk(mdate15, ofdic, kvdic, label="ReY")
    domain_chk(mdate3, ofdic, kvdic, label="ReY")
    domain_chk(mdate4, ofdic, kvdic, label="ReY")
    domain_chk(mdate5, ofdic, kvdic, label="ReY")
    domain_chk(mdate6, ofdic, kvdic, label="ReY")
    domain_chk(mdate7, ofdic, kvdic, label="ReY")
    domain_chk(mdate8, ofdic, kvdic, label="ReY")
    domain_chk(mdate9, ofdic, kvdic, label="ReY")
    domain_chk(mdate10, ofdic, kvdic, label="ReY")
    domain_chk(mdate11, ofdic, kvdic, label="ReY")
    domain_chk(mdate12, ofdic, kvdic, label="ReYY")  # 这俩是因为正则表达式取值group(2)所以为了后面domincheck加以区分
    domain_chk(mdate13, ofdic, kvdic, label="ReYY")  # 把标记多加了一个Y，最终domaincheck完了以后数据写入词典前标签将被改回ReY，所以仍然是ReY类
    domain_chk(mdate16, ofdic, kvdic, label="ReY")   # 对应原来的month1
    domain_chk(mdate17, ofdic, kvdic, label="ReY")
    domain_chk(mdate18, ofdic, kvdic, label="ReY")
    domain_chk(mdate19, ofdic, kvdic, label="ReY")
    domain_chk(mdate20, ofdic, kvdic, label="ReY")
    domain_chk(mdate21, ofdic, kvdic, label="ReY")   # 对应原来的month6
    domain_chk(mdatezh1, ofdic, kvdic, label="ReY")
    domain_chk(mdatezh2, ofdic, kvdic, label="ReY")
    domain_chk(mdatezh3, ofdic, kvdic, label="ReY")
    # return ofdic, kvdic
    mid_dic = dict(ofdic, **kvdic)
    final_dic = mid_dic.copy()
    for k, v in mid_dic.items():
        if not v:
            final_dic.pop(k)
    return final_dic


def year_translate(text):
    # print(text)
    mon_dic = {'January': 1, 'February': 2, 'March': 3,
               'April': 4, 'May': 5, 'June': 6,
               'July': 7, 'August': 8, 'September': 9,
               'October': 10, 'November': 11, 'December': 12,

               'January.': 1, 'February.': 2, 'March.': 3,
               'April.': 4, 'May.': 5, 'June.': 6,
               'July.': 7, 'August.': 8, 'September.': 9,
               'October.': 10, 'November.': 11, 'December.': 12,

               'Jan.': 1, 'Feb.': 2, 'Mar.': 3,
               'Apr.': 4, 'May.': 5, 'June.': 6,
               'July.': 7,'Aug.': 8, 'Sept.': 9,
               'Oct.': 10, 'Nov.': 11, 'Dec.': 12, 'Sep.': 9,

               'january': 1, 'february': 2, 'march': 3,
               'april': 4, 'may': 5, 'june': 6,
               'july': 7, 'august': 8, 'september': 9,
               'october': 10, 'november': 11, 'december': 12,

               'january.': 1, 'february.': 2, 'march.': 3,
               'april.': 4, 'may.': 5, 'june.': 6,
               'july.': 7, 'august.': 8, 'september.': 9,
               'october.': 10, 'november.': 11, 'december.': 12,

               'January': 1, 'February': 2, 'March': 3,
               'April': 4, 'May': 5, 'June': 6,
               'July': 7, 'August': 8, 'September': 9,
               'October': 10, 'November': 11, 'December': 12,

               'Jan': 1, 'Feb': 2, 'Mar': 3,
               'Apr': 4, 'Aug': 8, 'Sept': 9,
               'Oct': 10, 'Nov': 11, 'Dec': 12, 'Sep': 9,

               'jan': 1, 'feb': 2, 'mar': 3,
               'apr': 4, 'aug': 8, 'sept': 9,
               'oct': 10, 'nov': 11, 'dec': 12, 'sep': 9,

               'jan.': 1, 'feb.': 2, 'mar.': 3,
               'apr.': 4, 'aug.': 8, 'sept.': 9,
               'oct.': 10, 'nov.': 11, 'dec.': 12, 'sep.': 9
               }
    ap_dic = {"am": "上午", "a.m.": "上午", "a.m": "上午", "pm": "下午", "p.m.": "下午", "p.m": "下午", "AM": "上午", "PM":"下午"}
    rule20 = re.compile("[ \,\.\?]*(?P<shi>\d{1,2})[ ]*(?P<ap>((a.m.)|(p.m.)|(am[\.]?)|(pm[\.]?)|(AM[\.]?)|(PM[\.]?)))", re.I)  # 3:00am/3am/12:11:13/12:00
    rule21 = re.compile("[ \,\.\?]*(?P<shi>\d{1,2})(:|：|\.|-|\.| )*(?P<fen>\d{2})[ ]*(?P<ap>((a.m.)|(p.m.)|(am[\.]?)|(pm[\.]?)|(AM[\.]?)|(PM[\.]?)))", re.I)
    rule22 = re.compile("[ \,\.\?]*(?P<shi>\d{2})(:|：|\.|-)(?P<fen>\d{2})(:|：|\.|-)(?P<miao>\d{2})", re.I)
    rule23 = re.compile("[ \,\.\?]*(?P<shi>\d{2})(:|：|: | :)(?P<fen>\d{2})", re.I)
    rule1 = re.compile("(from|between)*[ ,]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<year>\d{4})[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon1>[A-Za-z\.]+)[, ]*(?P<year1>\d{4})[ ]?", re.I)  # 日月年-日月年
    rule2 = re.compile("(from|between)*[ ,]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(?P<year>\d{4})[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<mon1>[A-Za-z\.]+)[, ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*(?P<year1>\d{4})[ ]?", re.I)  # 月日年-月日年
    rule24 = re.compile("(from|between)*[ ,]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*(?P<year>\d{4})[ ,]*", re.I)  # 月日-日,年
    rule25 = re.compile("(from|between)*[ ,]*(?P<day>\d{1,2})(th|st|nd|rd)?[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<year>\d{4})[ ,]*", re.I)  # 日-日,月年
    rule3 = re.compile("(from|between)*[ ,]*(?P<year>\d{4})-(?P<mon>\d{1,2})-(?P<day>\d{2})[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<year1>\d{4})-(?P<mon1>\d{1,2})-(?P<day1>\d{2})[ ,]*", re.I)  # 2008-08-08 - 2009-09-09
    rule4 = re.compile("(from|between)*[ ,]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<year>\d{4})[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<mon1>[A-Za-z\.]+)[, ]*(?P<year1>\d{4})[ ]?", re.I)  # 月年-月年
    rule5 = re.compile("(from|between)*[ ,]*(?P<year>\d{4})-(?P<mon>\d{1,2})(th|st|nd|rd)?[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<year1>\d{4})-(?P<mon1>\d{1,2})(th|st|nd|rd)?[ ,]*", re.I)   # 2008-08 ~ 2009-09
    rule6 = re.compile("(from|between)*[ ,]*(?P<year>\d{4})[ ]*((\~)|(\-)|(to)|(and))[ ]*(?P<year1>((\d{4})|([2-9]\d)))", re.I)  # 年-年
    rule7 = re.compile("[ \,\.\?]*(?P<year>\d{4})-(?P<mon>\d{1,2})-(?P<day>\d{2})", re.I)  # 2008-00-09
    rule8 = re.compile("[ \,\.\?]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(?P<year>\d{4})", re.I)  # 月日年 英文/简写
    rule9 = re.compile("[ \,\.\?]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<year>\d{4})", re.I)  # 日月年
    rule10 = re.compile("[ \,\.\?]*(?P<year>\d{4})-(?P<mon>\d{1,2})(th|st|nd|rd)?", re.I)  # 2009-09
    rule11 = re.compile("[ \,\.\?]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<year>\d{4})", re.I)  # 月年
    rule12 = re.compile("[ \,\.\?]*(?P<years>\d{4})s", re.I)  # 1990s年代
    rule13 = re.compile("[ \,\.\?]*(?P<year>\d{4})", re.I)  # 年
    rule14 = re.compile("[ \,\.\?]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(\~|\-|to)[ ]*(?P<mon1>[A-Za-z\.]+)[ ,]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*",re.I)  # 月日-月日
    rule15 = re.compile("[ \,\.\?]*(?P<day>\d{1,2})[ ]*(?P<mon>[A-Za-z\.]+)[ ]*(\~|\-|to)[ ]*(?P<day1>\d{1,2})[, ]*(?P<mon1>[A-Za-z\.]+)",re.I)  # 日月-日月
    rule16 = re.compile("[ \,\.\?]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(\~|\-|to)[ ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*", re.I)  # 月日-日
    rule17 = re.compile("[ \,\.\?]*(?P<day>\d{1,2})(th|st|nd|rd)?[ ]*(\~|\-|to)[ ]*(?P<day1>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon>[A-Za-z\.]+)", re.I)  # 日-日月
    rule18 = re.compile("[ \,\.\?]*(?P<mon>[A-Za-z\.]+)[, ]*(?P<day>\d{1,2})(th|st|nd|rd)?", re.I)  # 月日
    rule19 = re.compile("[ \,\.\?]*(?P<day>\d{1,2})(th|st|nd|rd)?[, ]*(?P<mon>[A-Za-z\.]+)", re.I)  # 日月
    result20 = re.match(rule20, text)
    result21 = re.match(rule21, text)
    result22 = re.match(rule22, text)
    result23 = re.match(rule23, text)
    result1 = re.match(rule1, text)
    result2 = re.match(rule2, text)
    result24 = re.match(rule24, text)
    result25 = re.match(rule25, text)
    result3 = re.match(rule3, text)
    result4 = re.match(rule4, text)
    result5 = re.match(rule5, text)
    result6 = re.match(rule6, text)
    result7 = re.match(rule7, text)
    result8 = re.match(rule8, text)
    result9 = re.match(rule9, text)
    result10 = re.match(rule10, text)
    result11 = re.match(rule11, text)
    result12 = re.match(rule12, text)
    result13 = re.match(rule13, text)
    result14 = re.match(rule14, text)
    result15 = re.match(rule15, text)
    result16 = re.match(rule16, text)
    result17 = re.match(rule17, text)
    result18 = re.match(rule18, text)
    result19 = re.match(rule19, text)
    if result20:
        # print(18)
        shi = result20.group('shi')
        ap = result20.group('ap')
        trans_rep = ap_dic[ap.lower()] + shi + "时"
    elif result21:
        # print(19)
        shi = result21.group('shi')
        fen = result21.group('fen')
        ap = result21.group('ap')
        trans_rep = ap_dic[ap.lower()] + shi + "时" + fen + "分"
    elif result22:
        # print(20)
        shi = result22.group('shi')
        fen = result22.group('fen')
        miao = result22.group('miao')
        trans_rep = shi + "时" + fen + "分" + miao + "秒"
    elif result23:
        # print(21)
        shi = result23.group('shi')
        fen = result23.group('fen')
        trans_rep = shi + "时" + fen + "分"
    elif result1:
        # print(1)
        day = result1.group('day')
        mon = result1.group('mon')
        year = result1.group('year')
        day1 = result1.group('day1')
        mon1 = result1.group('mon1')
        year1 = result1.group('year1')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日"+"到"+year1 + "年" + str(mon_dic[mon.lower()]) + "月" + day1 + "日"
    elif result2:
        # print(2)
        mon = result2.group('mon')
        day = result2.group('day')
        year = result2.group('year')
        mon1 = result2.group('mon1')
        day1 = result2.group('day1')
        year1 = result2.group('year1')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + year1 + "年" + str(mon_dic[mon1.lower()]) + "月" + day1 + "日"
    elif result24:
        mon = result24.group('mon')
        day = result24.group('day')
        day1 = result24.group('day1')
        year = result24.group('year')
        # print(22)
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + day1 + "日"
    elif result25:
        # print(23)
        day = result25.group('day')
        day1 = result25.group('day1')
        mon = result25.group('mon')
        year = result25.group('year')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + day1 + "日"
    elif result3:
        year = result3.group('year')
        mon = result3.group('mon')
        day = result3.group('day')
        year1 = result3.group('year1')
        mon1 = result3.group('mon1')
        day1 = result3.group('day1')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + year1 + "年" + str(mon_dic[mon1.lower()]) + "月" + day1 + "日"
    elif result4:
        mon = result4.group('mon')
        year = result4.group('year')
        mon1 = result4.group('mon1')
        year1 = result4.group('year1')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + "到" + year1 + "年" + str(mon_dic[mon1.lower()]) + "月"
    elif result5:
        year = result5.group('year')
        mon = result5.group('mon')
        year1 = result5.group('year1')
        mon1 = result5.group('mon1')
        trans_rep = year + "年" + str(mon) + "月" + "到" + year1 + "年" + str(mon) + "月"
    elif result6:
        year = result6.group('year')
        year1 = result6.group('year1')
        trans_rep = year + "年" + "到" + year1 + "年"
    elif result7:
        year = result7.group('year')
        mon = result7.group('mon')
        day = result7.group('day')
        trans_rep = year + "年" + str(mon) + "月" + day + "日"
    elif result8:
        mon = result8.group('mon')
        day = result8.group('day')
        year = result8.group('year')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日"
    elif result9:
        day = result9.group('day')
        mon = result9.group('mon')
        year = result9.group('year')
        trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月" + day + "日"
    elif result10:
        year = result10.group('year')
        mon = result10.group('mon')
        trans_rep = year + "年" + str(mon) + "月"
    elif result11:
        mon = result11.group('mon')
        year = result11.group('year')
        try:
            trans_rep = year + "年" + str(mon_dic[mon.lower()]) + "月"
        except Exception as e:
            trans_rep = ""
    elif result12:
        years = result12.group('years')
        trans_rep = years + "年代"
    elif result13:
        year = result13.group('year')
        trans_rep = year + "年"
    elif result14:
        mon = result14.group('mon')
        mon1 = result14.group('mon1')
        day = result14.group('day')
        day1 = result14.group('day1')
        trans_rep = str(mon_dic[mon]) + "月" + day + "日" + "到" + str(mon_dic[mon1.lower()]) + "月" + day1 + "日"
    elif result15:
        mon = result15.group('mon')
        mon1 = result15.group('mon1')
        day = result15.group('day')
        day1 = result15.group('day1')
        trans_rep = str(mon_dic[mon]) + "月" + day + "日" + "到" + str(mon_dic[mon1.lower()]) + "月" + day1 + "日"
    elif result16:
        mon = result16.group('mon')
        day = result16.group('day')
        day1 = result16.group('day1')
        trans_rep = str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + day1 + "日"
    elif result17:
        day = result17.group('day')
        day1 = result17.group('day1')
        mon = result17.group('mon')
        trans_rep = str(mon_dic[mon.lower()]) + "月" + day + "日" + "到" + day1 + "日"
    elif result18:
        mon = result18.group('mon')
        day = result18.group('day')
        trans_rep = str(mon_dic[mon.lower()]) + "月" + day + "日"
    elif result19:
        day = result19.group('day')
        mon = result19.group('mon')
        trans_rep = str(mon_dic[mon.lower()]) + "月" + day + "日"
    else:
        trans_rep = text
    return trans_rep


def time_translate(text):
    ap_dic = {"am": "上午", "a.m.": "上午", "a.m": "上午", "pm": "下午", "p.m.": "下午", "p.m": "下午", "AM": "上午", "PM": "下午"}
    rule18 = "[ \,\.\?]*(?P<shi>\d{1,2})[ ]*(?P<ap>((a.m.)|(p.m.)|(am)|(pm)|(AM)|(PM)))"  # 3:00am/3am/12:11:13/12:00
    rule19 = "[ \,\.\?]*(?P<shi>\d{1,2})(:|：|\.|-| )*(?P<fen>\d{2})[ ]*(?P<ap>((a.m.)|(p.m.)|(am)|(pm)|(AM)|(PM)))"
    rule20 = "[ \,\.\?]*(?P<shi>\d{2})(:|：|\.|-| )*(?P<fen>\d{2})(:|：|\.|-| )*(?P<miao>\d{2})"
    rule21 = "[ \,\.\?]*(?P<shi>\d{2})(:|：|: | :)(?P<fen>\d{2})"
    result18 = re.match(rule18, text)
    result19 = re.match(rule19, text)
    result20 = re.match(rule20, text)
    result21 = re.match(rule21, text)
    if result18:
        # print(18)
        shi = result18.group('shi')
        ap = result18.group('ap')
        trans_rep = ap_dic[ap] + shi + "时"
    elif result19:
        # print(19)
        shi = result19.group('shi')
        fen = result19.group('fen')
        ap = result19.group('ap')
        trans_rep = ap_dic[ap] + shi + "时" + fen + "分"
    elif result20:
        # print(20)
        shi = result20.group('shi')
        fen = result20.group('fen')
        miao = result20.group('miao')
        trans_rep = shi + "时" + fen + "分" + miao + "秒"
    elif result21:
        # print(21)
        shi = result20.group('shi')
        fen = result20.group('fen')
        trans_rep = shi + "时" + fen + "分"
    return trans_rep


def match_zh(line):
    """
    判断是否包含数字
    """
    # 匹配字符串中是否含有汉字
    pattern = re.compile(u'[\u4e00-\u9fa5]')
    # findall是返回所有符合匹配的项，返回形式为数组
    match = pattern.findall(line)
    # if后加变量的意思是判断变量是否为空，不为空则为true，反之为false
    if match:
        # print('contain zh')
        return True
    else:
        # print('no zh')
        return False


def get_time_and_format(line):
    """
    正则匹配时间并且格式化为中文标准时间字符串
    :param line:
    :return:
    """
    marker_en = Mark()
    dates = total_mark(marker_en, line)
    res_list = []
    if "ReY" in dates:
        for date in dates["ReY"]:
            if match_zh(date):
                res = date
            else:
                res = year_translate(date)
            if res and "年代" in res:
                res = res.replace("年代", "年")
            res_list.append(res)
    print(res_list)
    return res_list


def format_times_str(tims):
    """
    格式化时间字符串
    :param tims:
    :return:
    """
    res_list = []
    for date in tims:
        if match_zh(date):
            res = date
        else:
            res = year_translate(date)
        if res and "年代" in res:
            res = res.replace("年代", "年")
        res_list.append(res)
    print(res_list)
    
    
def format_one_time_str(tim):
    """
    格式化时间字符串
    :param tim:
    :return:
    """
    if match_zh(tim):
        res = tim
    else:
        res = year_translate(tim)
    if res and "年代" in res:
        res = res.replace("年代", "年")
    return res


if __name__ == "__main__":
    line = "from June. 1 1919 到1920年1月期间"
    line1 = "from June 15"
    line2 = "from 15日"
    line3 = "2月"
    line4 = "2月15日"
    get_time_and_format(line)
    get_time_and_format(line1)
    get_time_and_format(line2)
    get_time_and_format(line3)
    get_time_and_format(line4)
    
    # format_time_str([line3])
    # format_time_str([line4])
