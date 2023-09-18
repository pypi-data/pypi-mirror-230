from pathlib import Path
from nonebot.matcher import Matcher
from nonebot.plugin import on_startswith
from uvdiviner.divine import quick_check, make_trigram
from uvdiviner.evolution import trigram, diagram
from uvdiviner.main import get_useful_data
from uvdiviner import colorize
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.adapters import Bot as Bot
from .utils import (
    version as __version__, init, reset_limit, minus_limit, get_limit,
    has_group, has_user, set_user, get_groups, get_users, format_msg,
    get_user_card
)

import nonebot
import logging
import sys
import asyncio

__plugin_meta__ = PluginMetadata(
    name="周易蓍草占卜",
    description="基于古蓍草占卜的算法, 简单的使用`.divine`指令.",
    usage="安装即可使用.",
    type="application",
    homepage="https://gitee.com/unvisitor/nonebot-plugin-uvdiviner",
)

try:
    driver = nonebot.get_driver()
    scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler
    initialized = True
except:
    initialized = False

DEBUG = False
colorize.disable()
current_dir = Path(__file__).resolve().parent
try:
    from multilogging import multilogger
    logger = multilogger(name="UV Diviner", payload="Nonebot2")
except:
    from nonebot import logger

divinecommand = on_startswith((".divine", ".div"), priority=2, block=True)
dqccommand = on_startswith((".dqc", ".qca", ".aqc"), priority=2, block=True)

async def helphandler(matcher: Matcher):
    await matcher.send(
        "Unvisitor Diviner 使用帮助:\n"
        ".divine/.div 标准占卜\n"
        ".dqc/.qca 快速吉凶检定\n"
    )

async def divine(matcher: Matcher):
    global DEBUG

    await matcher.send(
        "天何言哉，叩之即应；神之灵矣，感而遂通。\n"
        "今有某人，有事关心，罔知休咎，罔释厥疑，\n"
        "惟神惟灵，望垂昭报，若可若否，尚明告之。"
        )
    logger.warning(
        "天何言哉，叩之即应；神之灵矣，感而遂通。\n"
        "今有某人，有事关心，罔知休咎，罔释厥疑，\n"
        "惟神惟灵，望垂昭报，若可若否，尚明告之。"
    )
    trigrams = [make_trigram(), make_trigram(), make_trigram(),] if not DEBUG else [trigram(8), trigram(8), trigram(6),]

    for _ in range(1, 28):
        if not DEBUG:
            await asyncio.sleep(1)

    await matcher.send("某宫三象，吉凶未判，再求外象三爻，以成一卦，以决忧疑。")
    logger.warning("某宫三象，吉凶未判，再求外象三爻，以成一卦，以决忧疑。")

    for _ in range(28, 56):
        if not DEBUG:
            await asyncio.sleep(1)

    trigrams += [make_trigram(), make_trigram(), make_trigram()] if not DEBUG else [trigram(9), trigram(8), trigram(8)]

    if not DEBUG: await asyncio.sleep(1)

    dia = diagram(trigrams)

    static, variable, result = get_useful_data(dia)

    if not static["卦名"] == variable["卦名"]:
        await matcher.send(
                "占卜结果: " + static["卦名"][:-1] + "之" + variable["卦名"][:-1]
                )
        logger.info("占卜结果: " + static["卦名"][:-1] + "之" + variable["卦名"][:-1])
    else:
        await matcher.send("占卜结果: " + static["卦名"])
        logger.info("占卜结果: " + static["卦名"])

    if not DEBUG: await asyncio.sleep(1)

    await matcher.send("本卦: " + static["卦名"] + "\n" + "卦辞: " + static["卦辞"])
    logger.info("本卦: " + static["卦名"] + "\n" + "卦辞: " + static["卦辞"])

    if not DEBUG: await asyncio.sleep(1)

    if dia.variated != 0:
        await matcher.send("变卦:" + variable["卦名"] + "\n   卦辞: " + variable["卦辞"] + "\n" + "变爻数:" + str(dia.variated))
        logger.info("变卦:" + variable["卦名"] + "\n   卦辞: " + variable["卦辞"] + "\n" + "变爻数:" + str(dia.variated))

    if not DEBUG: await asyncio.sleep(2)

    await matcher.send(result)
    logger.info(result)

if initialized:
    @driver.on_startup
    async def _():
        global DEBUG
        logger.info("欧若可卜师初始化中...")
        if DEBUG:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.remove()
            logger.add(
                sys.stdout,
                level = "DEBUG"
            )
            logger.info("DEBUG 模式已启动.")
        init()
        logger.success("欧若可卜师初始化完毕.")

    @divinecommand.handle()
    async def divinehandler(matcher: Matcher, event: Event):
        args = format_msg(event.get_message(), begin=(".divine", ".div"))
        if len(args) != 0:
            await helphandler(matcher=matcher)
            return

        logger.warning("用户尝试发起一场占卜.")
        if not has_user(event):
            set_user(event)

        if get_limit(event) <= 0 and not DEBUG:
            await matcher.send("今日占卜次数已达安全上限, 欧若可拒绝继续进行占卜.")
            logger.warning("今日占卜次数已达安全上限, 欧若可拒绝继续进行占卜.")
            return

        minus_limit(event)
        await matcher.send(f"[{get_user_card(event)}]尝试发起一场蓍草象数占卜.\n请注意, 本次占卜可能消耗一些时间, 请耐心等待.")
        await asyncio.sleep(1)
        await divine(matcher)
        logger.success("占卜完成.")

    @dqccommand.handle()
    async def dqchandler(matcher: Matcher, event: Event):
        logger.warning("用户尝试发起一场快速占卜检定.")
        if not has_user(event):
            set_user(event)

        if get_limit(event) <= 0 and not DEBUG:
            await matcher.send("今日占卜次数已达安全上限, 欧若可拒绝继续进行占卜.")
            logger.warning("今日占卜次数已达安全上限, 欧若可拒绝继续进行占卜.")
            return

        minus_limit(event)
        qc = quick_check()
        result = str(qc)
        await matcher.send(f"卦象: {qc.name}\n占卜快速检定结果: {result}")
        logger.info(f"卦象: {qc.name}\n占卜快速检定结果: {result}")
        logger.success("快速检定完成.")

    @scheduler.scheduled_job("cron", hour='1', minute='00', id="reset")
    async def schedulerhandler():
        reset_limit()

        bot = nonebot.get_bot()

        groups = get_groups()
        if groups:
            for group in groups:
                await bot.send_group_msg(group_id=group, message="新的一天开始了, 占卜限制已重置.")
        else:
            for user in get_users():
                await bot.send_private_msg(user_id=user, messge="新的一天开始了, 占卜限制已重置.")

    try:
        scheduler.start()
    except:
        pass